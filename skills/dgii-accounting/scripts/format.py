#!/usr/bin/env python3
"""Generates the rows of formats 606 and 607 in the exact column order that
the DGII Excel template requires (Norma General 07-2018).

The output is TSV: it pastes straight into the official template. This script
does NOT generate the final TXT. That one is produced by the DGII template with
its "Generar Archivo" button, the only path the Oficina Virtual accepts.

Usage:
  format.py 606 --period 202608
  format.py 607 --period 202608
  format.py 607 --period 202608 --output ~/Documents/Finanzas/607-202608.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import load_profile, dec, read_records, money  # noqa: E402

# Column names are the literal DGII headers. Never translate them.
COLUMNS_606 = [
    "RNC/Cedula", "Tipo Id", "Tipo Bienes y Servicios Comprados", "NCF",
    "NCF o Documento Modificado", "Fecha Comprobante", "Fecha Pago",
    "Monto Facturado en Servicios", "Monto Facturado en Bienes",
    "Total Monto Facturado (auto)", "ITBIS Facturado", "ITBIS Retenido",
    "ITBIS sujeto a Proporcionalidad", "ITBIS llevado al Costo",
    "ITBIS por Adelantar (auto)", "ITBIS percibido en compras",
    "Tipo de Retencion en ISR", "Monto Retencion Renta",
    "ISR Percibido en compras", "Impuesto Selectivo al Consumo",
    "Otros Impuestos/Tasas", "Monto Propina Legal", "Forma de Pago",
]

COLUMNS_607 = [
    "RNC/Cedula/Pasaporte", "Tipo Identificacion", "Numero Comprobante Fiscal",
    "Numero Comprobante Fiscal Modificado", "Tipo de Ingreso",
    "Fecha Comprobante", "Fecha de Retencion", "Monto Facturado",
    "ITBIS Facturado", "ITBIS Retenido por Terceros", "ITBIS Percibido",
    "Retencion Renta por Terceros", "ISR Percibido",
    "Impuesto Selectivo al Consumo", "Otros Impuestos/Tasas",
    "Monto Propina Legal", "Efectivo", "Cheque/Transferencia/Deposito",
    "Tarjeta Debito/Credito", "Venta a Credito", "Bonos o Certificados de Regalo",
    "Permuta", "Otras Formas de Ventas",
]

# On-disk channel names stored in canal_cobro, in the order of boxes 17 to 23.
CHANNELS_607 = [
    "efectivo", "cheque_transferencia", "tarjeta", "venta_credito",
    "bonos", "permuta", "otras",
]


def dgii_date(iso: str) -> str:
    """YYYY-MM-DD -> YYYYMMDD. Empty string if there is no date."""
    return iso.replace("-", "") if iso else ""


def rows_606(year: int, month: int) -> list[list[str]]:
    rows = []
    for g in read_records("gastos", year, month):
        rows.append([
            g["rnc"], str(g["tipo_id"]), str(g["categoria"]), g["ncf"],
            g.get("ncf_modificado", ""), dgii_date(g["fecha"]),
            dgii_date(g.get("fecha_pago", "")),
            money(g["monto_servicios"]), money(g["monto_bienes"]),
            "",  # Total Monto Facturado: the template computes it on validation
            money(g["itbis_facturado"]), money(g["itbis_retenido"]),
            "", money(g["itbis_al_costo"]),
            "",  # ITBIS por Adelantar: the template computes it on validation
            "", str(g.get("tipo_retencion_isr", "") or ""),
            money(g["monto_retencion_isr"]), "",
            money(g["isc"]), money(g["otros_impuestos"]), money(g["propina"]),
            str(g["forma_pago"]),
        ])
    return rows


def rows_607(year: int, month: int) -> list[list[str]]:
    rows = []
    for i in read_records("ingresos", year, month):
        channels = {c: "" for c in CHANNELS_607}
        channels[i.get("canal_cobro", "otras")] = money(i["monto_canal"])
        rows.append([
            i["rnc_cliente"], str(i["tipo_id"]), i["ncf"],
            i.get("ncf_modificado", ""), str(i["tipo_ingreso"]),
            dgii_date(i["fecha"]), dgii_date(i.get("fecha_retencion", "")),
            money(i["monto_facturado"]), money(i["itbis_facturado"]),
            money(i["itbis_retenido_terceros"]), "",
            money(i["retencion_renta_terceros"]), "",
            money(i["isc"]), money(i["otros_impuestos"]), money(i["propina"]),
        ] + [channels[c] for c in CHANNELS_607])
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("format", choices=["606", "607"])
    p.add_argument("--period", required=True, help="YYYYMM, for example 202608")
    p.add_argument("--output", help="path of the TSV file (prints to screen by default)")
    a = p.parse_args()

    if len(a.period) != 6 or not a.period.isdigit():
        p.error("--period must be YYYYMM, for example 202608")
    year, month = int(a.period[:4]), int(a.period[4:])

    profile = load_profile()
    columns = COLUMNS_606 if a.format == "606" else COLUMNS_607
    rows = rows_606(year, month) if a.format == "606" else rows_607(year, month)

    lines = ["\t".join(columns)] + ["\t".join(f) for f in rows]
    content = "\n".join(lines)

    print("=" * 70)
    print(f"FORMAT {a.format}  |  period {a.period}")
    print(f"RNC: {profile['rnc'] or '(not set in perfil.json)'}")
    print(f"Number of records: {len(rows)}")
    print("=" * 70)

    if not rows:
        print("\nNO MOVEMENTS IN THIS PERIOD.")
        print("The filing is not skipped: it goes out INFORMATIVE (at zero).")
        print("OFV -> Declaraciones Juradas -> Declaraciones en Cero")
        print(f"   Format: {a.format}   Period: {a.period}")
        return

    if a.output:
        Path(a.output).expanduser().write_text(content + "\n", encoding="utf-8")
        print(f"\nWritten to {a.output}")
    else:
        print("\n" + content)

    total_col = 7 if a.format == "607" else None
    if total_col is not None:
        total = sum((dec(f[total_col]) for f in rows), dec(0))
        print(f"\nTotal invoiced before taxes: RD${money(total)}")

    print("\nNext step:")
    print("  1. Download the official template at dgii.gov.do -> Herramientas ->")
    print(f"     Formularios -> Formatos Envios de Datos -> Formato {a.format}")
    print("  2. Enable macros. Fill the header: RNC, period, number of records.")
    print("  3. Press Inicio, paste these rows, press Validar.")
    print("  4. Fix whatever the Estatus column flags and validate again.")
    print("  5. Press Generar Archivo and send the TXT through the Oficina Virtual.")
    print("\nThe columns marked (auto) are filled by the template itself on validation.")


if __name__ == "__main__":
    main()
