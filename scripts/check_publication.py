"""Check the tracked publication tree, including links to files ignored locally."""
import subprocess
from pathlib import Path

from scripts.report_contents import MARKDOWN_LINK, relative_target, working_material


def main():
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=root, text=True,
    ).rstrip('\0')
    if not tracked:
        raise SystemExit('No tracked files found; run this check from a Git checkout.')
    paths = set(tracked.split('\0'))
    errors = []
    for name in sorted(paths):
        if working_material(name):
            errors.append('Working material is tracked: ' + name)
        if not name.endswith('.md'):
            continue
        for match in MARKDOWN_LINK.finditer((root / name).read_text(encoding='utf-8')):
            target = relative_target(name, match[2])
            if target is not None and target not in paths:
                errors.append('Link target is not tracked: ' + name + ' -> ' + match[2])
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Public tree checked: {len(paths)} files; no working material or missing documentation targets.')


if __name__ == '__main__':
    main()
