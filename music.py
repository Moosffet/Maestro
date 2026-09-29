"""
Comandos de reprodução musical.
!conectar, !tocar, !pausar, !pular, !volume, etc.
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

from config import settings
from services.queue import queue_manager, QueueItem
from services.youtube import (
    search_video,
    get_video_info,
    get_playlist_videos,
    is_youtube_url,
    is_playlist_url,
)
from services.player import player_manager
from services.favorites import favorites_manager
from utils.formatting import (
    format_duration,
    format_queue_item,
    truncate,
    is_youtube_url as fmt_is_youtube,
    is_playlist_url as fmt_is_playlist,
)
from utils.validation import validate_volume, validate_index
from utils.errors import (
    YouTubeError,
    PlayerError,
    NotConnectedError,
    QueueEmptyError,
    BotError,
    format_error_for_user,
    format_error_for_log,
)


logger = logging.getLogger(__name__)


class MusicCog(commands.Cog):
    """Cog de comandos musicais."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def _connect_to_voice(self, ctx: commands.Context) -> discord.VoiceClient:
        """Conecta ao canal de voz do usuário."""
        if not ctx.author.voice:
            raise PlayerError(
                "Usuário não em canal de voz",
                "❌ Você precisa estar em um canal de voz."
            )
        
        channel = ctx.author.voice.channel
        
        if ctx.voice_client:
            if ctx.voice_client.channel.id == channel.id:
                return ctx.voice_client
            await ctx.voice_client.move_to(channel)
        else:
            try:
                voice_client = await channel.connect()
            except Exception as e:
                raise PlayerError(
                    f"Erro ao conectar: {e}",
                    "❌ Não consegui conectar ao canal de voz."
                ) from e
        
        return ctx.voice_client
    
    @commands.command(name="conectar", aliases=["j", "join"])
    async def connect_command(self, ctx: commands.Context):
        """Conecta ao canal de voz."""
        try:
            voice_client = await self._connect_to_voice(ctx)
            
            queue = await queue_manager.get_queue(ctx.guild.id)
            queue.voice_channel_id = voice_client.channel.id
            
            embed = discord.Embed(
                title="🎵 Conectado",
                description=f"Conectado a **{voice_client.channel.name}**",
                color=0x1DB954
            )
            await ctx.send(embed=embed)
            
        except BotError as e:
            await ctx.send(format_error_for_user(e))
            logger.error(f"[{ctx.guild.id}] {format_error_for_log(e)}")
        except Exception as e:
            await ctx.send("❌ Erro ao conectar")
            logger.error(f"[{ctx.guild.id}] Erro inesperado: {e}")
    
    @commands.command(name="tocar", aliases=["p", "play"])
    async def play_command(self, ctx: commands.Context, *, query: str):
        """
        Toca uma música.
        Aceita: nome, URL, URL de playlist, ou 'favorito X'
        """
        try:
            # Conecta se necessário
            voice_client = await self._connect_to_voice(ctx)
            queue = await queue_manager.get_queue(ctx.guild.id)
            
            # Verifica se é favorito
            if query.lower().startswith("favorito "):
                try:
                    fav_index = int(query.split(" ", 1)[1])
                    favorite = await favorites_manager.get(fav_index)
                    query = favorite.url
                except (ValueError, IndexError):
                    await ctx.send("❌ Uso: !tocar favorito <número>")
                    return
            
            # Processa URL ou busca
            if fmt_is_youtube(query):
                # URL do YouTube
                if fmt_is_playlist(query):
                    # Playlist
                    await ctx.send(f"⏳ Carregando playlist...")
                    playlist = await get_playlist_videos(query, settings.playlist_limit)
                    
                    if not playlist.videos:
                        await ctx.send("❌ Playlist vazia")
                        return
                    
                    # Adiciona vídeos à fila
                    items = [
                        QueueItem(
                            video_id=v.video_id,
                            title=v.title,
                            duration=v.duration,
                            uploader=v.uploader,
                            url=v.url,
                            added_by=ctx.author.name,
                            added_by_id=ctx.author.id,
                        )
                        for v in playlist.videos
                    ]
                    
                    start_pos, count = await queue.add_batch(items)
                    
                    embed = discord.Embed(
                        title="🎶 Playlist adicionada",
                        description=f"**{playlist.title}** ({count} músicas)",
                        color=0x1DB954
                    )
                    embed.add_field(
                        name="Posição",
                        value=f"#{start_pos} - #{start_pos + count - 1}",
                        inline=False
                    )
                    await ctx.send(embed=embed)
                    
                    # Inicia reprodução se nada tocando
                    if not queue.is_playing:
                        await self._play_next(ctx, voice_client, queue)
                
                else:
                    # Vídeo único
                    video = await get_video_info(query)
                    item = QueueItem(
                        video_id=video.video_id,
                        title=video.title,
                        duration=video.duration,
                        uploader=video.uploader,
                        url=video.url,
                        added_by=ctx.author.name,
                        added_by_id=ctx.author.id,
                    )
                    position = await queue.add(item)
                    
                    embed = discord.Embed(
                        title="🎵 Música adicionada",
                        description=f"**{truncate(video.title)}**",
                        color=0x1DB954
                    )
                    embed.add_field(name="Duração", value=format_duration(video.duration))
                    embed.add_field(name="Posição", value=f"#{position}")
                    await ctx.send(embed=embed)
                    
                    if not queue.is_playing:
                        await self._play_next(ctx, voice_client, queue)
            
            else:
                # Busca no YouTube
                await ctx.send(f"⏳ Buscando '{query}'...")
                video = await search_video(query)
                
                item = QueueItem(
                    video_id=video.video_id,
                    title=video.title,
                    duration=video.duration,
                    uploader=video.uploader,
                    url=video.url,
                    added_by=ctx.author.name,
                    added_by_id=ctx.author.id,
                )
                position = await queue.add(item)
                
                embed = discord.Embed(
                    title="🎵 Música adicionada",
                    description=f"**{truncate(video.title)}**",
                    color=0x1DB954
                )
                embed.add_field(name="Canal", value=video.uploader)
                embed.add_field(name="Duração", value=format_duration(video.duration))
                embed.add_field(name="Posição", value=f"#{position}")
                await ctx.send(embed=embed)
                
                if not queue.is_playing:
                    await self._play_next(ctx, voice_client, queue)
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
            logger.error(f"[{ctx.guild.id}] {format_error_for_log(e)}")
        except Exception as e:
            await ctx.send("❌ Erro ao tocar música")
            logger.error(f"[{ctx.guild.id}] Erro inesperado: {e}", exc_info=True)
    
    async def _play_next(
        self,
        ctx: commands.Context,
        voice_client: discord.VoiceClient,
        queue,
    ) -> None:
        """Inicia reprodução da próxima música."""
        if not voice_client or not voice_client.is_connected():
            return
        
        try:
            item = await queue.pop_next()
            if not item:
                queue.is_playing = False
                return
            
            player = await player_manager.get_player(
                ctx.guild.id,
                on_finished=lambda: self._on_track_finish(ctx, queue),
            )
            
            # Cria VideoInfo a partir do QueueItem
            from services.youtube import VideoInfo
            video = VideoInfo(
                video_id=item.video_id,
                title=item.title,
                duration=item.duration,
                uploader=item.uploader,
                url=item.url,
            )
            
            await player.play_video(video, voice_client, queue.volume)
            queue.is_playing = True
        
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao iniciar reprodução: {e}")
    
    def _on_track_finish(self, ctx: commands.Context, queue) -> None:
        """Callback quando música termina."""
        # Esta função deve ser async mas é chamada como sync
        # Cria task para executar próxima música
        asyncio.create_task(self._play_next_task(ctx, queue))
    
    async def _play_next_task(self, ctx: commands.Context, queue) -> None:
        """Task para tocar próxima música."""
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return
        
        # Verifica loop
        if queue.loop == 1 and queue.current:
            # Loop de uma música - repete atual
            player = await player_manager.get_player(ctx.guild.id)
            from services.youtube import VideoInfo
            video = VideoInfo(
                video_id=queue.current.video_id,
                title=queue.current.title,
                duration=queue.current.duration,
                uploader=queue.current.uploader,
                url=queue.current.url,
            )
            await player.play_video(video, ctx.voice_client, queue.volume)
        else:
            # Próxima música ou loop de fila
            if queue.loop == 2 and queue.current:
                # Loop de fila - volta atual para fila
                await queue.queue.appendleft(queue.current)
            
            await self._play_next(ctx, ctx.voice_client, queue)
    
    @commands.command(name="pausa")
    async def pause_command(self, ctx: commands.Context):
        """Pausa a música."""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                raise NotConnectedError()
            
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                queue = await queue_manager.get_queue(ctx.guild.id)
                queue.is_paused = True
                await ctx.send("⏸️ Pausado")
            else:
                await ctx.send("❌ Nenhuma música tocando")
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao pausar: {e}")
            await ctx.send("❌ Erro ao pausar")
    
    @commands.command(name="retomar", aliases=["r", "resume"])
    async def resume_command(self, ctx: commands.Context):
        """Retoma a música pausada."""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                raise NotConnectedError()
            
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                queue = await queue_manager.get_queue(ctx.guild.id)
                queue.is_paused = False
                await ctx.send("▶️ Retomando")
            else:
                await ctx.send("❌ Nenhuma música pausada")
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao retomar: {e}")
            await ctx.send("❌ Erro ao retomar")
    
    @commands.command(name="proximo", aliases=["s", "next"])
    async def next_command(self, ctx: commands.Context):
        """Pula para próxima música."""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                raise NotConnectedError()
            
            queue = await queue_manager.get_queue(ctx.guild.id)
            
            if not queue.queue and not queue.current:
                raise QueueEmptyError()
            
            ctx.voice_client.stop()
            await ctx.send("⏭️ Pulando")
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao pular: {e}")
            await ctx.send("❌ Erro ao pular")
    
    @commands.command(name="pular", aliases=["jmp", "jump"])
    async def jump_command(self, ctx: commands.Context, position: str):
        """Pula para posição específica."""
        try:
            queue = await queue_manager.get_queue(ctx.guild.id)
            pos = validate_index(position, queue.queue_size)
            
            if pos == 1 and queue.current:
                await ctx.send("✓ Já estamos nesta posição")
                return
            
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                raise NotConnectedError()
            
            # Pula para posição
            skip_count = pos - (1 if queue.current else 0)
            await queue.skip(skip_count)
            
            ctx.voice_client.stop()
            await ctx.send(f"⏭️ Pulando para posição #{pos}")
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except ValueError as e:
            await ctx.send(f"❌ {e}")
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao pular: {e}")
            await ctx.send("❌ Erro ao pular")
    
    @commands.command(name="parar", aliases=["stop"])
    async def stop_command(self, ctx: commands.Context):
        """Para a reprodução e limpa fila."""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                raise NotConnectedError()
            
            queue = await queue_manager.get_queue(ctx.guild.id)
            await queue.reset()
            
            ctx.voice_client.stop()
            await ctx.send("⏹️ Parado e fila limpa")
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao parar: {e}")
            await ctx.send("❌ Erro ao parar")
    
    @commands.command(name="limpar", aliases=["cl", "clear"])
    async def clear_command(self, ctx: commands.Context):
        """Limpa a fila (mantém música atual)."""
        try:
            queue = await queue_manager.get_queue(ctx.guild.id)
            await queue.clear()
            await ctx.send("🧹 Fila limpa")
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao limpar: {e}")
            await ctx.send("❌ Erro ao limpar")
    
    @commands.command(name="fila", aliases=["q", "queue"])
    async def queue_command(self, ctx: commands.Context, page: str = "1"):
        """Mostra fila de reprodução."""
        try:
            queue = await queue_manager.get_queue(ctx.guild.id)
            
            try:
                page_num = int(page)
                if page_num < 1:
                    raise ValueError
            except ValueError:
                await ctx.send("❌ Página inválida")
                return
            
            items, total_pages = await queue.get_page(page_num, per_page=10)
            
            # Construi descrição
            description = ""
            if queue.current:
                description += f"**▶️ Tocando agora:**\n"
                description += f"{format_queue_item(0, queue.current.title, queue.current.duration, True)}\n\n"
            
            if items:
                description += "**Próximas músicas:**\n"
                start_idx = (page_num - 1) * 10 + 1
                for i, item in enumerate(items, start=1):
                    description += f"{format_queue_item(start_idx + i, item.title, item.duration)}\n"
            else:
                description += "**Próximas músicas:**\n*Nenhuma*"
            
            embed = discord.Embed(
                title="🎶 Fila de Reprodução",
                description=description,
                color=0x1DB954
            )
            
            total_items = queue.queue_size
            embed.add_field(name="Total", value=f"{total_items} músicas")
            embed.add_field(name="Duração", value=format_duration(queue.total_duration))
            embed.set_footer(text=f"Página {page_num}/{total_pages}")
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao mostrar fila: {e}")
            await ctx.send("❌ Erro ao mostrar fila")
    
    @commands.command(name="repetir", aliases=["l", "loop"])
    async def loop_command(self, ctx: commands.Context, mode: str = ""):
        """
        Alterna modo loop.
        Uso: !repetir [off|song|queue]
        """
        try:
            queue = await queue_manager.get_queue(ctx.guild.id)
            
            if not mode or mode.lower() == "cycle":
                queue.loop = (queue.loop + 1) % 3
            elif mode.lower() == "off":
                queue.loop = 0
            elif mode.lower() == "song":
                queue.loop = 1
            elif mode.lower() in ("queue", "fila"):
                queue.loop = 2
            else:
                await ctx.send("❌ Uso: !repetir [off|song|queue]")
                return
            
            modes = ["❌ Desativado", "🔂 Uma música", "🔁 Fila inteira"]
            await ctx.send(f"Loop {modes[queue.loop]}")
        
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao ativar loop: {e}")
            await ctx.send("❌ Erro ao ativar loop")
    
    @commands.command(name="embaralhar", aliases=["sh", "shuffle"])
    async def shuffle_command(self, ctx: commands.Context):
        """Embaralha a fila."""
        try:
            queue = await queue_manager.get_queue(ctx.guild.id)
            await queue.shuffle()
            await ctx.send("🔀 Fila embaralhada")
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao embaralhar: {e}")
            await ctx.send("❌ Erro ao embaralhar")
    
    @commands.command(name="voltar", aliases=["b", "prev", "previous"])
    async def previous_command(self, ctx: commands.Context):
        """Volta para música anterior."""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                raise NotConnectedError()
            
            queue = await queue_manager.get_queue(ctx.guild.id)
            
            if not queue.history:
                await ctx.send("❌ Nenhuma música anterior")
                return
            
            item = await queue.previous()
            ctx.voice_client.stop()
            await ctx.send(f"⏮️ Voltando para: {truncate(item.title)}")
        
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao voltar: {e}")
            await ctx.send("❌ Erro ao voltar")
    
    @commands.command(name="volume", aliases=["vol"])
    async def volume_command(self, ctx: commands.Context, level: str):
        """Define volume (0-100)."""
        try:
            volume = validate_volume(level)
            
            queue = await queue_manager.get_queue(ctx.guild.id)
            queue.volume = volume
            
            if ctx.voice_client and ctx.voice_client.source:
                player = await player_manager.get_player(ctx.guild.id)
                player.set_volume(volume)
            
            await ctx.send(f"🔊 Volume: {volume}%")
        
        except ValueError as e:
            await ctx.send(f"❌ {e}")
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao ajustar volume: {e}")
            await ctx.send("❌ Erro ao ajustar volume")
    
    @commands.command(name="sair", aliases=["dc", "disconnect"])
    async def disconnect_command(self, ctx: commands.Context):
        """Desconecta do canal de voz."""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                await ctx.send("❌ Não estou conectado")
                return
            
            queue = await queue_manager.get_queue(ctx.guild.id)
            await queue.reset()
            
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Desconectado")
        
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao desconectar: {e}")
            await ctx.send("❌ Erro ao desconectar")
    
    @commands.command(name="ouvindoagora", aliases=["np", "nowplaying"])
    async def nowplaying_command(self, ctx: commands.Context):
        """Mostra música tocando agora."""
        try:
            queue = await queue_manager.get_queue(ctx.guild.id)
            
            if not queue.current:
                await ctx.send("❌ Nenhuma música tocando")
                return
            
            embed = discord.Embed(
                title="🎵 Tocando Agora",
                description=f"**{queue.current.title}**",
                color=0x1DB954,
                url=queue.current.url
            )
            embed.add_field(name="Canal", value=queue.current.uploader)
            embed.add_field(name="Duração", value=format_duration(queue.current.duration))
            embed.add_field(name="Adicionado por", value=queue.current.added_by)
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao mostrar música atual: {e}")
            await ctx.send("❌ Erro ao mostrar música atual")


import asyncio


async def setup(bot: commands.Bot):
    """Carrega este cog."""
    await bot.add_cog(MusicCog(bot))
    logger.info("✓ Cog Music carregado")
