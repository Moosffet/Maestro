"""Testes de validação."""

import pytest
from utils.validation import (
    validate_index,
    validate_volume,
    validate_url,
    validate_search_query,
)


class TestValidateIndex:
    """Testes de validate_index."""
    
    def test_valid_index(self):
        assert validate_index("1", 10) == 1
        assert validate_index("5", 10) == 5
        assert validate_index("10", 10) == 10
    
    def test_out_of_range(self):
        with pytest.raises(ValueError):
            validate_index("0", 10)
        with pytest.raises(ValueError):
            validate_index("11", 10)
    
    def test_invalid_number(self):
        with pytest.raises(ValueError):
            validate_index("abc", 10)
        with pytest.raises(ValueError):
            validate_index("-1", 10)


class TestValidateVolume:
    """Testes de validate_volume."""
    
    def test_valid_volume(self):
        assert validate_volume("0") == 0
        assert validate_volume("50") == 50
        assert validate_volume("100") == 100
    
    def test_out_of_range(self):
        with pytest.raises(ValueError):
            validate_volume("-1")
        with pytest.raises(ValueError):
            validate_volume("150")
    
    def test_invalid_number(self):
        with pytest.raises(ValueError):
            validate_volume("abc")


class TestValidateURL:
    """Testes de validate_url."""
    
    def test_valid_url(self):
        assert validate_url("https://example.com")
        assert validate_url("http://youtube.com/watch")
    
    def test_missing_protocol(self):
        with pytest.raises(ValueError):
            validate_url("example.com")
    
    def test_too_short(self):
        with pytest.raises(ValueError):
            validate_url("http://a")


class TestValidateSearchQuery:
    """Testes de validate_search_query."""
    
    def test_valid_query(self):
        assert validate_search_query("hello world") == "hello world"
        assert validate_search_query("  test  ") == "test"
    
    def test_too_short(self):
        with pytest.raises(ValueError):
            validate_search_query("a")
    
    def test_too_long(self):
        with pytest.raises(ValueError):
            validate_search_query("a" * 300)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
