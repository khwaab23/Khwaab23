"""Build a GitHub-profile NeetCode SVG from a synced submissions repo."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

REPO = os.environ.get('NEETCODE_REPO', 'khwaab23/neetcode-submissions')
URL = f'https://api.github.com/repos/{REPO}/git/trees/main?recursive=1'
HEADERS = {'Accept': 'application/vnd.github+json', 'User-Agent': 'neetcode-profile-stats'}
token = os.environ.get('GITHUB_TOKEN')
if token:
    HEADERS['Authorization'] = f'Bearer {token}'
with urlopen(Request(URL, headers=HEADERS), timeout=30) as resp:
    payload = json.load(resp)
if payload.get('truncated'):
    raise RuntimeError('GitHub returned a truncated tree; refusing to publish incomplete counts')

extensions = ('.py', '.cpp', '.cc', '.c', '.java', '.js', '.ts', '.go', '.rs', '.cs', '.kt', '.swift', '.sql')
files = [item['path'] for item in payload['tree'] if item['type'] == 'blob'
         and Path(item['path']).name.startswith('submission-')
         and item['path'].lower().endswith(extensions)]
problems = {str(Path(path).parent) for path in files}
count = len(files)
unique = len(problems)
# Scale relative bar lengths to the highest value, not to a fictional goal.
width = 520
left = 160
bar_w = 270
bar1 = round(bar_w * (unique / max(count, unique, 1)))
bar2 = round(bar_w * (count / max(count, unique, 1)))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="210" viewBox="0 0 {width} 210" role="img" aria-label="NeetCode: {unique} unique problems and {count} synced submissions">
<rect width="520" height="210" rx="14" fill="#0d1117" stroke="#30363d"/>
<text x="26" y="38" font-family="Arial,sans-serif" font-size="19" font-weight="700" fill="#e6edf3">NeetCode Progress</text>
<text x="26" y="62" font-family="Arial,sans-serif" font-size="11" fill="#8b949e">Synced GitHub solutions · updated automatically</text>
<text x="26" y="106" font-family="Arial,sans-serif" font-size="13" fill="#c9d1d9">Unique problems</text>
<rect x="{left}" y="90" width="{bar_w}" height="15" rx="6" fill="#21262d"/>
<rect x="{left}" y="90" width="{bar1}" height="15" rx="6" fill="#a371f7"/>
<text x="463" y="103" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#e6edf3" text-anchor="end">{unique}</text>
<text x="26" y="150" font-family="Arial,sans-serif" font-size="13" fill="#c9d1d9">Submissions</text>
<rect x="{left}" y="134" width="{bar_w}" height="15" rx="6" fill="#21262d"/>
<rect x="{left}" y="134" width="{bar2}" height="15" rx="6" fill="#3fb950"/>
<text x="463" y="147" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#e6edf3" text-anchor="end">{count}</text>
<text x="26" y="186" font-family="Arial,sans-serif" font-size="11" fill="#8b949e">Counts synced solution files, not accepted-status verification.</text>
</svg>'''
out = Path('assets/neetcode-stats.svg')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(svg, encoding='utf-8')
print(f'{unique} unique problem folders; {count} submission files. Saved {out}.')
