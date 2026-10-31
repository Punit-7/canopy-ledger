# tests/test_gfw.py
from ledger.gfw import GFW, version_key


def test_version_order():
    vs = ["v20260424", "v202204.2", "v20250515", "v202104", "v202204"]
    assert sorted(vs, key=version_key) == ["v202104", "v202204", "v202204.2", "v20250515", "v20260424"]


class FakeResponse:
    status_code = 200

    def __init__(self, body: bytes):
        self.body = body

    def iter_content(self, chunk_size):
        for i in range(0, len(self.body), 7):  # odd chunk size on purpose
            yield self.body[i : i + 7]


def test_download_counts_rows(tmp_path, monkeypatch):
    client = GFW("https://example.org", "key")
    body = b"a,b\n1,2\n3,4\n5,6"  # no trailing newline
    monkeypatch.setattr(client, "_get", lambda *a, **k: FakeResponse(body))
    dest = tmp_path / "out.csv"
    assert client.download_csv("d", "v1", "select 1", dest) == 3
    assert dest.read_bytes() == body
