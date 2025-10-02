from wembed_core.constants import HEADERS, IGNORE_EXTENSIONS  # , IGNORE_PARTS, MD_XREF


class TestConstants:
    def test_headers(self):
        assert isinstance(HEADERS, dict)
        assert "User-Agent" in HEADERS

    def test_ignore_extensions(self):
        assert isinstance(IGNORE_EXTENSIONS, set)
        assert ".exe" in IGNORE_EXTENSIONS

    # def test_ignore_parts(self):
    #     assert isinstance(IGNORE_PARTS, set)
    #     assert "node_modules" in IGNORE_PARTS

    # def test_md_xref(self):
    #     assert isinstance(MD_XREF, dict)
    #     assert ".py" in MD_XREF
    #     assert MD_XREF[".py"] == "python"
