"""
Comando de ajuda customizado.
Lista todos os comandos disponíveis com aliases.
"""

import discord
from discord.ext import commands
import logging


logger = logging.getLogger(__name__)


class HelpCog(commands.Cog):
    """Cog de ajuda."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="ajuda", aliases=["help", "?"])
    async def help_command(self, ctx: commands.Context, *, command: str = ""):
        """Mostra lista de comandos."""
        
        if command:
            # Busca comando específico
            cmd = self.bot.get_command(command.lower())
            if cmd:
                embed = discord.Embed(
                    title=f"📖 Ajuda - {cmd.name}",
                    description=cmd.help or "Sem descrição",
                    color=0x1DB954
                )
                
                if cmd.aliases:
                    embed.add_field(
                        name="Aliases",
                        value=", ".join(cmd.aliases),
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                return
            
            await ctx.send(f"❌ Comando '{command}' não encontrado")
            return
        
        # Lista todos os comandos
        embed = discord.Embed(
            title="🎵 Discord Music Bot - Ajuda",
            description="Aqui estão todos os comandos disponíveis:",
            color=0x1DB954
        )
        
        # Agrupa por categoria
        commands_by_category = {
            "🎶 Reprodução": [
                ("conectar, j, join", "Conecta ao canal de voz"),
                ("tocar, p, play <música>", "Toca uma música (nome, URL ou favorito)"),
                ("pausa", "Pausa a música"),
                ("retomar, r, resume", "Retoma a música pausada"),
                ("proximo, s, next", "Pula para próxima música"),
                ("pular, jmp, jump <pos>", "Pula para posição específica"),
                ("parar, stop", "Para e limpa fila"),
                ("limpar, cl, clear", "Limpa fila (mantém atual)"),
            ],
            "📊 Fila": [
                ("fila, q, queue [página]", "Mostra fila de reprodução"),
                ("ouvindoagora, np, nowplaying", "Mostra música tocando"),
                ("repetir, l, loop [off|song|queue]", "Ativa/desativa loop"),
                ("embaralhar, sh, shuffle", "Embaralha fila"),
                ("voltar, b, prev, previous", "Volta para música anterior"),
            ],
            "🔊 Controles": [
                ("volume, vol <0-100>", "Ajusta volume"),
                ("sair, dc, disconnect", "Desconecta do canal"),
            ],
            "⭐ Favoritos": [
                ("favoritos add <URL>", "Adiciona música aos favoritos"),
                ("favoritos rem <número>", "Remove favorito"),
                ("favoritos lista", "Lista todos favoritos"),
                ("tocar favorito <número>", "Toca um favorito"),
            ],
        }
        
        for category, cmds in commands_by_category.items():
            commands_text = "\n".join(
                f"`!{cmd}` - {desc}" for cmd, desc in cmds
            )
            embed.add_field(
                name=category,
                value=commands_text,
                inline=False
            )
        
        embed.add_field(
            name="💡 Dicas",
            value=(
                "• Use `!ajuda <comando>` para mais informações\n"
                "• Abreviaturas também funcionam (ex: !j = !join)\n"
                "• Playlist URL são suportadas\n"
                "• Busca automática no YouTube"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use !ajuda <comando> para mais detalhes")
        
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Carrega este cog."""
    await bot.add_cog(HelpCog(bot))
    logger.info("✓ Cog Help carregado")
