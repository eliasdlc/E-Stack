# Money: withholdings, prices and decisions

## The two withholdings

When a **legal entity** or a Negocio de Unico Dueno pays a **natural person**
for taxable services:

| Withholding | Rate | Legal basis |
|---|---|---|
| ISR on fees | **15%** | Art. 309 Codigo Tributario, amended by **Ley 30-26** |
| ITBIS | **100% of the invoiced amount** | Withholding of ITBIS from natural persons |

Ley 30-26 was enacted on 18 June 2026 and DGII set it in force from
**1 July 2026**. Before that it was 10%.

Example with a service of RD$100,000:

    Service                     100,000
    ITBIS 18%                    18,000
    Total invoiced              118,000
    - ITBIS withholding 100%    (18,000)
    - ISR withholding 15%       (15,000)
    = Reaches the bank           85,000

**Practical rule: you receive 85%.** Always quote with that number in mind.
To receive X clean, the service must be `X / 0.85`.

Use `scripts/calc.py quote --net <amount>`.

The 15% is **not a lost tax**: it is a payment on account of the annual ISR. It
is credited in the IR-1. In the first years, with low invoicing, the most likely
outcome is that the withholdings **exceed** the real ISR and leave a **credit
balance**. That balance is only recovered by filing the IR-1.

Natural persons are **not withholding agents**. Elias withholds from nobody
when he pays.

## Natural person ISR scale 2026

Resolucion DDG-AR1-2026-00001. Annual exemption: **RD$416,220** (RD$34,685 a month).

| Annual net taxable income | Tax |
|---|---|
| Up to 416,220.00 | 0% |
| 416,220.01 to 624,329.00 | 15% of the excess over 416,220 |
| 624,329.01 to 867,123.00 | 31,216 + 20% of the excess over 624,329 |
| From 867,123.01 | 79,776 + 25% of the excess over 867,123 |

From fiscal year 2027 it changes: exemption of RD$480,000, five brackets and a
top step of 27%. Update `calc.py` when it applies.

## The 40% of the RST

Under RST por Ingresos, natural person: the net taxable income comes from
reducing gross income by a **40% of presumed expenses**, without justifying a
single voucher (Art. 17 Decreto 265-19).

Why it suits a developer so well: the real expenses of this activity are low,
on the order of 10% to 15% of what is invoiced (hosting, domains, internet,
equipment). The RST hands over 40%.

When it does **not** suit: a year with real expenses above 40%, for example if
he hires people, sets up an office or buys expensive equipment. There the
ordinary regime deducts more.

**Honest warning:** the wording of Art. 17 admits two readings of how the 40%
interacts with the annual contributory exemption. `calc.py` applies the direct
reading (base = 60% of the gross, then the scale, which already contains the
exemption in its 0% bracket). The direction of the result is reliable; the exact
number is confirmed by an accountant.

## ITBIS and software: the angle that is worth money

Binding consultations from DGII (G.L. 2653 and 2680, 2021):

- "La venta y arrendamiento de **Licencias de Software** en el mercado local
  **no se encuentran gravadas** con ITBIS, por tratarse de un bien intangible,
  siempre que no implique la transmision de un bien corporal"
  (Art. 4 literal c, Decreto 293-11).
- Support, maintenance, training and instruction inherent to the installation,
  **exclusive to the software sold or leased**, and **invoiced jointly** with
  the license: **also not taxed**, being an ancillary supply to an exempt good
  (Parrafo I, Art. 10, Decreto 293-11).

Practical implication:

| How it is invoiced | Likely treatment |
|---|---|
| "Servicios de desarrollo web" | taxable service, 18% ITBIS |
| **Licencia de uso** of an own system | not taxed |
| Maintenance and support invoiced **together** with the license | not taxed |
| Maintenance on its own, without a license | taxed |

Three warnings that are not skipped:

1. A DGII consultation is issued to a specific taxpayer. It shows the criterion
   of the institution, **it is not authorization of your own**.
2. This is decided by the **reality of the operation**, not by the title on the
   invoice. Invoicing custom development as a "licencia" is simulation.
3. **Confirm with an accountant before structuring anything.**

The legitimate route is to design the business model this way from the start:
own product, the client licenses its use. It also suits commercially, because it
creates recurring income instead of projects that end.

Activity **722001** (suministros de programas de informatica) is registered
precisely so that this figure is defensible.

## Rules for handling the money

- **Never charge by the hour.** Fixed price for a closed, written scope.
- **50% up front**, no exceptions.
- **One page contract**: scope, deliverables, dates, and what it does NOT include.
- **Monthly maintenance in every contract.** That is what turns 5 clients into
  an income and not into 5 finished jobs.
- Keep control of domain and hosting until the final payment.
- Set money aside for the IR-1 if the projection shows a balance to pay.
- A separate bank account for the business. Mixing it with the personal one makes
  it impossible to reconstruct the year.

## When to escalate to an accountant

This skill handles the routine cycle. Escalate when any of these shows up:

- Structuring charges as a software license
- First hire of personnel
- Passing the RST cap
- A notification, requirement or audit from DGII
- Income from abroad or clients outside DR
- Purchase of significant assets or financing
- Any doubt about whether an expense is deductible

Three concrete questions pending with an accountant:
1. With these registered activities, is a monthly IT-1 always required
2. Is it worth structuring as a software license per the DGII consultations
3. Support to apply for or renew the RST in December
