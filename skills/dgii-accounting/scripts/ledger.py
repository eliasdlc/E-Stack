#!/usr/bin/env python3
"""Records and queries the ledger of income and expenses.

The agent translates what Elias says in natural language ("I bought hosting for
1500 pesos") into a call to this script. Elias never writes these flags.

Examples:
  ledger.py expense --date 2026-08-18 --rnc 130123456 --ncf B0100000123 \
      --category 6 --services 1500 --itbis 270 --payment-method 3 --desc "annual hosting"

  ledger.py income --date 2026-08-20 --client-rnc 101234567 --ncf E310000000001 \
      --amount 100000 --itbis 18000 --itbis-withheld 18000 --isr-withheld 15000 \
      --withholding-date 2026-08-25 --payment-channel transfer --desc "B2B portal phase 1"

  ledger.py list --year 2026 --month 8
  ledger.py summary --year 2026
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import append_record, dec, read_records, money  # noqa: E402

# Descriptions come from the official DGII code tables and stay in Spanish.
EXPENSE_CATEGORIES = {
    1: "Gastos de personal",
    2: "Gastos por trabajos, suministros y servicios",
    3: "Arrendamientos",
    4: "Gastos de activos fijos",
    5: "Gastos de representacion",
    6: "Otras deducciones admitidas",
    7: "Gastos financieros",
    8: "Gastos extraordinarios",
    9: "Compras y gastos que formaran parte del costo de venta",
    10: "Adquisiciones de activos",
    11: "Gastos de seguros",
}

PAYMENT_METHODS = {
    1: "Efectivo",
    2: "Cheques/Transferencias/Deposito",
    3: "Tarjeta credito/debito",
    4: "Compra a credito",
    5: "Permuta",
    6: "Notas de credito",
    7: "Mixto",
}

ISR_WITHHOLDING_TYPES = {
    1: "Alquileres",
    2: "Honorarios por servicios",
    3: "Otras rentas",
    4: "Otras rentas (rentas presuntas)",
    5: "Intereses pagados a personas juridicas residentes",
    6: "Intereses pagados a personas fisicas residentes",
    7: "Retencion por proveedores del Estado",
    8: "Juegos telefonicos",
    9: "Retenciones subsector de ganaderia de carne bovina",
}

INCOME_TYPES = {
    1: "Ingresos por operaciones (No financieros)",
    2: "Ingresos Financieros",
    3: "Ingresos Extraordinarios",
    4: "Ingresos por Arrendamientos",
    5: "Ingresos por Venta de Activo Depreciable",
    6: "Otros Ingresos",
}

# Boxes 17 to 23 of format 607. The values are the on-disk channel names.
PAYMENT_CHANNELS = {
    "cash": "efectivo",
    "transfer": "cheque_transferencia",
    "check": "cheque_transferencia",
    "deposit": "cheque_transferencia",
    "card": "tarjeta",
    "credit": "venta_credito",
    "gift-certificate": "bonos",
    "barter": "permuta",
    "other": "otras",
}

# On-disk ledger file names, one per kind of movement.
LEDGER_KINDS = {"income": "ingresos", "expenses": "gastos"}


def cmd_expense(a: argparse.Namespace) -> None:
    record = {
        "fecha": a.date,
        "fecha_pago": a.payment_date or "",
        "rnc": a.rnc,
        "tipo_id": a.id_type,
        "ncf": a.ncf,
        "ncf_modificado": a.modified_ncf or "",
        "categoria": a.category,
        "monto_servicios": money(a.services),
        "monto_bienes": money(a.goods),
        "itbis_facturado": money(a.itbis),
        "itbis_retenido": money(a.itbis_withheld),
        "itbis_al_costo": money(a.itbis_to_cost),
        "tipo_retencion_isr": a.isr_withholding_type or "",
        "monto_retencion_isr": money(a.isr_withheld),
        "isc": money(a.isc),
        "otros_impuestos": money(a.other_taxes),
        "propina": money(a.tip),
        "forma_pago": a.payment_method,
        "descripcion": a.desc,
    }
    year = int(a.date[:4])
    path = append_record("gastos", year, record)
    total = dec(a.services) + dec(a.goods) + dec(a.itbis)
    print(f"Expense recorded in {path}")
    print(f"  {a.desc} | NCF {a.ncf} | total RD${money(total)}")
    print(f"  category {a.category}: {EXPENSE_CATEGORIES.get(a.category, '?')}")


def cmd_income(a: argparse.Namespace) -> None:
    channel = PAYMENT_CHANNELS.get(a.payment_channel, "otras")
    # The amount per collection channel includes taxes and must add up to the invoiced total.
    gross = dec(a.amount) + dec(a.itbis) + dec(a.isc) + dec(a.other_taxes) + dec(a.tip)
    record = {
        "fecha": a.date,
        "fecha_retencion": a.withholding_date or "",
        "rnc_cliente": a.client_rnc,
        "tipo_id": a.id_type,
        "ncf": a.ncf,
        "ncf_modificado": a.modified_ncf or "",
        "tipo_ingreso": a.income_type,
        "monto_facturado": money(a.amount),
        "itbis_facturado": money(a.itbis),
        "itbis_retenido_terceros": money(a.itbis_withheld),
        "retencion_renta_terceros": money(a.isr_withheld),
        "isc": money(a.isc),
        "otros_impuestos": money(a.other_taxes),
        "propina": money(a.tip),
        "canal_cobro": channel,
        "monto_canal": money(gross),
        "descripcion": a.desc,
    }
    year = int(a.date[:4])
    path = append_record("ingresos", year, record)
    net = gross - dec(a.itbis_withheld) - dec(a.isr_withheld)
    print(f"Income recorded in {path}")
    print(f"  {a.desc} | NCF {a.ncf} | invoiced RD${money(gross)}")
    print(f"  withholdings: ITBIS RD${money(a.itbis_withheld)} + ISR RD${money(a.isr_withheld)}")
    print(f"  you should receive RD${money(net)}")


def cmd_list(a: argparse.Namespace) -> None:
    kinds = ["income", "expenses"] if a.kind == "all" else [a.kind]
    for kind in kinds:
        rows = read_records(LEDGER_KINDS[kind], a.year, a.month)
        print(f"\n== {kind.upper()} {a.year}" + (f"-{a.month:02d}" if a.month else "") + f" ({len(rows)}) ==")
        for f in rows:
            if kind == "expenses":
                total = dec(f["monto_servicios"]) + dec(f["monto_bienes"]) + dec(f["itbis_facturado"])
            else:
                total = dec(f["monto_facturado"]) + dec(f["itbis_facturado"])
            print(f"  {f['fecha']}  {f['ncf']:<15} RD${money(total):>12}  {f['descripcion']}")


def cmd_summary(a: argparse.Namespace) -> None:
    income = read_records("ingresos", a.year)
    expenses = read_records("gastos", a.year)
    invoiced = sum((dec(f["monto_facturado"]) for f in income), dec(0))
    itbis_wh = sum((dec(f["itbis_retenido_terceros"]) for f in income), dec(0))
    isr_wh = sum((dec(f["retencion_renta_terceros"]) for f in income), dec(0))
    spent = sum((dec(f["monto_servicios"]) + dec(f["monto_bienes"]) for f in expenses), dec(0))

    print(f"== Summary {a.year} ==")
    print(f"  Invoiced before taxes   : RD${money(invoiced):>14}")
    print(f"  Documented expenses     : RD${money(spent):>14}")
    print(f"  ITBIS withheld by clients : RD${money(itbis_wh):>10}")
    print(f"  ISR withheld (creditable in IR-1) : RD${money(isr_wh):>10}")
    print(f"  Records: {len(income)} income, {len(expenses)} expenses")
    print("\n  The withheld ISR is an advance. It is credited in the IR-1 of 31 March.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("expense", help="records a purchase (feeds the 606)")
    g.add_argument("--date", required=True, help="YYYY-MM-DD of the voucher")
    g.add_argument("--payment-date", help="YYYY-MM-DD, required if there was a withholding")
    g.add_argument("--rnc", required=True, help="RNC or cedula of the supplier")
    g.add_argument("--id-type", type=int, default=1, choices=[1, 2], help="1=RNC 2=Cedula")
    g.add_argument("--ncf", required=True)
    g.add_argument("--modified-ncf")
    g.add_argument("--category", type=int, required=True, choices=sorted(EXPENSE_CATEGORIES))
    g.add_argument("--services", default=0, help="amount in services, before taxes")
    g.add_argument("--goods", default=0, help="amount in goods, before taxes")
    g.add_argument("--itbis", default=0, help="invoiced ITBIS")
    g.add_argument("--itbis-withheld", default=0)
    g.add_argument("--itbis-to-cost", default=0)
    g.add_argument("--isr-withholding-type", type=int, choices=sorted(ISR_WITHHOLDING_TYPES))
    g.add_argument("--isr-withheld", default=0)
    g.add_argument("--isc", default=0)
    g.add_argument("--other-taxes", default=0)
    g.add_argument("--tip", default=0)
    g.add_argument("--payment-method", type=int, default=2, choices=sorted(PAYMENT_METHODS))
    g.add_argument("--desc", required=True)
    g.set_defaults(func=cmd_expense)

    i = sub.add_parser("income", help="records an issued invoice (feeds the 607)")
    i.add_argument("--date", required=True, help="YYYY-MM-DD of the voucher")
    i.add_argument("--withholding-date", help="YYYY-MM-DD, required if there was a withholding")
    i.add_argument("--client-rnc", required=True)
    i.add_argument("--id-type", type=int, default=1, choices=[1, 2, 3], help="1=RNC 2=Cedula 3=Pasaporte")
    i.add_argument("--ncf", required=True)
    i.add_argument("--modified-ncf")
    i.add_argument("--income-type", type=int, default=1, choices=sorted(INCOME_TYPES))
    i.add_argument("--amount", required=True, help="sale before taxes")
    i.add_argument("--itbis", default=0)
    i.add_argument("--itbis-withheld", default=0, help="ITBIS withheld by the client")
    i.add_argument("--isr-withheld", default=0, help="ISR withheld by the client")
    i.add_argument("--isc", default=0)
    i.add_argument("--other-taxes", default=0)
    i.add_argument("--tip", default=0)
    i.add_argument("--payment-channel", default="transfer", choices=sorted(PAYMENT_CHANNELS))
    i.add_argument("--desc", required=True)
    i.set_defaults(func=cmd_income)

    l = sub.add_parser("list", help="lists movements")
    l.add_argument("--year", type=int, required=True)
    l.add_argument("--month", type=int)
    l.add_argument("--kind", default="all", choices=["all", "income", "expenses"])
    l.set_defaults(func=cmd_list)

    r = sub.add_parser("summary", help="totals for the year")
    r.add_argument("--year", type=int, required=True)
    r.set_defaults(func=cmd_summary)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
