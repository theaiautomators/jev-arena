import io
import zipfile

import pytest

from scripts.report_contents import check_archive, public_documents


def archive(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buffer.getvalue()


def test_export_rejects_editorial_files_in_nested_source_archive():
    nested = archive({'docs/VIDEO-SCRIPT - Copy.md': 'unpublished draft'})
    with pytest.raises(ValueError, match='Non-public'):
        check_archive(archive({'report.html': 'viewer', 'source-snapshot.zip': nested}))
    assert check_archive(archive({'docs/RESULTS.md': 'measurements'})) == ['docs/RESULTS.md']


def test_report_links_remain_local_or_resolve_to_public_sources(tmp_path):
    docs = tmp_path / 'docs'
    docs.mkdir()
    (docs / 'RESULTS.md').write_text('[Methods](METHODS.md#scoring) [Data](data.json)', encoding='utf-8')
    (docs / 'METHODS.md').write_text('Scoring methods', encoding='utf-8')
    (docs / 'data.json').write_text('{}', encoding='utf-8')
    exported = public_documents(tmp_path, ('docs/RESULTS.md', 'docs/data.json'))
    text = exported['docs/RESULTS.md'].decode()
    assert '[Data](data.json)' in text
    assert 'https://github.com/theaiautomators/jev-arena/blob/main/docs/METHODS.md#scoring' in text
    (docs / 'RESULTS.md').write_text('[Draft](VIDEO-SCRIPT.txt)', encoding='utf-8')
    with pytest.raises(ValueError, match='Invalid public'):
        public_documents(tmp_path, ('docs/RESULTS.md',))
