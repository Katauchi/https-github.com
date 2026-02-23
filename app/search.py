from dataclasses import dataclass
from typing import Dict, Set, List, Tuple
from .utils import normalize, tokenize

@dataclass
class School:
    id: int
    school_name: str
    city: str
    state: str
    raw: dict
    name_norm: str
    city_norm: str
    state_norm: str

class SearchIndex:
    def __init__(self):
        self.schools: Dict[int, School] = {}
        self.inv: Dict[str, Set[int]] = {}  # token -> set(ids)

    def clear(self):
        self.schools.clear()
        self.inv.clear()

    def add(self, s: School):
        self.schools[s.id] = s
        tokens = set(tokenize(s.school_name) + tokenize(s.city) + tokenize(s.state))
        for t in tokens:
            self.inv.setdefault(t, set()).add(s.id)

    def search(self, query: str, k: int = 3) -> List[Tuple[School, float]]:
        q_norm = normalize(query)
        q_tokens = tokenize(query)

        if not q_tokens and not q_norm:
            return []

        # candidatos por tokens
        cand: Set[int] = set()
        for t in q_tokens:
            cand |= self.inv.get(t, set())

        # fallback si no hay tokens
        if not cand:
            cand = set(self.schools.keys())

        scored: List[Tuple[int, float]] = []
        for sid in cand:
            s = self.schools[sid]
            score = 0.0

            if q_norm and q_norm in s.name_norm:
                score += 50
            if q_norm and q_norm in s.city_norm:
                score += 20
            if q_norm and q_norm in s.state_norm:
                score += 10

            name_tokens = set(tokenize(s.school_name))
            city_tokens = set(tokenize(s.city))
            state_tokens = set(tokenize(s.state))

            for t in q_tokens:
                if t in name_tokens: score += 12
                if t in city_tokens: score += 6
                if t in state_tokens: score += 4

            score -= min(len(s.name_norm), 80) * 0.02
            scored.append((sid, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [(self.schools[i], sc) for i, sc in scored[:k]]