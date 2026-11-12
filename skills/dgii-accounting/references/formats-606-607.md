# Formats 606 and 607: field specification

Source: official DGII instructions, Norma General 07-2018 and 05-2019.
The script `scripts/format.py` emits the rows already in this exact order.

## Official filing path

DGII **does not accept a hand made TXT**. The only valid path is:

1. dgii.gov.do -> Herramientas -> Formularios -> Formatos Envios de Datos
2. Download the Excel template of the format and **enable macros**
3. Header: RNC or cedula, period `YYYYMM`, number of records (max 10,000)
4. Press **Inicio**: it enables that number of rows
5. Paste the generated rows
6. Press **Validar**. Errors show up in the **Estatus** column
7. Fix and validate again until it comes out clean
8. Press **Generar Archivo**: it produces the TXT
9. Send the TXT through the Oficina Virtual

Amounts with a decimal point and two positions. Example: `10.18`.

---

## Format 606: Compras de Bienes y Servicios

Columns in order:

| # | Field | Note |
|---|---|---|
| 1 | RNC/Cedula | of the supplier |
| 2 | Tipo Id | 1=RNC, 2=Cedula |
| 3 | Tipo de Bienes y Servicios Comprados | table below |
| 4 | NCF | 11 or 13 alphanumeric positions |
| 5 | NCF o Documento Modificado | credit/debit notes only |
| 6 | Fecha Comprobante | YYYYMMDD |
| 7 | Fecha Pago | YYYYMMDD. **Required if there is a withholding** |
| 8 | Monto Facturado en Servicios | before taxes |
| 9 | Monto Facturado en Bienes | before taxes |
| 10 | Total Monto Facturado | **automatic on validation, leave empty** |
| 11 | ITBIS Facturado | |
| 12 | ITBIS Retenido | requires box 7 |
| 13 | ITBIS sujeto a Proporcionalidad (Art. 349) | normally empty |
| 14 | ITBIS llevado al Costo | the one that is not advanced |
| 15 | ITBIS por Adelantar | **automatic on validation, leave empty** |
| 16 | ITBIS percibido en compras | field not enabled yet |
| 17 | Tipo de Retencion en ISR | table below. Requires box 7 |
| 18 | Monto Retencion Renta | requires box 7 |
| 19 | ISR Percibido en compras | field not enabled yet |
| 20 | Impuesto Selectivo al Consumo | |
| 21 | Otros Impuestos/Tasas | |
| 22 | Monto Propina Legal | Ley 54-32, the 10% of restaurants |
| 23 | Forma de Pago | table below |

### Tipo de Bienes y Servicios Comprados (field 3)

| Code | Description | Typical use for Elias |
|---|---|---|
| 1 | Gastos de personal | if some day he subcontracts with a payroll |
| 2 | Gastos por trabajos, suministros y servicios | subcontracting another dev or designer |
| 3 | Arrendamientos | office or coworking rent |
| 4 | Gastos de activos fijos | repair of equipment already recorded |
| 5 | Gastos de representacion | lunch with a client |
| 6 | Otras deducciones admitidas | **hosting, domains, SaaS, internet** |
| 7 | Gastos financieros | bank fees, interest |
| 8 | Gastos extraordinarios | |
| 9 | Compras y gastos que formaran parte del costo de venta | licenses he resells to the client |
| 10 | Adquisiciones de activos | **laptop, monitor, phone** |
| 11 | Gastos de seguros | |

### Tipo de Retencion en ISR (field 17)

| Code | Description |
|---|---|
| 1 | Alquileres |
| 2 | Honorarios por servicios |
| 3 | Otras rentas |
| 4 | Otras rentas (rentas presuntas) |
| 5 | Intereses pagados a personas juridicas residentes |
| 6 | Intereses pagados a personas fisicas residentes |
| 7 | Retencion por proveedores del Estado |
| 8 | Juegos telefonicos |
| 9 | Retenciones subsector de ganaderia de carne bovina |

Elias only fills this in if **he** withholds from someone, which as a natural
person is not his role: natural persons are not withholding agents.

### Forma de Pago (field 23)

| Code | Description |
|---|---|
| 1 | Efectivo |
| 2 | Cheques/Transferencias/Deposito |
| 3 | Tarjeta credito/debito |
| 4 | Compra a credito |
| 5 | Permuta |
| 6 | Notas de credito |
| 7 | Mixto |

---

## Format 607: Ventas de Bienes y Servicios

Columns in order:

| # | Field | Note |
|---|---|---|
| 1 | RNC/Cedula/Pasaporte | of the client |
| 2 | Tipo Identificacion | 1=RNC, 2=Cedula, 3=Pasaporte or tax ID |
| 3 | Numero Comprobante Fiscal | 11 positions |
| 4 | Numero Comprobante Fiscal Modificado | credit/debit notes only |
| 5 | Tipo de Ingreso | table below |
| 6 | Fecha Comprobante | YYYYMMDD |
| 7 | Fecha de Retencion | YYYYMMDD. **Required if there was a withholding** |
| 8 | Monto Facturado | before taxes |
| 9 | ITBIS Facturado | |
| 10 | ITBIS Retenido por Terceros | requires box 7 |
| 11 | ITBIS Percibido | field not enabled yet |
| 12 | Retencion Renta por Terceros | **the 15% the client withheld from him**. Requires box 7 |
| 13 | ISR Percibido | field not enabled yet |
| 14 | Impuesto Selectivo al Consumo | |
| 15 | Otros Impuestos/Tasas | |
| 16 | Monto Propina Legal | |
| 17 | Efectivo | |
| 18 | Cheque/Transferencia/Deposito | |
| 19 | Tarjeta Debito/Credito | |
| 20 | Venta a Credito | |
| 21 | Bonos o Certificados de Regalo | |
| 22 | Permuta | |
| 23 | Otras Formas de Ventas | |

### Tipo de Ingreso (field 5)

| Code | Description |
|---|---|
| 1 | Ingresos por operaciones (No financieros) |
| 2 | Ingresos Financieros |
| 3 | Ingresos Extraordinarios |
| 4 | Ingresos por Arrendamientos |
| 5 | Ingresos por Venta de Activo Depreciable |
| 6 | Otros Ingresos |

All development, design and maintenance work is **code 1**.

### Rules for boxes 17 to 23

- Not all of them are required, only the one that applies.
- The amounts **include taxes**.
- The sum of boxes 17 to 23 must equal the invoice total.

### Consumer invoices

Sales backed by a factura de consumo are reported in the 607 only when they are
**equal to or above RD$250,000** (Norma General 10-18). Below that they go in
the summary sent through the OFV module.
