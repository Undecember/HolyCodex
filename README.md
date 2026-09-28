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

The bundled `config.toml` selects `gpt-6-sol`, medium reasoning effort, the default service tier, `approval_policy = "never"`, and `sandbox_mode = "danger-full-access"`. These last two settings allow execution without tool approval prompts or filesystem sandbox restrictions. The bundled `AGENTS.md` adds your Git, release, documentation, model routing, verification, and plan approval conventions. Its routing policy uses GPT-6 Astra only when you explicitly request it.

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
