#!/usr/bin/env python3
"""Money math: what to charge, what reaches the bank, what to set aside.

Rules applied (verified against DGII and Ley 30-26, in force 1 July 2026):
  - A legal entity paying a natural person withholds 15% of ISR on fees.
  - And withholds 100% of the invoiced ITBIS.
  - The 15% of ISR is a payment on account, credited in the IR-1.

Usage:
  calc.py quote --net 100000         # what to invoice to receive 100,000
  calc.py quote --service 100000     # what I receive if I invoice 100,000
  calc.py projection --year 2026
  calc.py projection --gross 800000
"""
from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_profile, dec, read_records, money  # noqa: E402

# Annual ISR scale for a natural person, 2026 (resolucion DDG-AR1-2026-00001).
# (lower_limit, fixed_tax, rate_on_excess)
SCALE_2026 = [
    (Decimal("867123.01"), Decimal("79776"), Decimal("0.25")),
    (Decimal("624329.01"), Decimal("31216"), Decimal("0.20")),
    (Decimal("416220.01"), Decimal("0"), Decimal("0.15")),
    (Decimal("0"), Decimal("0"), Decimal("0")),
]
EXEMPTION = Decimal("416220")
RST_DEDUCTION = Decimal("0.40")
RST_CAP_2026 = Decimal("12068181.09")


def annual_isr(base: Decimal) -> Decimal:
    """Applies the natural person scale to the net taxable income."""
    for limit, fixed, rate in SCALE_2026:
        if base >= limit:
            floor = limit - Decimal("0.01") if limit > 0 else Decimal("0")
            return fixed + (base - floor) * rate
    return Decimal("0")


def cmd_quote(a: argparse.Namespace) -> None:
    profile = load_profile()
    r_itbis = dec(profile["tasa_itbis"]) if profile.get("aplica_itbis") else Decimal("0")
    r_isr = dec(profile["retencion_isr_honorarios"])

    if a.net:
        service = dec(a.net) / (Decimal("1") - r_isr)
        print(f"To receive RD${money(a.net)} clean in the bank:")
    else:
        service = dec(a.service)
        print(f"If you invoice a service of RD${money(service)}:")

    itbis = service * r_itbis
    total = service + itbis
    wh_itbis = itbis
    wh_isr = service * r_isr
    you_get = total - wh_itbis - wh_isr

    print()
    print(f"  Service (taxable base)         RD${money(service):>14}")
    print(f"  ITBIS {r_itbis * 100:.0f}%                      RD${money(itbis):>14}")
    print(f"  TOTAL TO INVOICE               RD${money(total):>14}")
    print()
    print(f"  Less ITBIS withholding 100%    RD${money(-wh_itbis):>14}")
    print(f"  Less ISR withholding {r_isr * 100:.0f}%       RD${money(-wh_isr):>14}")
    print(f"  YOU RECEIVE IN THE BANK        RD${money(you_get):>14}")
    print()
    print(f"  The withheld ISR (RD${money(wh_isr)}) is NOT lost: it is credited in the IR-1.")
    if a.net:
        print(f"  Quote the service at RD${money(service)} plus ITBIS.")


def cmd_projection(a: argparse.Namespace) -> None:
    profile = load_profile()
    if a.gross:
        gross = dec(a.gross)
        real_expenses = dec(a.expenses)
        isr_withheld = gross * dec(profile["retencion_isr_honorarios"])
        source = "amount given"
    else:
        income = read_records("ingresos", a.year)
        expenses = read_records("gastos", a.year)
        gross = sum((dec(f["monto_facturado"]) for f in income), Decimal("0"))
        real_expenses = sum(
            (dec(f["monto_servicios"]) + dec(f["monto_bienes"]) for f in expenses), Decimal("0")
        )
        isr_withheld = sum((dec(f["retencion_renta_terceros"]) for f in income), Decimal("0"))
        source = f"ledger {a.year} ({len(income)} invoices)"

    base_ord = max(gross - real_expenses, Decimal("0"))
    base_rst = gross * (Decimal("1") - RST_DEDUCTION)
    isr_ord = annual_isr(base_ord)
    isr_rst = annual_isr(base_rst)

    print(f"== ISR projection ==  source: {source}")
    print(f"\n  Invoiced before taxes            RD${money(gross):>14}")
    print(f"  Natural person annual exemption  RD${money(EXEMPTION):>14}")
    print()
    print(f"  {'':<28}{'ORDINARIO':>16}{'RST':>16}")
    print(f"  {'Deduction':<28}{money(real_expenses):>16}{money(base_rst and gross * RST_DEDUCTION):>16}")
    print(f"  {'Taxable base':<28}{money(base_ord):>16}{money(base_rst):>16}")
    print(f"  {'Estimated ISR for the year':<28}{money(isr_ord):>16}{money(isr_rst):>16}")
    print()
    print(f"  Already withheld from you (15%)  RD${money(isr_withheld):>14}")

    regime = profile.get("regimen", "ordinario")
    isr_applied = isr_rst if regime == "rst" else isr_ord
    balance = isr_withheld - isr_applied
    if balance >= 0:
        print(f"  CREDIT BALANCE ({regime})      RD${money(balance):>14}")
        print("\n  You only get it back by filing the IR-1. If you do not file, you give it away.")
    else:
        print(f"  STILL TO PAY ({regime})        RD${money(-balance):>14}")
        print(f"\n  Set aside RD${money(-balance)} before 31 March.")

    if gross > RST_CAP_2026:
        print(f"\n  NOTICE: you passed the RST cap for 2026 (RD${money(RST_CAP_2026)}).")

    print("\n  Estimated numbers. The fine calculation, in particular how the 40% of the")
    print("  RST interacts with the contributory exemption (Art. 17 Decreto 265-19), is")
    print("  confirmed by an accountant. The direction of the result is reliable.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("quote", help="price to invoice and net that reaches the bank")
    group = c.add_mutually_exclusive_group(required=True)
    group.add_argument("--net", help="how much you want to receive clean")
    group.add_argument("--service", help="price of the service before taxes")
    c.set_defaults(func=cmd_quote)

    pr = sub.add_parser("projection", help="estimated ISR and credit balance")
    pr.add_argument("--year", type=int, help="calculate from the ledger")
    pr.add_argument("--gross", help="or simulate with an invoiced amount")
    pr.add_argument("--expenses", default=0, help="real documented expenses (with --gross)")
    pr.set_defaults(func=cmd_projection)

    a = p.parse_args()
    if a.cmd == "projection" and not a.year and not a.gross:
        p.error("projection needs --year or --gross")
    a.func(a)


if __name__ == "__main__":
    main()
