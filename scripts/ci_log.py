"""Print the tail of a log; on GitHub Actions also as one error annotation (the run log itself is not always readable)."""
import os, sys
path, title = sys.argv[1], sys.argv[2]
lines = open(path, errors='replace').read().splitlines()[-60:]
print('\n'.join(lines))
if os.environ.get('GITHUB_ACTIONS'):
    print(f'::error title={title} failed::' + '%0A'.join(l.replace('%', '%25') for l in lines))
