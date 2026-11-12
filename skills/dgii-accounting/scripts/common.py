"""Shared helpers: paths, profile, and reading/writing the ledger.

The ledger lives outside the skill, in ~/Documents/Finanzas/, so the data
survives any change or reinstall of the skill.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# "Finanzas" and "perfil.json" are the real on-disk names. Do not translate.
BASE = Path.home() / "Documents" / "Finanzas"
PROFILE = BASE / "perfil.json"

# Keys are the on-disk schema of perfil.json and stay in Spanish.
DEFAULT_PROFILE = {
    "rnc": "",
    "nombre": "",
    "regimen": "ordinario",          # "ordinario" | "rst"
    "aplica_itbis": True,
    "tasa_itbis": "0.18",
    "retencion_isr_honorarios": "0.15",
    "emite_ecf": False,
}


def dec(value) -> Decimal:
    """Converts to Decimal tolerating None, empty strings and numbers."""
    if value in (None, "", "-"):
        return Decimal("0")
    return Decimal(str(value))


def money(value) -> str:
    """Formats an amount with two decimals, as DGII requires."""
    return str(dec(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def load_profile() -> dict:
    if not PROFILE.exists():
        return dict(DEFAULT_PROFILE)
    profile = dict(DEFAULT_PROFILE)
    profile.update(json.loads(PROFILE.read_text(encoding="utf-8")))
    return profile


def save_profile(profile: dict) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    PROFILE.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")


def ledger_path(kind: str, year: int) -> Path:
    """kind is 'gastos' or 'ingresos', the on-disk file names."""
    return BASE / f"{kind}-{year}.jsonl"


def append_record(kind: str, year: int, record: dict) -> Path:
    path = ledger_path(kind, year)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def read_records(kind: str, year: int, month: int | None = None) -> list[dict]:
    """Reads one year of the ledger, optionally filtered by month (1-12)."""
    path = ledger_path(kind, year)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if month is not None and int(record["fecha"][5:7]) != month:
            continue
        rows.append(record)
    return rows
