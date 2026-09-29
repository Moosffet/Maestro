"""
Utilitários de formatação de strings, duração, etc.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def format_duration(seconds: int | float) -> str:
    """
    Converte segundos em formato HH:MM:SS ou MM:SS.
    
    Args:
        seconds: Duração em segundos.
        
    Returns:
        String formatada (ex: "3:45" ou "1:23:45").
    """
    if not isinstance(seconds, (int, float)):
        return "00:00"
    
    try:
        seconds = int(max(0, seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    except (ValueError, TypeError):
        return "00:00"


def parse_duration(time_str: str) -> int:
    """
    Converte string de tempo em segundos.
    
    Args:
        time_str: String no formato "MM:SS" ou "HH:MM:SS".
        
    Returns:
        Duração em segundos.
        
    Raises:
        ValueError: Se formato inválido.
    """
    parts = time_str.split(":")
    
    try:
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        pass
    
    raise ValueError(f"Formato de tempo inválido: {time_str}")


def is_youtube_url(url: str) -> bool:
    """
    Verifica se é uma URL do YouTube.
    
    Args:
        url: URL a verificar.
        
    Returns:
        True se for YouTube, False caso contrário.
    """
    youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
    return bool(re.match(youtube_regex, url))


def is_playlist_url(url: str) -> bool:
    """
    Verifica se é uma URL de playlist do YouTube.
    
    Args:
        url: URL a verificar.
        
    Returns:
        True se for playlist, False caso contrário.
    """
    return "playlist?list=" in url or "/playlist?list=" in url


def extract_video_id(url: str) -> Optional[str]:
    """
    Extrai o ID do vídeo de uma URL do YouTube.
    
    Args:
        url: URL do YouTube.
        
    Returns:
        ID do vídeo ou None se inválido.
    """
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)",
        r"youtube\.com\/.*[?&]v=([^&\n?#]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def truncate(text: str, max_length: int = 100) -> str:
    """
    Trunca texto com ellipsis.
    
    Args:
        text: Texto a truncar.
        max_length: Comprimento máximo.
        
    Returns:
        Texto truncado.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def bold(text: str) -> str:
    """Retorna texto em bold no Discord."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Retorna texto em itálico no Discord."""
    return f"*{text}*"


def code(text: str) -> str:
    """Retorna texto em código no Discord."""
    return f"`{text}`"


def code_block(text: str, language: str = "") -> str:
    """Retorna texto em bloco de código no Discord."""
    return f"```{language}\n{text}\n```"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Formata datetime como string legível.
    
    Args:
        dt: datetime para formatar (padrão: agora).
        
    Returns:
        String formatada.
    """
    if dt is None:
        dt = datetime.now(datetime.UTC)
    
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_queue_item(index: int, title: str, duration: int, current: bool = False) -> str:
    """
    Formata item da fila para exibição.
    
    Args:
        index: Posição na fila.
        title: Título da música.
        duration: Duração em segundos.
        current: Se é a música atual.
        
    Returns:
        String formatada.
    """
    duration_str = format_duration(duration)
    title_short = truncate(title, 60)
    
    if current:
        return f"**▶️ {index}. {title_short}** [{duration_str}]"
    return f"{index}. {title_short} [{duration_str}]"


def create_embed_music_added(
    title: str,
    duration: int,
    added_by: str,
    position: int,
) -> dict:
    """
    Cria embed de música adicionada.
    
    Returns:
        Dict para passar em discord.Embed.
    """
    return {
        "title": "🎵 Música adicionada",
        "description": f"**{truncate(title)}**",
        "color": 0x1DB954,  # Verde Spotify
        "fields": [
            {"name": "Duração", "value": format_duration(duration), "inline": True},
            {"name": "Adicionado por", "value": added_by, "inline": True},
            {"name": "Posição na fila", "value": str(position), "inline": True},
        ],
    }


def create_embed_queue(
    items: list[str],
    page: int,
    total_pages: int,
    current: Optional[str] = None,
) -> dict:
    """
    Cria embed da fila.
    
    Returns:
        Dict para passar em discord.Embed.
    """
    description = ""
    
    if current:
        description += f"**▶️ Tocando agora:**\n{current}\n\n"
    
    description += "**Próximas músicas:**\n"
    if items:
        description += "\n".join(items)
    else:
        description += "*Nenhuma*"
    
    return {
        "title": "🎶 Fila de Reprodução",
        "description": description,
        "color": 0x1DB954,
        "footer": {"text": f"Página {page}/{total_pages}" if total_pages > 1 else ""},
    }


# Tests
if __name__ == "__main__":
    # Testa formatação de duração
    assert format_duration(0) == "0:00"
    assert format_duration(90) == "1:30"
    assert format_duration(3661) == "1:01:01"
    
    # Testa verificação de URL
    assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
    assert not is_youtube_url("https://example.com")
    
    # Testa verificação de playlist
    assert is_playlist_url("https://www.youtube.com/playlist?list=PLxxx")
    
    # Testa extração de ID
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    # Testa truncate
    assert truncate("abc", 3) == "abc"
    assert truncate("abcde", 3) == "..."
    
    print("✅ Todos os testes de formatação passaram!")
