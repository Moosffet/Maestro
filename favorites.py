"""
Comandos de gerenciamento de favoritos.
!favoritos add, !favoritos rem, !favoritos lista
"""

import discord
from discord.ext import commands
import logging

from services.favorites import favorites_manager
from utils.errors import BotError, format_error_for_user, format_error_for_log
from utils.formatting import truncate
from utils.validation import validate_url, validate_index


logger = logging.getLogger(__name__)


class FavoritesCog(commands.Cog):
    """Cog de gerenciamento de favoritos."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.group(name="favoritos", aliases=["fav"], invoke_without_command=True)
    async def favorites_group(self, ctx: commands.Context):
        """Gerencia favoritos. Use: !favoritos [add|rem|lista]"""
        await ctx.send(
            "🎵 **Gerenciador de Favoritos**\n"
            "`!favoritos add <URL>` - Adiciona favorito\n"
            "`!favoritos rem <número>` - Remove favorito\n"
            "`!favoritos lista` - Lista favoritos\n"
            "`!tocar favorito <número>` - Toca favorito"
        )
    
    @favorites_group.command(name="add")
    async def add_favorite(self, ctx: commands.Context, *, url: str):
        """Adiciona uma nova música aos favoritos."""
        try:
            # Valida URL
            validate_url(url)
            
            # Obtém título da URL (por enquanto usa URL como título)
            title = truncate(url, 100)
            
            # Tenta obter título real se for YouTube
            from utils.formatting import is_youtube_url
            if is_youtube_url(url):
                try:
                    from services.youtube import get_video_info
                    video = await get_video_info(url)
                    title = video.title
                except Exception as e:
                    logger.debug(f"Não consegui obter título: {e}")
            
            # Adiciona ao gerenciador
            index = await favorites_manager.add(
                url=url,
                title=title,
                added_by=ctx.author.name,
                added_by_id=ctx.author.id,
                guild_id=ctx.guild.id,
            )
            
            embed = discord.Embed(
                title="⭐ Favorito Adicionado",
                description=f"**{truncate(title)}**",
                color=0x1DB954
            )
            embed.add_field(name="Índice", value=f"#{index}")
            embed.add_field(name="Adicionado por", value=ctx.author.mention)
            
            await ctx.send(embed=embed)
            
        except BotError as e:
            await ctx.send(format_error_for_user(e))
            logger.error(f"[{ctx.guild.id}] {format_error_for_log(e)}")
        except ValueError as e:
            await ctx.send(f"❌ {e}")
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao adicionar favorito: {e}")
            await ctx.send("❌ Erro ao adicionar favorito")
    
    @favorites_group.command(name="rem", aliases=["remove", "delete", "del"])
    async def remove_favorite(self, ctx: commands.Context, index: str):
        """Remove um favorito."""
        try:
            favorites = await favorites_manager.list_all()
            
            # Valida índice
            fav_index = validate_index(index, len(favorites))
            
            # Remove
            favorite = await favorites_manager.remove(fav_index, ctx.guild.id)
            
            embed = discord.Embed(
                title="⭐ Favorito Removido",
                description=f"**{truncate(favorite.title)}**",
                color=0xFF0000
            )
            
            await ctx.send(embed=embed)
            
        except BotError as e:
            await ctx.send(format_error_for_user(e))
        except ValueError as e:
            await ctx.send(f"❌ {e}")
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao remover favorito: {e}")
            await ctx.send("❌ Erro ao remover favorito")
    
    @favorites_group.command(name="lista", aliases=["list", "ls"])
    async def list_favorites(self, ctx: commands.Context):
        """Lista todos os favoritos."""
        try:
            favorites = await favorites_manager.list_all()
            
            if not favorites:
                embed = discord.Embed(
                    title="⭐ Favoritos",
                    description="*Nenhum favorito ainda*",
                    color=0x808080
                )
                await ctx.send(embed=embed)
                return
            
            # Cria embed com favoritos
            description = ""
            for i, fav in enumerate(favorites, 1):
                title_short = truncate(fav.title, 60)
                description += f"**{i}.** {title_short}\n"
                description += f"   └─ Adicionado por {fav.added_by}\n"
            
            embed = discord.Embed(
                title=f"⭐ Favoritos ({len(favorites)})",
                description=description,
                color=0x1DB954
            )
            embed.set_footer(text="Use !tocar favorito <número> para tocar")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"[{ctx.guild.id}] Erro ao listar favoritos: {e}")
            await ctx.send("❌ Erro ao listar favoritos")


async def setup(bot: commands.Bot):
    """Carrega este cog."""
    await bot.add_cog(FavoritesCog(bot))
    logger.info("✓ Cog Favorites carregado")
