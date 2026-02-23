import csv
import time
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from .utils import normalize
from .search import SearchIndex, School

DATASET = Path("seed/school_data.csv")

app = FastAPI(title="CandoCorp / Glaamxy Challenge API")
idx = SearchIndex()
_next_id = 1

def detect_columns(header: list[str]) -> tuple[str, str, str]:
    # Intentamos adivinar columnas típicas del dataset NCES
    # Ajustamos si es necesario luego viendo el header real.
    candidates_name = ["SCHNAM05", "SCHOOL_NAME", "SCH_NAME", "school_name"]
    candidates_city = ["LCITY05", "CITY", "city"]
    candidates_state = ["LSTATE05", "STATE", "ST", "state"]

    def pick(cands):
        for c in cands:
            if c in header:
                return c
        return ""

    name = pick(candidates_name)
    city = pick(candidates_city)
    state = pick(candidates_state)

    if not name:
        raise RuntimeError(f"No encontré columna de nombre en header: {header[:20]}")
    if not city:
        raise RuntimeError(f"No encontré columna de ciudad en header: {header[:20]}")
    if not state:
        raise RuntimeError(f"No encontré columna de estado en header: {header[:20]}")
    return name, city, state

def load_csv():
    global _next_id
    if not DATASET.exists():
        raise RuntimeError("No existe seed/school_data.csv. Ejecuta primero scripts/merge_csv.py")

    idx.clear()
    _next_id = 1

    with open(DATASET, "r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        name_col, city_col, state_col = detect_columns(header)

        for row in reader:
            name = row.get(name_col, "") or ""
            city = row.get(city_col, "") or ""
            state = row.get(state_col, "") or ""

            s = School(
                id=_next_id,
                school_name=name,
                city=city,
                state=state,
                raw=row,
                name_norm=normalize(name),
                city_norm=normalize(city),
                state_norm=normalize(state),
            )
            idx.add(s)
            _next_id += 1

@app.on_event("startup")
def startup():
    load_csv()

@app.get("/health")
def health():
    return {"ok": True, "count": len(idx.schools)}

@app.get("/search")
def search(query: str = Query(..., min_length=1)):
    t0 = time.perf_counter()
    results = idx.search(query, k=3)
    ms = (time.perf_counter() - t0) * 1000.0

    return {
        "query": query,
        "search_ms": round(ms, 3),
        "results": [
            {
                "id": s.id,
                "school_name": s.school_name,
                "city": s.city,
                "state": s.state,
                "score": round(score, 3),
            }
            for s, score in results
        ],
    }

@app.get("/schools/{school_id}")
def get_school(school_id: int):
    s = idx.schools.get(school_id)
    if not s:
        raise HTTPException(404, "School not found")
    return {"id": s.id, "school_name": s.school_name, "city": s.city, "state": s.state, "raw": s.raw}