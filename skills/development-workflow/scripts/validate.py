#!/usr/bin/env python3
"""Validate delivery claims, without pretending to authenticate their evidence."""
import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path

STATES = {'Requested', 'Implemented', 'Verified', 'Distributed', 'Accepted'}
CHANNELS = {'test', 'render', 'native', 'device-simulated', 'real-trip', 'nonvisual'}
SHA = re.compile(r'^[0-9a-f]{40}$')
AGENTS_SCOPE = re.compile(r'https://github\.com/eliasdlc/agents/(?:pull/[1-9]\d*|issues/[1-9]\d*|tree/[A-Za-z0-9_./%+-]+)')


def validate(document):
    errors = []
    rows = document.get('requirements') if isinstance(document, dict) else None
    if not isinstance(rows, list) or not rows:
        return ['requirements must be a nonempty list']
    version = document.get('schema_version', 1)
    if type(version) is not int or version not in (1, 2):
        errors.append('unsupported schema_version')
    work_kind = document.get('work_kind', 'product')
    if work_kind not in ('product', 'agent-environment'):
        errors.append('unknown work_kind')
    inventory = document.get('inventory')
    if inventory is None:
        errors.append('inventory is required to detect omitted requirements')
    else:
        actual = [r.get('requirement') for r in rows if isinstance(r, dict)]
        if not isinstance(inventory, list) or sorted(map(str, inventory)) != sorted(map(str, actual)):
            errors.append('inventory differs from requirement rows')
    for index, row in enumerate(rows, 1):
        label = f'row {index}'
        if not isinstance(row, dict):
            errors.append(f'{label}: expected object')
            continue
        def fail(message):
            errors.append(f'{label}: {message}')
        for key in ('requirement', 'decision', 'ticket'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                fail(f'missing {key}')
        ticket = str(row.get('ticket', ''))
        if work_kind == 'agent-environment':
            if not AGENTS_SCOPE.fullmatch(ticket):
                fail('agent environment scope must link to the agents GitHub issue, PR or branch')
        elif not re.match(r'^https://projects\.zoho\.com/\S+$', ticket):
            fail('ticket must link to Zoho')
        state, channel, sha = row.get('state'), row.get('channel'), row.get('sha')
        if not isinstance(state, str) or state not in STATES:
            fail('unknown state')
        if not isinstance(channel, str) or channel not in CHANNELS:
            fail('unknown channel')
        snapshot = channel == 'nonvisual' and row.get('identity_type') == 'sha256' and re.fullmatch(r'[0-9a-f]{64}', str(sha or ''))
        if state != 'Requested' and not (SHA.fullmatch(str(sha or '')) or snapshot):
            fail('claim needs full commit SHA, or identified SHA256 snapshot for nonvisual files')
        evidence = row.get('evidence', [])
        if not isinstance(evidence, list) or any(not isinstance(e, dict) for e in evidence):
            fail('evidence must be a list of objects')
            continue
        current = [e for e in evidence if e.get('sha') == sha and e.get('reference')]
        if isinstance(state, str) and state in STATES - {'Requested'} and not any(e.get('kind') == 'code' for e in current):
            fail('implementation needs code reference at this SHA')
        if isinstance(state, str) and state in {'Verified', 'Accepted'}:
            if isinstance(channel, str) and channel in {'native', 'device-simulated', 'real-trip'}:
                verified = any(e.get('kind') == 'capture' and e.get('channel') == channel
                               and e.get('inspected') is True and isinstance(e.get('receipt'), dict)
                               and e['receipt'].get('sha') == sha
                               and e['receipt'].get('versionName') and e['receipt'].get('versionCode')
                               for e in current)
            else:
                verified = any(e.get('kind') == 'command' and e.get('channel') == channel
                               for e in current)
            if not verified:
                fail('verification missing for required channel and SHA')
        if version == 2 and isinstance(state, str) and state in STATES - {'Requested'}:
            chain = row.get('implementation')
            if not isinstance(chain, dict) or any(not isinstance(chain.get(k), str) or not chain[k].strip() for k in ('producer', 'consumer', 'effect')):
                fail('consumer verification: implementation needs producer, consumer and effect')
            if state in {'Verified', 'Distributed', 'Accepted'}:
                scenario = row.get('verification')
                if not isinstance(scenario, dict) or any(not isinstance(scenario.get(k), str) or not scenario[k].strip() for k in ('action', 'expected', 'observed', 'reference')):
                    fail('consumer verification: scenario needs action, expected, observed and reference')
                elif not any(e.get('kind') in {'command', 'capture'} and e.get('channel') == channel and e.get('reference') == scenario['reference'] for e in current):
                    fail('consumer verification: scenario must reference current evidence on the required channel')
        metadata = evidence + [e['receipt'] for e in evidence if isinstance(e.get('receipt'), dict)]
        for item in metadata:
            for field in ('utc', 'local', 'observedAt'):
                if field in item:
                    try:
                        if dt.datetime.fromisoformat(str(item[field]).replace('Z', '+00:00')).tzinfo is None:
                            fail(f'{field} requires timezone')
                    except ValueError:
                        fail(f'invalid {field}')
            if 'elapsedSeconds' in item and (not isinstance(item['elapsedSeconds'], (int, float)) or item['elapsedSeconds'] < 0):
                fail('invalid duration')
        if state == 'Distributed':
            receipts = [e.get('receipt') for e in current if e.get('kind') == 'receipt']
            if not any(isinstance(r, dict) and r.get('sha') == sha
                       and re.fullmatch(r'https://console\.firebase\.google\.com/project/[^/]+/appdistribution/app/[^/]+/releases/[A-Za-z0-9_-]+', str(r.get('releaseUrl', '')))
                       and (r.get('runUrl') or r.get('receiptPath'))
                       and r.get('versionName') and isinstance(r.get('versionCode'), int)
                       for r in receipts):
                fail('distributed claim needs concrete release receipt at this SHA')
        if state == 'Accepted' and not any(e.get('kind') == 'acceptance' and e.get('message') for e in current):
            fail('acceptance needs owner message reference at this SHA')
    return errors


def render_pr(document):
    """The What was asked list and the Proof table that `agents proof` reads.

    A row with no evidence of its own channel at its SHA prints as Pending, so
    the PR stays red until it is proven rather than looking proven."""
    rows = document['requirements']
    shas = [row['sha'] for row in rows if row.get('sha')]
    stamp = max(set(shas), key=shas.count)[:7] if shas else '<sha7>'
    out = ['## What was asked', '']
    out += [f"- R{i} {row['requirement']}" for i, row in enumerate(rows, 1)]
    out += ['', '## Proof', f'Proof at `{stamp}`', '',
            '| Req | What it proves | Channel | Evidence | Seen |', '|---|---|---|---|---|']
    for i, row in enumerate(rows, 1):
        proven = [e for e in row.get('evidence', [])
                  if e.get('kind') in {'command', 'capture'} and e.get('sha') == row.get('sha')
                  and e.get('channel', row['channel']) == row['channel']]
        if row['state'] in {'Verified', 'Distributed', 'Accepted'} and proven:
            refs = []
            for e in proven:
                ref = e['reference']
                image = e.get('kind') == 'capture' and re.search(r'\.(png|jpe?g|gif|webp)$', ref, re.I)
                refs.append(f'![R{i}]({ref})' if image and ref.startswith('http') else ref)
            evidence = ' '.join(refs).replace('|', '\\|')
            seen = ' '.join(e.get('seen', '') for e in proven).strip()
        else:
            evidence, seen = f"Pending: {row['state']}, needs {row['channel']} evidence at {str(row.get('sha'))[:7]}", ''
        out.append(f"| R{i} | {row['decision']} | `{row['channel']}` | {evidence} | {seen} |")
    return '\n'.join(out)


TOML_CHANNEL = {'test': 'test', 'nonvisual': 'test', 'render': 'render',
                'native': 'device', 'device-simulated': 'device', 'real-trip': 'device'}


def toml_string(text):
    return json.dumps(text, ensure_ascii=False)


def render_toml(document):
    """The rows of .proof/<branch>.toml that CI proves (bin/proof_ci.py), one
    per requirement. `run` is left empty for a test or render row, so the spec
    stays red until the command that runs its test is written in."""
    out = []
    for i, row in enumerate(document['requirements'], 1):
        channel = TOML_CHANNEL[row['channel']]
        out += ['[[row]]', f'req = "R{i}"', f"proves = {toml_string(row['decision'])}"]
        if channel != 'test':
            out.append(f'channel = "{channel}"')
        if channel in ('test', 'render'):
            out.append('run = ""')
        else:
            out.append('pending = "batch"')
        out.append('')
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    parser.add_argument('--render', choices=['pr', 'handoff', 'toml'])
    args = parser.parse_args()
    try:
        document = json.loads(args.ledger.read_text())
        errors = validate(document)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    counts = Counter(row['state'] for row in document['requirements'])
    if args.render == 'pr':
        print(render_pr(document))
        return
    if args.render == 'toml':
        print(render_toml(document), end='')
        return
    if args.render:
        print('## State per requirement\n')
        for row in document['requirements']:
            print(f"- {row['requirement']}: {row['state']} ({row['channel']}); {row.get('sha') or 'no commit'}. {row['ticket']}")
        print('\n## Verified\n')
        for row in document['requirements']:
            for item in row.get('evidence', []):
                if (row['state'] in {'Verified', 'Accepted'} or item.get('kind') == 'receipt') and item.get('sha') == row.get('sha') and item.get('kind') in {'command', 'capture', 'receipt'}:
                    print(f"- {row['requirement']}: {item['reference']}")
        print('\n## Not verified\n')
        for row in document['requirements']:
            if row['state'] not in {'Verified', 'Accepted'}:
                print(f"- {row['requirement']}: channel {row['channel']}; review pending evidence.")
        return
    print(json.dumps({'requirements': len(document['requirements']), 'states': dict(counts)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
