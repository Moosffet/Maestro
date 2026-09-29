"""Testes de formatação."""

import pytest
from utils.formatting import (
    format_duration,
    parse_duration,
    is_youtube_url,
    is_playlist_url,
    extract_video_id,
    truncate,
)


class TestFormatDuration:
    """Testes de format_duration."""
    
    def test_zero_seconds(self):
        assert format_duration(0) == "0:00"
    
    def test_seconds_only(self):
        assert format_duration(45) == "0:45"
    
    def test_minutes_and_seconds(self):
        assert format_duration(90) == "1:30"
        assert format_duration(125) == "2:05"
    
    def test_hours_minutes_seconds(self):
        assert format_duration(3661) == "1:01:01"
        assert format_duration(7322) == "2:02:02"
    
    def test_invalid_input(self):
        assert format_duration("invalid") == "00:00"
        assert format_duration(None) == "00:00"


class TestParseDuration:
    """Testes de parse_duration."""
    
    def test_minutes_seconds(self):
        assert parse_duration("1:30") == 90
        assert parse_duration("0:45") == 45
    
    def test_hours_minutes_seconds(self):
        assert parse_duration("1:01:01") == 3661
        assert parse_duration("2:02:02") == 7322
    
    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_duration("invalid")
        with pytest.raises(ValueError):
            parse_duration("1:2:3:4")


class TestYouTubeURL:
    """Testes de URL do YouTube."""
    
    def test_youtube_com_url(self):
        assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert is_youtube_url("http://youtube.com/watch?v=dQw4w9WgXcQ")
    
    def test_youtu_be_url(self):
        assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        assert is_youtube_url("http://youtu.be/dQw4w9WgXcQ")
    
    def test_non_youtube_url(self):
        assert not is_youtube_url("https://example.com")
        assert not is_youtube_url("https://vimeo.com/123")


class TestPlaylistURL:
    """Testes de URL de playlist."""
    
    def test_playlist_url(self):
        assert is_playlist_url("https://www.youtube.com/playlist?list=PLxxx")
        assert is_playlist_url("https://youtube.com/playlist?list=PLyyy")
    
    def test_non_playlist_url(self):
        assert not is_playlist_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


class TestExtractVideoID:
    """Testes de extração de video ID."""
    
    def test_youtube_com_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_youtu_be_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_with_parameters(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_invalid_url(self):
        assert extract_video_id("https://example.com") is None


class TestTruncate:
    """Testes de truncate."""
    
    def test_no_truncate(self):
        text = "Hello World"
        assert truncate(text, 20) == "Hello World"
    
    def test_truncate(self):
        text = "Hello World This Is A Long Text"
        result = truncate(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")
    
    def test_default_length(self):
        text = "A" * 150
        result = truncate(text, 100)
        assert len(result) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
