"""
RAILSHIELD backend API.

Run with:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open frontend/index.html (it calls http://localhost:8000).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

import engine

app = FastAPI(title="RAILSHIELD API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory "digital twin" state — reset on restart, mutated by /approve
STATE = {"trains": engine.default_network(), "applied": {}}


def current_trains():
    return STATE["trains"]


@app.get("/api/state")
def get_state():
    sim = engine.simulate(current_trains(), STATE["applied"])
    return {
        "sections": engine.SECTIONS,
        "trains": [
            {"id": t.id, "type": t.type, "route": t.route,
             "delay": sim["delay"].get(t.id, 0)}
            for t in current_trains()
        ],
        "total_delay": sim["total_delay"],
        "conflicts": sim["conflicts"],
    }


@app.get("/api/future")
def get_future(horizon: int = 15):
    field = engine.risk_field(current_trains(), horizon)
    return {"horizon": horizon, "field": field}


@app.get("/api/future/series")
def get_future_series():
    """Risk field at several horizons at once, for the timeline scrubber."""
    return {h: engine.risk_field(current_trains(), h) for h in [5, 10, 15, 20, 30]}


@app.get("/api/conflicts")
def get_conflicts():
    sim = engine.simulate(current_trains(), STATE["applied"])
    out = []
    for i, c in enumerate(sim["conflicts"]):
        out.append({"id": f"conflict-{i}", **c,
                     "probability": min(0.97, 0.5 + c["added_delay"] / 20)})
    return out


@app.get("/api/conflicts/{conflict_id}/options")
def get_options(conflict_id: str):
    sim = engine.simulate(current_trains(), STATE["applied"])
    idx = _idx(conflict_id)
    if idx >= len(sim["conflicts"]):
        raise HTTPException(404, "conflict not found")
    conflict = sim["conflicts"][idx]
    return {"conflict": conflict,
            "options": engine.generate_interventions(current_trains(), conflict)}


@app.get("/api/conflicts/{conflict_id}/rootcause")
def get_root_cause(conflict_id: str):
    sim = engine.simulate(current_trains(), STATE["applied"])
    idx = _idx(conflict_id)
    if idx >= len(sim["conflicts"]):
        raise HTTPException(404, "conflict not found")
    section = sim["conflicts"][idx]["section"]
    return engine.root_cause(current_trains(), section)


@app.get("/api/conflicts/{conflict_id}/counterfactual")
def get_counterfactual(conflict_id: str, option_id: str = "speed"):
    sim = engine.simulate(current_trains(), STATE["applied"])
    idx = _idx(conflict_id)
    if idx >= len(sim["conflicts"]):
        raise HTTPException(404, "conflict not found")
    conflict = sim["conflicts"][idx]
    options = engine.generate_interventions(current_trains(), conflict)
    chosen = next((o for o in options if o["id"] == option_id), options[0])

    no_action = engine.ripple(current_trains(), conflict["trains"][0], STATE["applied"])
    applied = _option_to_applied(conflict, chosen)
    with_action = engine.ripple(current_trains(), conflict["trains"][0], applied)
    return {"no_action": no_action, "with_action": with_action, "option": chosen}


class ApproveBody(BaseModel):
    option_id: str


@app.post("/api/conflicts/{conflict_id}/approve")
def approve(conflict_id: str, body: ApproveBody):
    sim = engine.simulate(current_trains(), STATE["applied"])
    idx = _idx(conflict_id)
    if idx >= len(sim["conflicts"]):
        raise HTTPException(404, "conflict not found")
    conflict = sim["conflicts"][idx]
    options = engine.generate_interventions(current_trains(), conflict)
    chosen = next((o for o in options if o["id"] == body.option_id), options[0])
    applied = _option_to_applied(conflict, chosen)
    STATE["applied"].update(applied)
    new_sim = engine.simulate(current_trains(), STATE["applied"])
    return {"applied": applied, "new_total_delay": new_sim["total_delay"],
            "remaining_conflicts": len(new_sim["conflicts"])}


@app.post("/api/reset")
def reset():
    STATE["trains"] = engine.default_network()
    STATE["applied"] = {}
    return {"ok": True}


def _idx(conflict_id: str) -> int:
    try:
        return int(conflict_id.split("-")[-1])
    except ValueError:
        raise HTTPException(400, "bad conflict id")


def _option_to_applied(conflict, option):
    a, b = conflict["trains"]
    yielder = conflict["yields"]
    holder = a if yielder == b else b
    if option["id"] == "hold":
        return {yielder: {"held_min": 5}}
    if option["id"] == "speed":
        return {holder: {"speed_delta_kmh": -14}}
    if option["id"] == "reroute":
        return {yielder: {"section_shift": {conflict["section"]: 7}}}
    return {yielder: {"held_min": 14}}


# Optionally serve the built frontend directly from the backend at "/"
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
