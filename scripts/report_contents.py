"""Explicit public report contents and checks against accidentally bundling drafts."""
import fnmatch
import io
import posixpath
import re
import zipfile
from pathlib import PurePosixPath
from urllib.parse import quote, unquote, urlsplit


LOCAL_ONLY = (
    'PLAN.md', 'RESEARCH.md', 'docs/ABCD-ASSESSMENT-QUEUE.md',
    'docs/ADVERSARIAL-REVIEW.md', 'docs/DESIGN.md',
    'docs/LESSON-SANITY-CHECK.md', 'docs/PUBLISHING.md',
    'docs/VIDEO-SCRIPT*', 'docs/VIDEO-SPINE.md', 'docs/VIDEO-ANALYSIS.md',
    'docs/archive/*', 'docs/evidence/abcd-feasibility.md',
    'docs/evidence/demo-summary.json', 'docs/evidence/full-summary.json',
)
FULL_DOCS = (
    'docs/RESULTS.md', 'docs/ANALYSIS.md', 'docs/BUILDER-TAKEAWAYS.md',
    'docs/WHY-ARENA.md', 'docs/VERIFICATION.md', 'docs/VIDEO-EVALUATION-V2.md',
    'docs/IMPLEMENTATION.md', 'docs/REFERENCE-CAUTIONS.md',
    'docs/reference-cautions.json',
    'docs/evidence/full-v2-summary.json', 'docs/evidence/full-v2-supplement.json',
    'docs/evidence/video-task-analysis.json', 'docs/evidence/video-findings.json',
    'docs/evidence/model-guide.json', 'docs/evidence/builder-task-breakdown.json',
    'docs/evidence/abcd-dashboard-data.json', 'docs/evidence/winnow-memory.json',
    'docs/evidence/ASTRA-V2-REVIEW.md', 'docs/evidence/winnow-option-limit.md',
    'docs/evidence/clm-preflight-recovery.md', 'docs/evidence/parallel-audit-amendment.md',
)
ABCD_DOCS = (
    'docs/ABCD-RESULTS.md', 'docs/ABCD-PROTOCOL.md',
    'docs/evidence/ABCD-AUDIT-REVIEW.md', 'docs/evidence/ASTRA-ABCD-REVIEW.md',
    'docs/evidence/abcd-retrieval-correction.json',
)
MARKDOWN_LINK = re.compile(r'(!?\[[^\]\n]*\]\()([^\s)]+)(\))')


def working_material(path):
    normalized = path.replace('\\', '/').lstrip('./')
    return any(fnmatch.fnmatchcase(normalized, pattern) for pattern in LOCAL_ONLY)


def relative_target(source, href):
    url = urlsplit(href)
    if url.scheme or url.netloc or not url.path:
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(url.path)))


def public_documents(root, names):
    """Keep included links local; link other public documentation to its source."""
    included = set(names)
    output = {}
    for name in names:
        if working_material(name):
            raise ValueError('Working material requested for public report: ' + name)
        data = (root / name).read_bytes()
        if name.endswith('.md'):
            def link(match):
                href = match[2]
                target = relative_target(name, href)
                if target is None or target in included:
                    return match[0]
                if target.startswith('../') or working_material(target):
                    raise ValueError('Invalid public documentation link: ' + name + ' -> ' + href)
                if not (root / target).is_file():
                    raise ValueError('Missing documentation link: ' + name + ' -> ' + href)
                anchor = urlsplit(href).fragment
                remote = 'https://github.com/theaiautomators/jev-arena/blob/main/' + quote(target)
                return match[1] + remote + ('#' + anchor if anchor else '') + match[3]
            data = MARKDOWN_LINK.sub(link, data.decode('utf-8')).encode('utf-8')
        output[name] = data
    return output


def check_archive(data):
    """Reject editorial files even when accidentally added through a nested ZIP."""
    checked = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            path = PurePosixPath(name.replace('\\', '/'))
            if path.is_absolute() or '..' in path.parts or working_material(name):
                raise ValueError('Non-public archive member: ' + name)
            if name.endswith('/'):
                continue
            checked.append(name)
            if name.endswith('.zip'):
                checked.extend(name + '/' + child for child in check_archive(archive.read(name)))
    return checked
