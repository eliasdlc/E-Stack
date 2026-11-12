# T3 launcher details, discovery and costs

Read when launching or watching a T3 child, choosing among non-Claude models, or estimating cost.

## T3 launcher details

- Status: `t3_thread_list` with statuses running, waiting, starting and queued (pass `projectId` for another project), `t3_thread_read` for one thread, `task_status` for a delegated task.
- Steering: `t3_thread_send` (steer or queue) and `t3_thread_interrupt` change a running child only when Elias asks for that change.
- A new thread: read it with `t3_thread_read` until preparation ends, then give him its title. `agents t3-launch` takes the same project and worktree flags on either host; `--host auto` places the thread where more memory is free after each machine's reserve, and says which and why, because the laptop shares its memory with his desktop.
- Fork: `t3_thread_fork` from `latest_stable`, or a run or checkpoint id, when the context is nearly full or a second line of work starts from this point. A clean context, or the other machine, takes a handoff instead.
- Depth: a prompt restriction is not an enforced depth cap. Require children to return to the principal for additional work, and monitor descendant status.
- Review: the principal inspects findings, changed files, actual commands, limitations and observed identity, verifies against sources and integrates authorized changes. An independent reviewer is `delivery-reviewer`, or `delegate_task` on another provider.
- Scope: the brief carries the orchestration items from the start of the run; new scope from the child or the orchestrator becomes a new PR or ticket.

## Discovery

- In T3 call `orchestrator_capabilities` and choose a provider with `canRunChildTask: true` (and `canRunCrossProviderChildTask: true` for another provider) and the exact advertised model.
- A cached or advertised identity stays unverified account availability until execution succeeds. A provider's manifest, announcement or self-description is weaker evidence than the live runnable catalog and the observed runtime identity.
- Choose any current runnable model that fits the required tools, context, permissions and task, using provider capability descriptions and current version information.
- Outside the Claude split there is no permanent model ordering or fixed assignment of models to writing, visuals or code. Astra is excluded from automatic selection; an explicit user selection can use it.
- Set effort explicitly from the chosen harness's advertised options. Default service tier and ordinary subscription execution apply; paid fallback, fast mode or increased-usage options need the user's authorization.
- `completed` is the child's lifecycle report. The principal decides whether it satisfied the bounded task; Elias's acceptance of the delivery is separate.

## Costs

- Estimate coordination and verification costs before a call.
- A T3 wait timeout does not terminate work: cancel explicitly at the deadline and confirm terminal status. Retain partial results and diagnostic evidence.
