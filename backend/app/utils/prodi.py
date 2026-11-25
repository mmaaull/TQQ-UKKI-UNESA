"""Samakan variasi penulisan prodi tanpa mencampur jenjang pendidikan."""

import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Any, Iterable

from backend.app.utils.helpers import normalize_text


DEGREE_PATTERN = re.compile(r"^(D[1-4]|S[1-3])\s*[-.]?\s*(.+)$", re.IGNORECASE)


def _prodi_parts(value: str) -> tuple[str, str, str]:
    text = re.sub(r"\s+", " ", value).strip()
    match = DEGREE_PATTERN.match(text)
    degree, name = (match.group(1).upper(), match.group(2)) if match else ("", text)
    name = re.sub(r"(?<=[A-Za-z])\s*1$", "", name).strip()
    name = re.sub(r"\bpeforma\b", "Performa", name, flags=re.IGNORECASE)
    key = re.sub(r"[^\w\s]", " ", name.casefold())
    key = re.sub(r"\s+", " ", key).strip()
    return degree, name, key


def canonical_prodi_map(values: Iterable[Any]) -> dict[str, str]:
    """Peta nama asli ke nama seragam untuk prodi yang terdeteksi sama."""
    cleaned_values = [normalize_text(value) for value in values]
    names = sorted({value for value in cleaned_values if value}, key=str.casefold)
    parts = {name: _prodi_parts(name) for name in names}
    parent = {name: name for name in names}

    def root(name: str) -> str:
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    for index, left in enumerate(names):
        degree_left, _, key_left = parts[left]
        for right in names[index + 1 :]:
            degree_right, _, key_right = parts[right]
            if degree_left != degree_right or not key_left or not key_right:
                continue
            if key_left == key_right or (
                len(key_left.split()) == len(key_right.split())
                and SequenceMatcher(None, key_left, key_right).ratio() >= 0.94
            ):
                parent[root(right)] = root(left)

    clusters: dict[str, list[str]] = {}
    for name in names:
        clusters.setdefault(root(name), []).append(name)

    counts = Counter(cleaned_values)
    mapping: dict[str, str] = {}
    for cluster in clusters.values():
        if len(cluster) == 1:
            mapping[cluster[0]] = cluster[0]
            continue
        best = min(cluster, key=lambda name: (-counts[name], len(parts[name][1]), parts[name][1].casefold()))
        degree, cleaned_name, _ = parts[best]
        label = f"{degree} {cleaned_name.title()}".strip()
        for name in cluster:
            mapping[name] = label
    return mapping
