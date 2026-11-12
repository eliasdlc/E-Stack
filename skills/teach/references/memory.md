# Memory of the session

A session is a markdown file in `~/Documents/Universidad/Aprendizaje/sessions/`. It can be
opened, read and corrected by hand. The file is the state: there is no service
and no database behind it.

```
# Topic
> Learning session - v1 - <sessionId>
## Now          what to attend to
## Why          why this step matters
## Next         the next action, a single one
## Checkpoint   the state in JSON, which is what gets resumed
## Log          what happened, and it only grows
```

The map, the plan, the checks and what is parked live inside the log as marked
entries. The script reads them for you: **do not parse the file by hand and do
not touch it with `Edit` or `Write`.**

## The commands

They all spit JSON. A failure goes out on stderr with code 1 and explains what
is missing.

```bash
S=~/.claude/skills/teach/scripts/session.py
```

| Command | When |
|---|---|
| `python3 $S list` | The first thing of every session, always |
| `python3 $S read --session <topic>` | On resuming, and whenever you doubt where you were |
| `python3 $S open --topic ...` | After the probe, once you know what comes first |
| `python3 $S save --session ...` | On closing a step, and always before he leaves |
| `python3 $S record --session <t> --type probe\|teach\|note\|parked` | Every probe, every explanation, every claim, every parked idea |
| `python3 $S map --session <t>` | Whenever what you know about him changes |
| `python3 $S plan --session <t> --state proposed\|approved` | On proposing and on approving |
| `python3 $S check --session <t> ...` | On every check, with the literal answer |
| `python3 $S master --session <t> --node <n>` | On closing a node |
| `python3 $S export --session <t>` | If he wants the whole document |

`open` and `save` ask for the complete state:

```bash
python3 $S open --topic "Logistic regression" \
  --now "Why a straight line does not work for a probability" \
  --why "It is exactly what the sigmoid comes to fix" \
  --node "odds" --understood "He knows what a slope is" \
  --next "Turn three probabilities into odds by hand" --minutes 15 \
  --open-question "why the log and not another function?"
```

`map`, `plan` and `record` read from stdin with `-`, which is the comfortable
way for long content:

```bash
echo '[{"id":"odds","name":"Odds","state":"shaky","evidence":"Got the definition right and failed the use"}]' \
  | python3 $S map --session logistic-regression

echo '[{"id":"odds","title":"Probability as a ratio","dependsOn":["linear"],"state":"pending"}]' \
  | python3 $S plan --session logistic-regression --goal "Understand the sigmoid" --state proposed
```

A check is recorded whole, with what he actually answered:

```bash
python3 $S check --session logistic-regression --node odds --type explain \
  --question "why a ratio and not a fraction?" \
  --answer "because it compares what happens against what does not" \
  --confidence think-so --verdict correct \
  --note "He still has to connect it with the infinite range"
```

## Rhythm of writing

- `record` goes as things happen. It is the memory of what has already been
  tried: without it, in the next session you repeat the example that already
  failed.
- `save` goes when a step ends, not on every sentence.
- The checkpoint has a single `next` action. If you write two, choose.
- `understood` is written with his words, not with yours.

## Resuming

`read` gives you the checkpoint, the map, the plan, the next unblocked node and
what is missing to close the current node. With that:

1. One line of where you were.
2. The question that was left open, if any was left.
3. The next action, exactly as it is in the checkpoint.

No summarizing the whole previous session, and no probing again what is already
in the map.

## If something breaks

The file is his and he can touch it. If a command complains about the format,
tell him which section is wrong and where the file is. Do not fix it behind his
back without telling him.
