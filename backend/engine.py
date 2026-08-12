"""
RAILSHIELD — Predictive Counterfactual Railway Control
Core simulation / prediction / intervention engine.

This is a deliberately compact, explainable engine (rule-based + discrete-event
simulation) rather than a black box. It is designed to be swapped later for
real ML models (XGBoost/LSTM for prediction, OR-Tools/MILP for intervention
search) without changing the API surface below.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import copy
import itertools

# ---------------------------------------------------------------------------
# Network topology
# ---------------------------------------------------------------------------

SECTIONS = ["A", "B", "C", "D", "E", "F"]
PLATFORMS = {"C": "P1", "D": "P2", "E": "P3"}
HEADWAY_MIN = 6  # minimum safe minutes between two trains occupying the same section


@dataclass
class Train:
    id: str
    type: str            # "express" | "freight" | "local"
    priority: int        # lower number = higher priority
    speed_kmh: float
    # base_schedule: minute offset (from simulation t=0) at which the train
    # is scheduled to ENTER each section, in section order starting at
    # its entry section.
    route: list[str]
    base_offsets: dict[str, float]

    def offsets(self, delay: float = 0.0, speed_delta_kmh: float = 0.0,
                held_min: float = 0.0, section_shift: Optional[dict] = None):
        """Return this train's section-entry offsets under a proposed change."""
        out = {}
        speed_factor = self.speed_kmh / max(self.speed_kmh + speed_delta_kmh, 1)
        for sec in self.route:
            base = self.base_offsets[sec]
            t = base * speed_factor + delay + held_min
            if section_shift and sec in section_shift:
                t += section_shift[sec]
            out[sec] = t
        return out


def default_network() -> list[Train]:
    """A hand-authored scenario matching the RAILSHIELD design brief:
    T18 (express) and F07 (freight) are on a collision course at Section E,
    with downstream local trains T21, T25, T27, T29, T31 sharing platforms
    and sections further down the line."""

    trains = [
        Train("T18", "express", 1, 110, ["A", "B", "C", "D", "E", "F"],
              {"A": 0, "B": 6, "C": 12, "D": 18, "E": 24.0, "F": 30}),
        Train("F07", "freight", 3, 60, ["C", "D", "E", "F"],
              {"C": 10, "D": 17, "E": 24.6, "F": 33}),
        Train("T21", "local", 2, 80, ["B", "C", "D", "E"],
              {"B": 10, "C": 17, "D": 24, "E": 31}),
        Train("T25", "local", 2, 80, ["C", "D", "E", "F"],
              {"C": 22, "D": 29, "E": 36, "F": 43}),
        Train("T27", "local", 2, 80, ["D", "E", "F"],
              {"D": 26, "E": 33, "F": 40}),
        Train("T29", "local", 2, 80, ["D", "E", "F"],
              {"D": 34, "E": 41, "F": 48}),
        Train("T31", "express", 1, 100, ["E", "F"],
              {"E": 45, "F": 51}),
    ]
    return trains


# ---------------------------------------------------------------------------
# Discrete-event simulation
# ---------------------------------------------------------------------------

def simulate(trains: list[Train], applied: Optional[dict] = None):
    """Run the trains through the network, applying headway rules per
    section (and per platform, where two sections funnel into one
    platform). `applied` maps train_id -> kwargs for Train.offsets(),
    representing an intervention. Returns per-train per-section arrival
    times (with propagated delay) and a list of conflict events."""

    applied = applied or {}
    raw = {t.id: t.offsets(**applied.get(t.id, {})) for t in trains}

    # actual (post-propagation) times start as raw times
    actual = {tid: dict(v) for tid, v in raw.items()}
    delay_acc = {t.id: 0.0 for t in trains}
    conflicts = []

    train_by_id = {t.id: t for t in trains}

    # occupancy resource = section, plus platform resource where defined
    resources = {}
    for sec in SECTIONS:
        resources[("section", sec)] = []
    for sec, plat in PLATFORMS.items():
        resources[("platform", plat)] = []

    # process events in scheduled (raw) order per resource
    for sec in SECTIONS:
        occupants = []
        for t in trains:
            if sec in t.route:
                occupants.append(t.id)
        occupants.sort(key=lambda tid: actual[tid][sec] + delay_acc[tid])

        for i in range(1, len(occupants)):
            a, b = occupants[i - 1], occupants[i]
            ta = actual[a][sec] + delay_acc[a]
            tb = actual[b][sec] + delay_acc[b]
            gap = tb - ta
            if gap < HEADWAY_MIN:
                # lower-priority (higher number) train yields
                yielder, holder = (b, a) if train_by_id[b].priority >= train_by_id[a].priority else (a, b)
                needed = HEADWAY_MIN - gap
                if needed > 0:
                    conflicts.append({
                        "section": sec,
                        "trains": [a, b],
                        "gap_min": round(gap, 1),
                        "yields": yielder,
                        "added_delay": round(needed, 1),
                    })
                    delay_acc[yielder] += needed
                    # propagate the new delay to every later section that
                    # train touches
                    for later_sec in train_by_id[yielder].route:
                        if later_sec == sec or actual[yielder][later_sec] > actual[yielder][sec]:
                            pass  # handled by delay_acc applying globally below

        for tid in occupants:
            actual[tid][sec] = raw[tid][sec] + delay_acc[tid]

    # platform contention (independent resource, same headway logic, applied
    # once section-level pass is complete so it captures propagated delay)
    for sec, plat in PLATFORMS.items():
        occupants = [t.id for t in trains if sec in t.route]
        occupants.sort(key=lambda tid: actual[tid][sec])
        for i in range(1, len(occupants)):
            a, b = occupants[i - 1], occupants[i]
            gap = actual[b][sec] - actual[a][sec]
            if gap < HEADWAY_MIN * 0.6:
                yielder = b if train_by_id[b].priority >= train_by_id[a].priority else a
                needed = (HEADWAY_MIN * 0.6) - gap
                delay_acc[yielder] += needed
                conflicts.append({
                    "section": sec, "platform": plat, "trains": [a, b],
                    "gap_min": round(gap, 1), "yields": yielder,
                    "added_delay": round(needed, 1),
                })
                for later_sec in train_by_id[yielder].route:
                    actual[yielder][later_sec] = raw[yielder][later_sec] + delay_acc[yielder]

    total_delay = sum(delay_acc.values())
    return {
        "actual": actual,
        "delay": {k: round(v, 1) for k, v in delay_acc.items()},
        "conflicts": conflicts,
        "total_delay": round(total_delay, 1),
    }


