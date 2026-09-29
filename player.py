"""
Reprodução de áudio no Discord.
Gerencia playback, callbacks e reconexão.
"""

import asyncio
import logging
from typing import Optional, Callable, Any
import discord
from discord.ext import commands

from services.queue import GuildQueue, queue_manager
from services.youtube import get_stream_url, VideoInfo
from utils.errors import (
    PlayerError,
    NotConnectedError,
    StreamError,
)


logger = logging.getLogger(__name__)


class AudioPlayer:
    """Controlador de áudio para um servidor."""
    
    def __init__(
        self,
        guild_id: int,
        ffmpeg_path: str,
        on_finished: Optional[Callable] = None,
    ):
        self.guild_id = guild_id
        self.ffmpeg_path = ffmpeg_path
        self.on_finished = on_finished
        self.current_source: Optional[discord.PCMVolumeTransformer] = None
        self.is_playing = False
    
    async def play_video(
        self,
        video: VideoInfo,
        voice_client: discord.VoiceClient,
        volume: int = 100,
    ) -> None:
        """
        Inicia reprodução de um vídeo.
        
        Args:
            video: Informações do vídeo.
            voice_client: Cliente de voz do Discord.
            volume: Volume (0-100).
            
        Raises:
            StreamError: Se não conseguir obter stream.
            PlayerError: Se erro ao reproduzir.
        """
        if not voice_client or not voice_client.is_connected():
            raise NotConnectedError()
        
        logger.info(f"[{self.guild_id}] Iniciando reprodução: {video.title}")
        
        # Obtém URL de stream
        stream_url = await get_stream_url(video.video_id)
        
        # Cria source
        try:
            source = discord.FFmpegOpusAudio(
                stream_url,
                executable=self.ffmpeg_path,
                **{
                    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    "options": "-vn",
                }
            )
            
            # Aplica volume
            volume_source = discord.PCMVolumeTransformer(source, volume=volume / 100)
            self.current_source = volume_source
            
            # Callback
            def after_play(error):
                if error:
                    logger.error(f"[{self.guild_id}] Erro ao reproduzir: {error}")
                else:
                    logger.debug(f"[{self.guild_id}] Reprodução finalizada")
                
                # Chama callback se definido
                if self.on_finished:
                    asyncio.create_task(self.on_finished())
            
            # Reproduz
            voice_client.play(volume_source, after=after_play)
            self.is_playing = True
            logger.info(f"✓ Reproduzindo: {video.title}")
        
        except Exception as e:
            logger.error(f"[{self.guild_id}] Erro ao iniciar playback: {e}")
            raise PlayerError(f"Erro ao reproduzir: {e}") from e
    
    def stop(self) -> None:
        """Para reprodução."""
        if self.is_playing:
            self.is_playing = False
            # Parar via voice_client é feito externamente
            logger.debug(f"[{self.guild_id}] Stop solicitado")
    
    def set_volume(self, volume: int) -> None:
        """
        Define volume.
        
        Args:
            volume: Volume (0-100).
        """
        if self.current_source and isinstance(self.current_source, discord.PCMVolumeTransformer):
            self.current_source.volume = volume / 100
            logger.debug(f"[{self.guild_id}] Volume: {volume}%")


class PlayerManager:
    """Gerencia reprodução para todos os servidores."""
    
    def __init__(self, ffmpeg_path: str):
        self.ffmpeg_path = ffmpeg_path
        self.players: dict[int, AudioPlayer] = {}
        self.global_lock = asyncio.Lock()
    
    async def get_player(
        self,
        guild_id: int,
        on_finished: Optional[Callable] = None,
    ) -> AudioPlayer:
        """Obtém ou cria player para servidor."""
        if guild_id not in self.players:
            async with self.global_lock:
                if guild_id not in self.players:
                    self.players[guild_id] = AudioPlayer(
                        guild_id=guild_id,
                        ffmpeg_path=self.ffmpeg_path,
                        on_finished=on_finished,
                    )
        
        return self.players[guild_id]
    
    async def delete_player(self, guild_id: int) -> None:
        """Remove player."""
        if guild_id in self.players:
            del self.players[guild_id]
            logger.debug(f"[{guild_id}] Player deletado")


# Instância global
player_manager: Optional[PlayerManager] = None


def init_player_manager(ffmpeg_path: str) -> PlayerManager:
    """Inicializa gerenciador de reprodução."""
    global player_manager
    player_manager = PlayerManager(ffmpeg_path)
    return player_manager
