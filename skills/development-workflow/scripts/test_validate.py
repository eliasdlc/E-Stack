import unittest
from validate import render_pr, render_toml, validate

SHA = 'a' * 40


class ClaimsTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(requirement='No native shadow', decision='Turn off the model shadow',
                        ticket='https://projects.zoho.com/portal/x#task/1', channel='native',
                        state='Implemented', sha=SHA,
                        evidence=[dict(kind='code', sha=SHA, reference='commit:file:line')])

    def check(self, row):
        return validate({'inventory': [row['requirement']], 'requirements': [row]})

    def test_implementation_is_not_native_verification(self):
        self.assertEqual(self.check(self.row), [])
        self.row['state'] = 'Verified'
        self.row['evidence'].append(dict(kind='command', channel='render', sha=SHA, reference='flutter test: 1544 pass'))
        self.assertTrue(self.check(self.row))

    def test_matching_inspected_native_capture_verifies(self):
        self.row['state'] = 'Verified'
        self.row['evidence'].append(dict(kind='capture', channel='native', sha=SHA, reference='/capture.png', inspected=True, receipt=dict(sha=SHA, versionName='review', versionCode=60)))
        self.assertEqual(self.check(self.row), [])
        self.row['evidence'][-1]['sha'] = 'b' * 40
        self.assertTrue(self.check(self.row))

    def test_simulation_does_not_verify_real_trip(self):
        self.row.update(state='Verified', channel='real-trip')
        self.row['evidence'].append(dict(kind='capture', channel='device-simulated', sha=SHA, reference='/capture.png', inspected=True, receipt=dict(sha=SHA, versionName='review', versionCode=60)))
        self.assertTrue(self.check(self.row))

    def test_distribution_is_not_acceptance(self):
        self.row['state'] = 'Distributed'
        self.row['evidence'].append(dict(kind='receipt', sha=SHA, reference='run', receipt=dict(sha=SHA, versionName='review', versionCode=60, runUrl='https://github.com/a/b/actions/runs/1', releaseUrl='https://console.firebase.google.com/project/x/appdistribution/app/android:x/releases/abc')))
        self.assertEqual(self.check(self.row), [])
        self.row['state'] = 'Accepted'
        self.assertTrue(self.check(self.row))

    def test_nonvisual_work_can_be_accepted_without_build(self):
        self.row.update(state='Accepted', channel='nonvisual')
        self.row['evidence'] += [dict(kind='command', sha=SHA, channel='nonvisual', reference='python3 -m unittest: 7 OK'), dict(kind='acceptance', sha=SHA, reference='thread:message', message='green')]
        self.assertEqual(self.check(self.row), [])

    def test_config_without_git_uses_explicit_sha256_snapshot(self):
        self.row.update(channel='nonvisual', identity_type='sha256', sha='b' * 64)
        self.row['evidence'][0]['sha'] = 'b' * 64
        self.assertEqual(self.check(self.row), [])
        self.row['channel'] = 'native'
        self.assertTrue(self.check(self.row))

    def test_missing_inventory_row_is_rejected(self):
        self.assertTrue(validate({'inventory': ['Missing'], 'requirements': [self.row]}))

    def test_bad_time_and_negative_duration_are_rejected(self):
        self.row['evidence'].append(dict(kind='command', sha=SHA, reference='test', utc='2026-09-14T21:00:00', elapsedSeconds=-1))
        self.assertEqual(len(self.check(self.row)), 2)
        self.row['evidence'][-1] = dict(receipt=self.row['evidence'][-1])
        self.assertEqual(len(self.check(self.row)), 2)

    def test_malformed_rows_fail_closed(self):
        for document in (None, {}, {'requirements': []}, {'requirements': [None]}, {'requirements': [{'evidence': [None]}]}):
            self.assertTrue(validate(document))


class ConsumerVerificationTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(requirement='Delegation result is verified', decision='Verify consumer output',
                        ticket='https://github.com/eliasdlc/agents/tree/feat/adaptive-agent-workflow',
                        channel='nonvisual', state='Verified', sha=SHA,
                        implementation=dict(producer='Child receipt', consumer='Principal acceptance check', effect='Result inspected'),
                        verification=dict(action='Read result and run acceptance check', expected='Requested result passes',
                                          observed='Acceptance check passes', reference='acceptance check: PASS'),
                        evidence=[dict(kind='code', sha=SHA, reference='bin/delegation.py'),
                                  dict(kind='command', sha=SHA, channel='nonvisual', reference='acceptance check: PASS')])
        self.document = dict(schema_version=2, work_kind='agent-environment',
                             inventory=[self.row['requirement']], requirements=[self.row])

    def test_complete_consumer_chain_and_scenario_pass(self):
        self.assertEqual(validate(self.document), [])

    def test_missing_consumer_fails_and_repaired_passes(self):
        consumer = self.row['implementation'].pop('consumer')
        self.assertIn('consumer verification: implementation needs producer, consumer and effect', '\n'.join(validate(self.document)))
        self.row['implementation']['consumer'] = consumer
        self.assertEqual(validate(self.document), [])

    def test_worker_completion_cannot_replace_consumer_scenario(self):
        self.row['verification'] = dict(observed='Worker completed')
        self.assertIn('consumer verification: scenario needs action, expected, observed and reference', '\n'.join(validate(self.document)))

    def test_scenario_must_match_current_channel_evidence(self):
        for field, value in (('sha', 'b' * 40), ('channel', 'render'), ('reference', 'different result')):
            with self.subTest(field=field):
                evidence = dict(self.row['evidence'][1])
                self.row['evidence'][1][field] = value
                self.assertTrue(validate(self.document))
                self.row['evidence'][1] = evidence

    def test_old_ledgers_keep_their_explicit_compatibility(self):
        self.document.pop('schema_version')
        self.row.pop('implementation')
        self.row.pop('verification')
        self.assertEqual(validate(self.document), [])

    def test_invalid_schema_version_fails(self):
        for version in (True, 0, 3, '2', None):
            self.document['schema_version'] = version
            self.assertIn('unsupported schema_version', validate(self.document))

    def test_github_scope_exception_is_only_for_agents_work(self):
        for ticket in ('https://github.com/eliasdlc/agents/pull/70', 'https://github.com/eliasdlc/agents/issues/1'):
            self.row['ticket'] = ticket
            self.assertEqual(validate(self.document), [])
        self.document['work_kind'] = 'product'
        self.assertIn('ticket must link to Zoho', '\n'.join(validate(self.document)))
        self.document['work_kind'] = 'agent-environment'
        for ticket in ('https://github.com/eliasdlc/kino/pull/1', 'https://github.com/eliasdlc/agents.evil/pull/1', 'https://github.com/eliasdlc/agents/pull/1?x=2'):
            self.row['ticket'] = ticket
            self.assertTrue(validate(self.document))


class RenderTests(unittest.TestCase):
    def test_pr_render_is_what_agents_proof_reads(self):
        row = dict(requirement='Export row in Settings', decision='Export row renders', channel='render',
                   ticket='https://projects.zoho.com/portal/x#task/1', state='Verified', sha=SHA,
                   evidence=[dict(kind='capture', channel='render', sha=SHA, inspected=True,
                                  reference='https://raw.githubusercontent.com/eliasdlc/evidencia/main/w/b/aaaaaaa/r1.png',
                                  seen='Row under Account at 393x852')])
        text = render_pr({'inventory': [row['requirement']], 'requirements': [row]})
        self.assertIn('- R1 Export row in Settings', text)
        self.assertIn('Proof at `aaaaaaa`', text)
        self.assertIn('| R1 | Export row renders | `render` | ![R1](https://', text)
        row['state'] = 'Implemented'
        self.assertIn('Pending: Implemented', render_pr({'inventory': [], 'requirements': [row]}))

    def test_toml_render_is_the_spec_ci_proves(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'bin'))
        import proof_ci
        rows = [dict(requirement=r, decision=f'{r} "quoted"', channel=c, ticket='t', state='Implemented', sha=SHA)
                for r, c in (('a', 'test'), ('b', 'render'), ('c', 'native'), ('d', 'nonvisual'))]
        text = render_toml({'requirements': rows})
        self.assertIn('[[row]]\nreq = "R3"\nproves = "c \\"quoted\\""\nchannel = "device"\npending = "batch"', text)
        # Empty run commands keep the spec red until each is written in.
        problems = proof_ci.load_spec(text)[1]
        self.assertEqual(sorted({req for req, _, _ in problems}), ['R1', 'R2', 'R4'])
        filled = text.replace('run = ""', 'run = "python3 -m unittest tests.test_x"', 1)
        self.assertNotIn('R1', {req for req, _, _ in proof_ci.load_spec(filled)[1]})


if __name__ == '__main__':
    unittest.main()
