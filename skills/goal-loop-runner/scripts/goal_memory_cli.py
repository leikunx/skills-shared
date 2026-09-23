#!/usr/bin/env python3
"""Compatibility launcher; the private repository owns the memory implementation."""
import json
import os
from pathlib import Path
import runpy
import sys


def resolve():
    home = Path(os.environ.get('GOAL_MEMORY_HOME') or (
        str(Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'GoalMemory') if os.name == 'nt'
        else str(Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'goal-memory')))
    if '--home' in sys.argv:
        home = Path(sys.argv[sys.argv.index('--home') + 1]).expanduser()
    binding = home / 'repository.json'
    if binding.exists():
        return Path(json.loads(binding.read_text())['path'])
    for variable in ('GOAL_MEMORY_REPOSITORY', 'CODEX_SKILLS_PRIVATE_REPOSITORY'):
        if os.environ.get(variable):
            return Path(os.environ[variable]).expanduser()
    raise RuntimeError('Goal Memory now lives in the private skills repository. Use knowledge-setup-goal-memory to clone/pull and run ensure --repository <editable-checkout>. No private records were created in the application checkout.')


def main():
    repository = resolve()
    entry = repository / 'goal-memory/scripts/goal_memory_cli.py'
    if not entry.is_file():
        raise RuntimeError('Bound goal-memory implementation is missing; repair the editable repository binding.')
    sys.path.insert(0, str(entry.parent))
    # Environment discovery alone must also establish the canonical source binding.
    if 'ensure' in sys.argv and '--repository' not in sys.argv:
        sys.argv.extend(['--repository', str(repository)])
    sys.argv[0] = str(entry)
    runpy.run_path(str(entry), run_name='__main__')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