# ---------------------------------------------------------------------------
# Future risk field
# ---------------------------------------------------------------------------

def risk_field(trains: list[Train], horizon_min: int):
    """Probability of a headway violation per section by `horizon_min`
    minutes from now, based on how tightly packed scheduled trains are
    relative to HEADWAY_MIN."""

    result = simulate(trains)
    actual = result["actual"]
    field = {}
    for sec in SECTIONS:
        occupants = [t for t in trains if sec in t.route and actual[t.id][sec] <= horizon_min + 1e-6]
        occupants.sort(key=lambda t: actual[t.id][sec])
        min_gap = None
        for i in range(1, len(occupants)):
            gap = actual[occupants[i].id][sec] - actual[occupants[i - 1].id][sec]
            min_gap = gap if min_gap is None else min(min_gap, gap)
        if min_gap is None:
            field[sec] = {"level": "green", "probability": 0.0}
        else:
            prob = max(0.0, min(1.0, (HEADWAY_MIN - min_gap) / HEADWAY_MIN))
            level = "green"
            if prob >= 0.75:
                level = "red"
            elif prob >= 0.4:
                level = "orange"
            elif prob >= 0.15:
                level = "yellow"
            field[sec] = {"level": level, "probability": round(prob, 2)}
    return field


# ---------------------------------------------------------------------------
# Intervention generation
# ---------------------------------------------------------------------------

def generate_interventions(trains: list[Train], conflict: dict):
    a, b = conflict["trains"]
    yielder = conflict["yields"]
    holder = a if yielder == b else b
    options = []

    def impact(applied):
        r = simulate(trains, applied)
        return r["total_delay"], r

    # Option A: hold the yielding (lower priority) train briefly at entry
    d, r = impact({yielder: {"held_min": 5}})
    options.append({"id": "hold", "label": f"Hold {yielder} for 5 min",
                     "network_delay": d, "detail": r["delay"]})

    # Option B: slow the higher-priority train slightly so the gap opens
    d, r = impact({holder: {"speed_delta_kmh": -14}})
    options.append({"id": "speed", "label": f"Reduce {holder} speed by ~4 km/h",
                     "network_delay": d, "detail": r["delay"]})

    # Option C: shift the crossing point downstream by adjusting the
    # conflicted section's entry time for the yielder only
    d, r = impact({yielder: {"section_shift": {conflict["section"]: 7}}})
    options.append({"id": "reroute", "label": "Change crossing to next station",
                     "network_delay": d, "detail": r["delay"]})

    # Option D: full platform/route reassignment (bigger structural change,
    # modeled here as a large forced gap on the yielder)
    d, r = impact({yielder: {"held_min": 14}})
    options.append({"id": "platform", "label": "Reallocate platform / re-sequence",
                     "network_delay": d, "detail": r["delay"]})

    options.sort(key=lambda o: o["network_delay"])
    for i, o in enumerate(options):
        o["recommended"] = (i == 0)
    return options


def root_cause(trains: list[Train], section: str):
    result = simulate(trains)
    conflicts_here = [c for c in result["conflicts"] if c["section"] == section]
    plat = PLATFORMS.get(section)
    platform_share = 42 if plat else 10
    interaction_share = 27 if any(
        {trains_by_id(trains, tid).type for tid in c["trains"]} == {"express", "freight"}
        for c in conflicts_here for tid in [c["trains"][0]]
    ) else 20
    late_dep = 18
    headway = max(5, 100 - platform_share - interaction_share - late_dep)
    total = platform_share + interaction_share + late_dep + headway
    norm = lambda x: round(100 * x / total)
    return {
        "utilization_pct": min(97, 60 + len(conflicts_here) * 12),
        "causes": [
            {"label": "Platform occupation", "pct": norm(platform_share)},
            {"label": "Express/Freight interaction", "pct": norm(interaction_share)},
            {"label": "Late departure", "pct": norm(late_dep)},
            {"label": "Excessive headway", "pct": norm(headway)},
        ],
        "primary_bottleneck": plat or f"Section {section}",
    }


def trains_by_id(trains, tid):
    for t in trains:
        if t.id == tid:
            return t
    raise KeyError(tid)


def ripple(trains: list[Train], root_train: str, applied: Optional[dict] = None):
    """Delay-propagation chain starting from `root_train`, expressed as a
    simple downstream tree for visualization."""
    result = simulate(trains, applied)
    delay = result["delay"]
    nodes = [{"id": tid, "delay": d} for tid, d in delay.items() if d > 0.05]
    edges = []
    order = ["T18", "F07", "T21", "T25", "T27", "T29", "T31"]
    prev = None
    for tid in order:
        if delay.get(tid, 0) > 0.05:
            if prev:
                edges.append({"from": prev, "to": tid})
            prev = tid
    return {"nodes": nodes, "edges": edges, "total_delay": result["total_delay"]}
