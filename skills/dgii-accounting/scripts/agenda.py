#!/usr/bin/env python3
"""Says what has to be sent to DGII, when, and whether the period goes at zero.

Reads the regime from perfil.json and the ledger to know whether there were
any movements.

Usage:
  agenda.py                    # status for today
  agenda.py --date 2026-09-14  # simulate another date
"""
from __future__ import annotations

import argparse
import calendar
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_profile, read_records  # noqa: E402

ECF_MANDATORY_DATE = date(2026, 11, 15)  # Aviso 06-26, small/micro/unclassified


def last_business_day(year: int, month: int) -> date:
    """Last working day of the month, counting Monday to Friday only.
    It does not consider Dominican holidays: when in doubt, file early.
    """
    d = date(year, month, calendar.monthrange(year, month)[1])
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def previous_period(today: date) -> tuple[int, int]:
    return (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)


def block(title: str) -> None:
    print(f"\n{title}\n" + "-" * len(title))


def days_left(today: date, deadline: date) -> str:
    d = (deadline - today).days
    if d < 0:
        return f"OVERDUE by {-d} days"
    if d == 0:
        return "DUE TODAY"
    return f"{d} days left"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", help="YYYY-MM-DD to simulate another day")
    a = p.parse_args()
    today = date.fromisoformat(a.date) if a.date else date.today()

    profile = load_profile()
    regime = profile.get("regimen", "ordinario")
    py, pm = previous_period(today)
    period = f"{py}{pm:02d}"

    print("=" * 62)
    print(f"DGII AGENDA  |  {today.isoformat()}  |  regime: {regime.upper()}")
    print("=" * 62)

    if regime == "ordinario":
        block(f"MONTHLY  (period {period})")
        deadline_formats = date(today.year, today.month, 15)
        deadline_it1 = date(today.year, today.month, 20)

        n_expenses = len(read_records("gastos", py, pm))
        n_income = len(read_records("ingresos", py, pm))

        status_606 = f"{n_expenses} record" + ("s" if n_expenses != 1 else "") if n_expenses else "NO MOVEMENTS -> file AT ZERO"
        status_607 = f"{n_income} record" + ("s" if n_income != 1 else "") if n_income else "NO MOVEMENTS -> file AT ZERO"

        print(f"  606 Purchases  deadline {deadline_formats}  ({days_left(today, deadline_formats)})  {status_606}")
        print(f"  607 Sales      deadline {deadline_formats}  ({days_left(today, deadline_formats)})  {status_607}")
        print(f"  608 Voided     deadline {deadline_formats}  ({days_left(today, deadline_formats)})  only if you voided an NCF")
        print(f"  IT-1 ITBIS     deadline {deadline_it1}  ({days_left(today, deadline_it1)})  filed even if it goes at zero")
        print("\n  Mandatory order: 606 and 607 -> Anexo A -> IT-1")
        print("  No movements: OFV -> Declaraciones Juradas -> Declaraciones en Cero")

        block("ANNUAL")
        ir1 = date(today.year if today.month <= 3 else today.year + 1, 3, 31)
        print(f"  IR-1 natural person income tax  deadline {ir1}  ({days_left(today, ir1)})")
        print("  This is where you credit the 15% of ISR withheld and claim the credit balance.")

    else:
        block("ANNUAL  (RST)")
        decl = last_business_day(today.year if today.month <= 2 else today.year + 1, 2)
        second = last_business_day(today.year if today.month <= 8 else today.year + 1, 8)
        print(f"  Simplified return + 1st installment  deadline {decl}  ({days_left(today, decl)})")
        print(f"  2nd installment                      deadline {second}  ({days_left(today, second)})")
        print("\n  Under RST you do not send 606, 607 or 608, and you pay no ISR advances.")
        print("  You still keep the ledger: it is the basis of the return and of the IR-1.")

    block("RST APPLICATION / RENEWAL")
    ref = last_business_day(today.year + 1 if today.month > 2 else today.year, 2)
    deadline_rst = ref - timedelta(days=60)
    print(f"  Last date to apply for the RST of the next fiscal year: {deadline_rst}  ({days_left(today, deadline_rst)})")
    print("  Rule: up to 60 days before the last working day of February.")

    block("ELECTRONIC INVOICING (e-CF)")
    if profile.get("emite_ecf"):
        print("  You already issue e-CF. Download and back up the XML every month (keep 10 years).")
    else:
        print(f"  Mandatory from {ECF_MANDATORY_DATE}  ({days_left(today, ECF_MANDATORY_DATE)})")
        print("  Fine for noncompliance: 5 to 50 minimum wages.")
        print("  Free path: OFV -> Solicitudes -> Facturador Gratuito (digital certificate")
        print("  free for 1 year, up to 150 vouchers per month).")

    block("ALWAYS")
    print("  - Download the XML of the e-CF issued and received. DGII only keeps them 2 years,")
    print("    you answer for 10 (Art. 50 Codigo Tributario).")
    print("  - Keep the certificado de retencion from every client. Without it you cannot credit the 15%.")
    print("  - Being up to date is a requirement to keep the RST and the Facturador Gratuito.")
    print()


if __name__ == "__main__":
    main()
