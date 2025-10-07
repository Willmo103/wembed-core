from wembed_core.constants import (
    HEADERS,
    IGNORE_EXTENSIONS,
    IGNORE_PARTS,
    MD_XREF,
    STD_LIB_MODULES,
)


class TestConstants:
    def test_headers(self):
        assert isinstance(HEADERS, dict)
        assert "User-Agent" in HEADERS

    def test_ignore_extensions(self):
        assert isinstance(IGNORE_EXTENSIONS, set)
        assert ".exe" in IGNORE_EXTENSIONS

    def test_ignore_parts(self):
        assert isinstance(IGNORE_PARTS, set)
        assert "node_modules" in IGNORE_PARTS

    def test_md_xref(self):
        assert isinstance(MD_XREF, dict)
        assert ".py" in MD_XREF
        assert MD_XREF[".py"] == "python"

    def test_std_lib_modules_is_a_set(self):
        assert isinstance(STD_LIB_MODULES, set)

    def test_std_lib_modules_is_not_empty(self):
        assert len(STD_LIB_MODULES) > 0

    def test_std_lib_modules_contains_only_strings(self):
        assert all(isinstance(item, str) for item in STD_LIB_MODULES)

    def test_std_lib_modules_spot_check(self):
        expected_modules = {"os", "sys", "json", "pathlib", "asyncio"}
        # The issubset() method checks if all items in expected_modules
        # are present in STD_LIB_MODULES.
        assert expected_modules.issubset(STD_LIB_MODULES)
