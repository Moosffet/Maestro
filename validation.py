"""
Utilitários de validação de entrada.
"""

import re
from typing import Optional
from utils.formatting import is_youtube_url
from utils.errors import InvalidFavoriteError


def validate_index(value: str, max_value: int) -> int:
    """
    Valida um índice numérico.
    
    Args:
        value: String contendo o índice.
        max_value: Valor máximo permitido.
        
    Returns:
        Índice validado (1-based).
        
    Raises:
        ValueError: Se inválido.
    """
    try:
        index = int(value)
        if index < 1 or index > max_value:
            raise ValueError(f"Índice deve estar entre 1 e {max_value}")
        return index
    except ValueError:
        raise ValueError(f"'{value}' não é um número válido")


def validate_volume(value: str) -> int:
    """
    Valida volume (0-100).
    
    Args:
        value: String contendo o volume.
        
    Returns:
        Volume validado (0-100).
        
    Raises:
        ValueError: Se inválido.
    """
    try:
        volume = int(value)
        if volume < 0 or volume > 100:
            raise ValueError("Volume deve estar entre 0 e 100")
        return volume
    except ValueError:
        raise ValueError(f"'{value}' não é um volume válido")


def validate_url(url: str) -> str:
    """
    Valida URL básico.
    
    Args:
        url: URL a validar.
        
    Returns:
        URL validado.
        
    Raises:
        ValueError: Se inválido.
    """
    if not url or len(url) < 10:
        raise ValueError("URL muito curto")
    
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("URL deve começar com http:// ou https://")
    
    return url


def validate_search_query(query: str, min_length: int = 2) -> str:
    """
    Valida termo de busca.
    
    Args:
        query: Termo de busca.
        min_length: Comprimento mínimo.
        
    Returns:
        Query validado.
        
    Raises:
        ValueError: Se inválido.
    """
    query = query.strip()
    
    if len(query) < min_length:
        raise ValueError(f"Busca deve ter pelo menos {min_length} caracteres")
    
    if len(query) > 255:
        raise ValueError("Busca muito longa (máx 255 caracteres)")
    
    return query


def validate_favorite_data(data: dict) -> dict:
    """
    Valida dados de favorito.
    
    Args:
        data: Dicionário com dados do favorito.
        
    Returns:
        Dados validados.
        
    Raises:
        InvalidFavoriteError: Se inválido.
    """
    required_fields = ["url", "title"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise InvalidFavoriteError(f"Campo obrigatório ausente: {field}")
    
    # Valida URL
    try:
        validate_url(data["url"])
    except ValueError as e:
        raise InvalidFavoriteError(f"URL inválido: {e}")
    
    # Valida título
    if len(data["title"]) > 255:
        raise InvalidFavoriteError("Título muito longo (máx 255 caracteres)")
    
    return data


def normalize_youtube_url(url: str) -> str:
    """
    Normaliza URL do YouTube removendo parâmetros extras.
    
    Args:
        url: URL do YouTube.
        
    Returns:
        URL normalizada.
    """
    if "youtube.com" in url:
        # Extrai apenas o v parameter
        match = re.search(r"[?&]v=([^&]+)", url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
    
    elif "youtu.be" in url:
        # Extrai video ID
        match = re.search(r"youtu\.be/([^?]+)", url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
    
    return url


def is_valid_discord_user_id(user_id: int) -> bool:
    """
    Verifica se é um ID de usuário Discord válido.
    
    Args:
        user_id: ID a verificar.
        
    Returns:
        True se válido, False caso contrário.
    """
    return isinstance(user_id, int) and 17 <= len(str(user_id)) <= 20


# Tests
if __name__ == "__main__":
    # Testa índice
    assert validate_index("1", 10) == 1
    assert validate_index("10", 10) == 10
    try:
        validate_index("0", 10)
        assert False, "Deveria falhar"
    except ValueError:
        pass
    
    # Testa volume
    assert validate_volume("0") == 0
    assert validate_volume("50") == 50
    assert validate_volume("100") == 100
    try:
        validate_volume("150")
        assert False, "Deveria falhar"
    except ValueError:
        pass
    
    # Testa query
    assert validate_search_query("ab") == "ab"
    try:
        validate_search_query("a")
        assert False, "Deveria falhar"
    except ValueError:
        pass
    
    # Testa URL
    assert validate_url("https://example.com/test")
    try:
        validate_url("invalid")
        assert False, "Deveria falhar"
    except ValueError:
        pass
    
    print("✅ Todos os testes de validação passaram!")
