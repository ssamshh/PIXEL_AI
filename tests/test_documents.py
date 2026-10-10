import pytest
from pixel.documents import extract_text

def test_text_extract():
    assert extract_text("notes.txt",b"hello PIXEL")=="hello PIXEL"

def test_reject_unsupported():
    with pytest.raises(ValueError):
        extract_text("program.exe",b"no")
