"""
Integração com yt-dlp para busca de vídeos e extração de streams.
Executa operações bloqueantes em executor thread.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from dataclasses import dataclass
import yt_dlp

from config import settings as global_settings
from utils.formatting import is_youtube_url, is_playlist_url, extract_video_id
from utils.errors import (
    YouTubeError,
    VideoNotFoundError,
    PlaylistError,
    StreamError,
    URLNotFoundError,
)


logger = logging.getLogger(__name__)


# Executor para operações bloqueantes
_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="youtube_")


@dataclass
class VideoInfo:
    """Informações de um vídeo."""
    video_id: str
    title: str
    duration: int  # segundos
    uploader: str
    url: str
    stream_url: Optional[str] = None


@dataclass
class PlaylistInfo:
    """Informações de uma playlist."""
    playlist_id: str
    title: str
    video_count: int
    videos: list[VideoInfo]


def _get_yt_dlp_options() -> dict:
    """
    Retorna opções do yt-dlp.
    Centraliza toda a configuração.
    """
    options = {
        "format": "bestaudio/best",
        "quiet": False,
        "no_warnings": False,
        "default_search": "ytsearch",
        "socket_timeout": 30,
        "skip_unavailable_fragments": True,
        "fragment_retries": 3,
    }
    
    # Configura bgutil se especificado
    if global_settings and global_settings.bgutil_url:
        options["proxy"] = global_settings.bgutil_url
        logger.debug(f"Usando bgutil: {global_settings.bgutil_url}")
    
    # Configura cookies se especificado
    if global_settings and global_settings.cookies_file:
        options["cookiefile"] = global_settings.cookies_file
        logger.debug(f"Usando cookies: {global_settings.cookies_file}")
    
    return options


def _extract_video_info(info: dict) -> VideoInfo:
    """Extrai informações relevantes de um vídeo."""
    return VideoInfo(
        video_id=info.get("id", "unknown"),
        title=info.get("title", "Desconhecido"),
        duration=int(info.get("duration", 0)),
        uploader=info.get("uploader", "Desconhecido"),
        url=info.get("webpage_url") or f"https://youtube.com/watch?v={info.get('id')}",
    )


async def search_video(query: str) -> VideoInfo:
    """
    Busca um vídeo no YouTube.
    
    Args:
        query: Termo de busca.
        
    Returns:
        VideoInfo do primeiro resultado.
        
    Raises:
        VideoNotFoundError: Se não encontrar.
        YouTubeError: Se erro no yt-dlp.
    """
    logger.info(f"Buscando vídeo: {query}")
    
    def _search():
        try:
            with yt_dlp.YoutubeDL(_get_yt_dlp_options()) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                
                if not info or "entries" not in info or not info["entries"]:
                    raise VideoNotFoundError(query)
                
                video_info = info["entries"][0]
                return _extract_video_info(video_info)
        
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Erro yt-dlp ao buscar '{query}': {e}")
            raise VideoNotFoundError(query) from e
        except Exception as e:
            logger.error(f"Erro ao buscar '{query}': {e}")
            raise YouTubeError(f"Erro ao buscar: {e}") from e
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _search)


async def get_video_info(url: str) -> VideoInfo:
    """
    Obtém informações de um vídeo do YouTube.
    
    Args:
        url: URL do vídeo.
        
    Returns:
        VideoInfo.
        
    Raises:
        URLNotFoundError: Se URL inválida.
        YouTubeError: Se erro no yt-dlp.
    """
    if not is_youtube_url(url):
        raise URLNotFoundError()
    
    logger.info(f"Obtendo info: {url}")
    
    def _get_info():
        try:
            with yt_dlp.YoutubeDL({**_get_yt_dlp_options(), "noplaylist": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise URLNotFoundError()
                
                return _extract_video_info(info)
        
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Erro yt-dlp ao obter info '{url}': {e}")
            raise URLNotFoundError() from e
        except Exception as e:
            logger.error(f"Erro ao obter info '{url}': {e}")
            raise YouTubeError(f"Erro ao obter info: {e}") from e
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_info)


async def get_playlist_videos(url: str, limit: int = 200) -> PlaylistInfo:
    """
    Obtém vídeos de uma playlist.
    
    Args:
        url: URL da playlist.
        limit: Máximo de vídeos a carregar.
        
    Returns:
        PlaylistInfo com vídeos.
        
    Raises:
        PlaylistError: Se erro.
    """
    if not is_playlist_url(url):
        raise PlaylistError("URL não é uma playlist válida")
    
    logger.info(f"Carregando playlist (limite: {limit}): {url}")
    
    def _get_playlist():
        try:
            options = {
                **_get_yt_dlp_options(),
                "extract_flat": "in_playlist",
                "playlist_items": f"1-{limit}",
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise PlaylistError("Playlist não encontrada")
                
                videos = []
                for entry in info.get("entries", []):
                    if entry:
                        video_info = VideoInfo(
                            video_id=entry.get("id", "unknown"),
                            title=entry.get("title", "Desconhecido"),
                            duration=int(entry.get("duration", 0)),
                            uploader=entry.get("uploader", "Desconhecido"),
                            url=entry.get("url") or f"https://youtube.com/watch?v={entry.get('id')}",
                        )
                        videos.append(video_info)
                
                return PlaylistInfo(
                    playlist_id=info.get("id", "unknown"),
                    title=info.get("title", "Desconhecida"),
                    video_count=len(videos),
                    videos=videos,
                )
        
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Erro yt-dlp ao carregar playlist: {e}")
            raise PlaylistError(f"Erro ao carregar: {e}") from e
        except Exception as e:
            logger.error(f"Erro ao carregar playlist: {e}")
            raise PlaylistError(f"Erro: {e}") from e
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _get_playlist)


async def get_stream_url(video_id: str) -> str:
    """
    Obtém URL de stream de áudio de um vídeo.
    
    Args:
        video_id: ID do vídeo do YouTube.
        
    Returns:
        URL de stream.
        
    Raises:
        StreamError: Se não conseguir obter stream.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info(f"Obtendo stream: {video_id}")
    
    def _get_stream():
        try:
            options = {
                **_get_yt_dlp_options(),
                "format": "bestaudio/best",
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Tenta obter URL de stream
                stream_url = info.get("url") or info.get("formats", [{}])[-1].get("url")
                
                if not stream_url:
                    raise StreamError()
                
                return stream_url
        
        except StreamError:
            raise
        except Exception as e:
            logger.error(f"Erro ao obter stream para {video_id}: {e}")
            raise StreamError() from e
    
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(_executor, _get_stream),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout ao obter stream: {video_id}")
        raise StreamError()


async def test_connection() -> bool:
    """
    Testa conexão com YouTube.
    
    Returns:
        True se conectado, False caso contrário.
    """
    logger.info("Testando conexão com YouTube...")
    
    try:
        # Tenta buscar um vídeo simples
        video = await search_video("test")
        logger.info(f"✓ Conexão OK. Teste: {video.title}")
        return True
    except Exception as e:
        logger.warning(f"⚠ Falha na conexão: {e}")
        return False
