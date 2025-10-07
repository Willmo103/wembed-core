import pytest

from wembed_core.enums import CodeChunkerChunkTypes, CodeChunkerDependancyTypes


def test_enum_members_exist():
    """
    Tests that all expected members are present in the enum.
    """
    assert hasattr(CodeChunkerDependancyTypes, "STD_LIB")
    assert hasattr(CodeChunkerDependancyTypes, "LOCAL")
    assert hasattr(CodeChunkerDependancyTypes, "EXTERNAL")


def test_enum_member_values():
    """
    Tests that each enum member has the correct string value.
    """
    assert CodeChunkerDependancyTypes.STD_LIB.value == "stdlib"
    assert CodeChunkerDependancyTypes.LOCAL.value == "local"
    assert CodeChunkerDependancyTypes.EXTERNAL.value == "external"


def test_enum_member_types():
    """
    Tests that enum members are instances of both the enum class and str.
    This is because it inherits from (str, Enum).
    """
    assert isinstance(CodeChunkerDependancyTypes.STD_LIB, CodeChunkerDependancyTypes)
    assert isinstance(CodeChunkerDependancyTypes.LOCAL, str)
    assert isinstance(CodeChunkerDependancyTypes.EXTERNAL, str)


def test_enum_completeness():
    """
    Ensures no unexpected members have been added.
    """
    expected_members = {"STD_LIB", "LOCAL", "EXTERNAL"}
    actual_members = {member.name for member in CodeChunkerDependancyTypes}
    assert actual_members == expected_members


class TestCodeChunkerChunkTypes:
    """Tests for the CodeChunkerChunkTypes Enum."""

    def test_chunk_type_members_exist(self):
        """Ensures all expected members are present in the enum."""
        assert hasattr(CodeChunkerChunkTypes, "FUNCTION")
        assert hasattr(CodeChunkerChunkTypes, "CLASS")
        assert hasattr(CodeChunkerChunkTypes, "METHOD")
        assert hasattr(CodeChunkerChunkTypes, "IMPORT")
        assert hasattr(CodeChunkerChunkTypes, "MODULE")

    def test_chunk_type_member_values(self):
        """Verifies that each enum member has the correct string value."""
        assert CodeChunkerChunkTypes.FUNCTION.value == "function"
        assert CodeChunkerChunkTypes.CLASS.value == "class"
        assert CodeChunkerChunkTypes.METHOD.value == "method"
        assert CodeChunkerChunkTypes.IMPORT.value == "import"
        assert CodeChunkerChunkTypes.MODULE.value == "module"

    def test_chunk_type_member_types(self):
        """Confirms members are instances of both the enum class and str."""
        assert isinstance(CodeChunkerChunkTypes.FUNCTION, CodeChunkerChunkTypes)
        assert isinstance(CodeChunkerChunkTypes.CLASS, str)

    def test_chunk_type_completeness(self):
        """Checks that no unexpected members have been added."""
        expected_members = {"FUNCTION", "CLASS", "METHOD", "IMPORT", "MODULE"}
        actual_members = {member.name for member in CodeChunkerChunkTypes}
        assert actual_members == expected_members
