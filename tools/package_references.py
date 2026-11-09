#!/usr/bin/env python3
"""Validate the model reference pack; optionally build both release ZIPs (stdlib only)."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import argparse
import csv
import hashlib
import json
import re
import struct
import zipfile
import zlib

REPO = Path(__file__).resolve().parents[1]
PACK = REPO / 'references' / 'models'
APPROVED = REPO / 'docs'


def png_size(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG signature: {path}'
    offset, size, ended = 8, None, False
    while offset < len(data):
        assert offset + 12 <= len(data), f'Truncated PNG: {path}'
        length = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 8 + length
        assert end + 4 <= len(data), f'Truncated PNG chunk: {path}'
        actual = zlib.crc32(data[offset + 4:end]) & 0xffffffff
        expected = struct.unpack_from('>I', data, end)[0]
        assert actual == expected, f'PNG CRC mismatch: {path}'
        if kind == b'IHDR':
            size = struct.unpack_from('>II', data, offset + 8)
        if kind == b'IEND':
            ended = True
            break
        offset = end + 4
    assert ended and size, f'Incomplete PNG: {path}'
    return size


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_links():
    for path in REPO.rglob('*.md'):
        if '.git' in path.parts or 'build' in path.parts:
            continue
        for ref in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' in ref or ref.startswith('#'):
                continue
            target = ref.split('#', 1)[0]
            assert (path.parent / target).is_file(), f'Broken link in {path}: {ref}'

    class GalleryLinks(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key in ('href', 'src'):
                    assert not value.startswith(('http:', 'https:', '//')), value
                    assert (PACK / value).is_file(), f'Broken gallery link: {value}'

    GalleryLinks().feed((PACK / 'GALLERY.html').read_text(encoding='utf-8'))


def update_checksums():
    lines = []
    for path in sorted(PACK.rglob('*')):
        if path.is_file() and path.name != 'SHA256SUMS.txt':
            lines.append(f'{sha256(path)}  {path.relative_to(PACK).as_posix()}')
    (PACK / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def validate():
    assets = json.loads((PACK / 'ASSET_MANIFEST.json').read_text(encoding='utf-8'))
    assert len(assets) == 31
    assert len({asset['id'] for asset in assets}) == 31
    assert sum(asset['rig'] for asset in assets) == 6
    assert Counter(asset['priority'] for asset in assets) == {'P0': 12, 'P1': 15, 'P2': 4}
    hashes = set()
    briefs = (PACK / '05_ASSET_BRIEFS.md').read_text(encoding='utf-8')
    for asset in assets:
        path = PACK / asset['reference']
        assert path.is_file(), f'Missing reference: {path}'
        width, height = png_size(path)
        assert width >= 1500 and height >= 800, (asset['id'], width, height)
        assert briefs.count('## ' + asset['id'] + ' —') == 1
        hashes.add(sha256(path))
    assert len(hashes) == 31, 'Asset images unexpectedly duplicated'
    for path in (PACK / '06_approved_art').glob('*.png'):
        png_size(path)
    with (PACK / '01_ASSET_LIST.csv').open(encoding='utf-8-sig', newline='') as stream:
        assert len(list(csv.reader(stream, delimiter=';'))) == 32
    for line in (PACK / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected, name = line.split('  ', 1)
        assert sha256(PACK / name) == expected, f'Stale checksum: {name}; run without --check to rebuild'
    validate_links()
    print('OK: 31 unique model references, 6 character sheets, PNG CRCs, manifest, checksums and local links.')


def build():
    output = REPO / 'build' / 'release'
    output.mkdir(parents=True, exist_ok=True)
    model_zip = output / 'BESOGON_3D_MODEL_REFERENCES.zip'
    with zipfile.ZipFile(model_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(PACK.rglob('*')):
            if path.is_file():
                archive.write(path, 'BESOGON_3D_REFERENCES/' + path.relative_to(PACK).as_posix())
    visual_zip = output / 'BESOGON_APPROVED_VISUAL.zip'
    with zipfile.ZipFile(visual_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(APPROVED / 'APPROVED_VISUAL.md', 'BESOGON_APPROVED_VISUAL.md')
        for path in sorted((APPROVED / 'visual').glob('*.png')):
            archive.write(path, 'visual/' + path.name)
    for path in [model_zip, visual_zip]:
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
        print(f'Built {path.relative_to(REPO)} ({path.stat().st_size / 1024 ** 2:.1f} MiB)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate only; do not update checksums or build ZIPs')
    args = parser.parse_args()
    if not args.check:
        update_checksums()
    validate()
    if not args.check:
        build()


if __name__ == '__main__':
    main()
