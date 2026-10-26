"""Build a GitHub project site without modifying the Sites source or history."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def project_paths(text, base_path):
    # Rewrite only known site routes, including JS fetches, generated links,
    # pathname comparisons and score-history JSON. Leave external URLs,
    # fragments, SVG markup and JavaScript slash separators intact.
    text = re.sub(
        r'''(["'`])/(assets|data|focus|lan|score|boring|geodata)(?=[/?.#"'`])''',
        lambda m: m[1] + base_path + m[2],
        text,
    )
    text = re.sub(
        r'''((?:href|src)\s*=\s*["'])/(?=[#?"'])''',
        lambda m: m[1] + base_path,
        text,
    )
    # The old geodata route redirects to an anchor on the home page.
    text = text.replace('0;url=/#', '0;url=' + base_path + '#')
    # This shared illustration is also referenced by nested source pages.
    text = text.replace('src="baninfo-jarnvagsnat.png"',
                        'src="' + base_path + 'baninfo-jarnvagsnat.png"')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-path', default='/statistik-/')
    args = parser.parse_args()
    if not re.fullmatch(r'/(?:[A-Za-z0-9_-]+/)+', args.base_path):
        parser.error('--base-path must be a project path such as /statistik-/')
    parent = ROOT / 'public-build'
    parent.mkdir(exist_ok=True)
    output = parent / 'github-pages'
    with tempfile.TemporaryDirectory(prefix='pages-', dir=parent) as temporary:
        stage = Path(temporary)
        for name in ('data', 'dist'):
            shutil.copytree(ROOT / name, stage / name)
        subprocess.run([sys.executable, 'data/prepare-public.py'], cwd=stage, check=True)
        build = stage / 'build'
        changed = 0
        for file in build.rglob('*'):
            if file.suffix not in ('.html', '.js', '.css', '.json'):
                continue
            original = file.read_text(encoding='utf-8')
            rewritten = project_paths(original, args.base_path)
            if rewritten != original:
                file.write_text(rewritten, encoding='utf-8')
                changed += 1
        (build / '.nojekyll').touch()
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(build), output)
    print(f'GitHub Pages: {output}, base {args.base_path}, {changed} adapted files')


if __name__ == '__main__':
    main()
