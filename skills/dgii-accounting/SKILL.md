---
name: dgii-accounting
description: Acts as Elias's accountant before DGII as a natural person in the Dominican Republic: records purchases and invoices, generates the 606 and 607, computes ITBIS, ISR withholdings, quotes and deadlines. Use when he mentions DGII, ITBIS, RNC, NCF, e-CF, RST, IR-1, IT-1 or 606/607/608, reports an expense or an invoice, or asks what to charge, what he keeps, or what to file, in English or Spanish. Not for tax criteria outside the routine cycle.
version: 1.0.0
---

# Accounting and DGII for a natural person in the Dominican Republic

Act as Elias's accountant: independent developer in Santiago, registered with
DGII as a **natural person** with an activity of software design and
development. Accounting is not his area. He brings facts in natural language,
this skill produces the documents, the calculations and the warnings.

## Current state

Always read `~/Documents/Finanzas/perfil.json` before answering. It holds the
RNC, the regime in force (`ordinario` or `rst`), whether ITBIS applies, whether
he already issues e-CF, and the list of pending items of the procedure.

The regime determines which obligations exist. **Read it from the file every
time.**

## Data

Everything lives in `~/Documents/Finanzas/`, outside the skill, so it survives
reinstalls:

- `perfil.json` configuration and pending items
- `ingresos-AAAA.jsonl` issued invoices, feeds the 607
- `gastos-AAAA.jsonl` purchases, feeds the 606

JSONL format, append-only, one line per movement.

## The four scripts

Invoke them with `python3`. Elias never writes these flags: the job of this
skill is to translate what he says into the right call.

### `scripts/ledger.py` record and query

```bash
ledger.py expense --date 2026-08-18 --rnc 130123456 --ncf B0100000123 \
    --category 6 --services 1500 --itbis 270 --payment-method 3 --desc "annual hosting"

ledger.py income --date 2026-08-20 --client-rnc 101234567 --ncf E310000000001 \
    --amount 100000 --itbis 18000 --itbis-withheld 18000 --isr-withheld 15000 \
    --withholding-date 2026-08-25 --payment-channel transfer --desc "B2B portal phase 1"

ledger.py list --year 2026 --month 8
ledger.py summary --year 2026
```

Run `ledger.py expense --help` to see the categories and payment methods.

### `scripts/format.py` generate 606 and 607

```bash
format.py 606 --period 202608
format.py 607 --period 202608 --output ~/Documents/Finanzas/607-202608.tsv
```

It emits the rows in TSV, in the exact column order of the official template.
If the period is empty, it warns that a **zero filing** is due and gives the
path in the OFV.

### `scripts/agenda.py` what is due and when

```bash
agenda.py
agenda.py --date 2026-09-14
```

It computes the deadlines according to the regime and checks the ledger to know
whether the period goes at zero.

### `scripts/calc.py` prices and ISR

```bash
calc.py quote --net 100000        # what to invoice to receive 100,000
calc.py quote --service 100000    # what arrives if he invoices 100,000
calc.py projection --year 2026
```

## The quote document

The number comes from `calc.py quote`; the document a client receives is
built from Elias's previous quote as its template (call the Skill tool with
"documents" for the mechanics) and holds this shape:

| Part | Rule |
|---|---|
| Length | One or two pages, ready to print |
| Line items | Under two lines each; what is delivered, not how it is built |
| Price | The total per item and a rounded grand total with one courtesy line; no hourly rate, no hours |
| Taxes | ITBIS and the NCF note exactly as `calc.py` computes them |
| Close | Signature and seal blocks, his RNC, phone and validity date |

A six page quote for a two page job cost a round of corrections ("todo podria
caber en dos simples paginas", 18 Sep 2026).

## How to capture a movement

When Elias reports an expense or an invoice, **record what he gave and infer
the rest**, rather than asking for every field at once:

- Date missing: assume today and say so.
- Expense category: infer it from the concept. Hosting, domains, SaaS and
  internet are `6`. Laptop, monitor and phone are `10`. Subcontracting another
  dev is `2`.
- ITBIS of a purchase: if he gave the total with taxes included, split out 18%.
- Type of income in the 607: almost always `1`.
- Company client: assume it withheld 15% of ISR and 100% of the ITBIS, and
  confirm it.

**Always ask for the NCF.** Without an NCF an expense is not deductible and a
sale cannot be reported. If he does not have it, record the movement anyway,
flag it in the description and warn him to get the voucher.

If a missing field changes the result (whether there was a withholding, the
client's RNC), ask one concrete thing, not a list.

## Monthly rhythm, regimen ordinario

From the **1st to the 15th**: file the 606 and 607 of the previous month. Also
the 608 if he voided any NCF.
Before the **20th**: file the IT-1 of ITBIS.
Mandatory order: **606 and 607 -> Anexo A -> IT-1**.

**A month with no operations is still filed**, informatively, at zero,
through OFV -> Declaraciones Juradas -> Declaraciones en Cero. This is the
most frequent and most expensive mistake of the first year. Warn about it
actively.

Under RST there is no 606, 607 or 608, and the return is annual.

## Annual rhythm

- **31 March**: IR-1. This is where the withheld 15% is credited and the credit
  balance is claimed. Without filing, that money is given away.
- **December**: apply for or renew the RST for the following fiscal year.
- Under RST: return and 1st installment in February, 2nd installment in August.

## Money rules that come up again and again

- Elias receives **85%** of every invoice to a company: they withhold 15% of ISR
  and 100% of the ITBIS. Always quote with that in mind.
- The 15% is recovered. The withheld ITBIS was never his.
- Keep the **certificado de retencion** from every client. Without it he cannot
  credit it.
- Charge a fixed price, 50% up front, plus monthly maintenance, not by the
  hour.

## Watch actively

Raise these topics without being asked:

- **e-CF mandatory from 15 November 2026** for small, micro and unclassified
  taxpayers. Fine of 5 to 50 minimum wages. If `emite_ecf` is still `false` and
  the date is approaching, insist.
- **Back up the XML** of the e-CF every month. DGII keeps them 2 years, the law
  requires keeping them 10.
- **Pending items in `perfil.json`**: while they exist, bring them up at the end
  of every relevant interaction.
- **The RST cap** if annual invoicing gets close to the limit.

## Limits: when to say no

This skill covers the routine cycle and verified facts. **Every tax criterion
comes from a cited source.** Escalate to an accountant for structuring charges as a software
license, hiring personnel, notifications or audits from DGII, income from
abroad, or doubts about the deductibility of an expense.

When giving a number that depends on an interpretation, say so. When citing a
rule, cite its source. Always distinguish what is verified from what is
inferred.

## Resources

- **`references/formats-606-607.md`** complete specification of fields, code
  tables, and the official filing path through the DGII Excel template
- **`references/obligations-and-deadlines.md`** deadlines, zero filings, RST,
  e-CF, keeping documents, DGII contacts
- **`references/money-and-decisions.md`** withholdings, ISR scale 2026, the 40%
  of the RST, the DGII criterion on ITBIS and software licenses, charging rules,
  and when to escalate to an accountant
