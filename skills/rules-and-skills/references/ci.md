# The agents CI while GitHub blocks Actions

Read this when a PR of `eliasdlc/agents` shows no `local/configuration` or `local/branch-model` status, or when installing the CI on a machine.

GitHub blocks Actions for the private `eliasdlc/agents` repo (no payment method on the account, self-hosted runners included), so the machines are its CI through commit statuses.

## The laptop is the primary CI

`agents-ci.timer` runs `agents ci` every minute. It checks each open PR and the dev and main heads with `bin/ci-check.sh` and posts `local/configuration` and `local/branch-model` as commit statuses, at low priority with 4 GB of memory at most. Install it by copying `systemd/agents-ci.service` and `agents-ci.timer` into `~/.config/systemd/user/` and enabling the timer. Logs are in `~/.cache/agents/ci/logs/`.

## Agentbox is the fallback

Agentbox takes a commit only after it waited 300 s with no status, which means the laptop is asleep. It runs the same `agents-ci.service` and `agents-ci.timer`, plus `systemd/agents-ci-fallback.conf` as the drop-in `~/.config/systemd/user/agents-ci.service.d/fallback.conf`, which adds `--grace 300` and caps memory at 3 GB.
