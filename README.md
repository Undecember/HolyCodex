# Portable Codex setup

Copy this whole directory to another device, install Python 3.11 or newer, and run:

```sh
python3 init.py --dry-run
python3 init.py
```

On Windows, use `py -3` instead of `python3`. Run these commands from this directory, or provide the full path to `init.py`.

The script installs the bundled preferences and working instructions into `$CODEX_HOME`, if set, or `~/.codex`. You can choose another destination:

```sh
python3 init.py --codex-home /path/to/codex-home
```

The bundled `config.toml` selects `gpt-6.1-sol`, medium reasoning effort, the default service tier, `approval_policy = "never"`, and `sandbox_mode = "danger-full-access"`. These last two settings allow execution without tool approval prompts or filesystem sandbox restrictions. The bundled `AGENTS.md` adds your Git, release, documentation, model routing, verification, and plan approval conventions.

The routing policy uses `gpt-6-luna` with max reasoning effort for scouting, the first implementation attempt on every task (including complex and high-risk work), localized repairs, and routine and integration test generation. `gpt-6.1-sol` with medium reasoning effort handles orchestration, architecture, independent review, and implementation retries when review finds a material quality shortfall or conceptual capability gap. `gpt-6-astra` with low reasoning effort handles defined architectural escalation and critical review; high-risk work keeps Sol's architecture and safety guidance and requires Astra review before consequential changes are applied. Deterministic verification and independent review follow implementation. If Luna is unavailable, the runtime limitation and any explicit fallback must be reported. Cost decisions consider the expected whole-task cost and risk; a price multiplier is not a retry quota.

The bundled instructions require progress messages to show each subagent's task, exact model identifier, and reasoning effort when spawning and waiting. Unconfirmed settings are labeled as requested, and failures, fallbacks, or assignment changes are reported explicitly. This controls assistant messages; it does not configure model labels in the client's built-in subagent cards.

Running `python3 init.py` installs this worktree preference globally for the user, so it applies across projects in new Codex sessions. The worktree instructions default to `<project-root>/.worktrees/` in each repository and require Git to ignore that directory before use. This applies to agent-created Git worktrees; it does not configure the Codex app’s built-in worktree manager.

Existing unrelated TOML settings are preserved. Existing files that change are backed up before replacement. The destination `AGENTS.md` is replaced as a whole with the bundled version; its previous contents are kept in a backup. Running the script again with the same settings makes no changes.

This directory is a snapshot. Edit its templates to change future installations, or refresh `AGENTS.md` from your preferred source before copying it to another device.

The script does not install Codex, authenticate an account, or transfer credentials, sessions, skills, plugins, or trusted project paths. Existing destination trust entries remain intact. Referenced skills and model names require availability on the destination installation; `AGENTS.md` alone does not install skills or change the model of an already running session. Start a new Codex session after setup.

To undo an installation over existing files, restore the backup paths printed by the script. For a fresh installation, remove only the files created by the script.

## Parallel SDD skill

The bundled `skills/parallel-sdd` skill inspects task dependencies, generates a dependency graph, and executes waves of independent tasks concurrently in isolated worktrees. For dependencies `A → C`, `B → C`, and `D → E`, the waves are `(A, B, D)` followed by `(C, E)`.

Install the skill separately from `init.py`, running this command from this directory in Bash or PowerShell (use `py -3` on Windows):

```sh
python3 -c 'import os, pathlib, shutil; destination = pathlib.Path(os.environ.get("CODEX_HOME") or pathlib.Path.home() / ".codex").expanduser() / "skills" / "parallel-sdd"; shutil.copytree("skills/parallel-sdd", destination); print(destination)'
```

This command refuses to overwrite an existing skill directory. If replacing an installation, move the old directory to a backup outside the skills directory first. To uninstall, remove only the installed `parallel-sdd` directory.

Invoke `$parallel-sdd` with an implementation plan. If it is not listed, start a new session. The skill is self-contained; the other Superpowers skills referenced by `AGENTS.md` are not bundled.

## Release notes

### v0.2.1

- Routes the first implementation attempt for every task, including complex and high-risk work, to `gpt-6-luna` at max reasoning effort. Verification and independent review guide follow-up: Luna handles localized revisions, while `gpt-6.1-sol` at medium reasoning effort retries when review finds a material quality or capability gap. High-risk work retains Sol-defined architecture and requires `gpt-6-astra` critical review before consequential changes.
- Removes the root fast-path implementation bypass. Fast-path work still uses Luna first, deterministic verification, and independent review.
- Bases routing on expected whole-task cost and risk, including retries, review, tool use, latency, and defect risk; price multipliers and turn counts are not retry quotas.
- Requires reporting when Luna is unavailable and identifying any runtime fallback. The root session model and configuration, and installer behavior, are unchanged.
