"""
Discord Music Bot - Arquivo Principal
Inicializa todas as configurações, services e cogs.
"""

import asyncio
import sys
import logging
from pathlib import Path

import discord
from discord.ext import commands

# Importações locais
import config
from config import Settings
from utils.logging import setup_logging, get_logger
from utils.persistence import ensure_dir_exists
from services.favorites import init_favorites
from services.player import init_player_manager
from services.queue import queue_manager


logger = logging.getLogger(__name__)


def print_banner():
    """Exibe banner inicial."""
    banner = """
╔══════════════════════════════════════════════╗
║     🎵 Discord Music Bot v2.0               ║
║     Refatoração Completa                    ║
╚══════════════════════════════════════════════╝
"""
    print(banner)


async def load_cogs(bot: commands.Bot) -> None:
    """Carrega todos os cogs."""
    cogs = ["cogs.music", "cogs.favorites", "cogs.help"]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
        except Exception as e:
            logger.error(f"Erro ao carregar cog {cog}: {e}", exc_info=True)
            raise


async def validate_setup() -> Settings:
    """
    Valida o ambiente de execução.
    Mostra status de inicialização.
    """
    print_banner()
    
    print("📋 Validando ambiente...\n")
    
    # Carrega configurações
    try:
        settings = config.init_settings()
    except RuntimeError as e:
        print(f"\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro ao carregar configurações: {e}")
        sys.exit(1)
    
    # Mostra status
    checks = []
    
    # Python
    python_ok = sys.version_info >= (3, 11)
    checks.append(("✓ Python" if python_ok else "✗ Python", python_ok))
    
    # Token
    token_ok = bool(settings.discord_token)
    checks.append(("✓ Discord Token" if token_ok else "✗ Discord Token", token_ok))
    
    # FFmpeg
    import shutil
    ffmpeg_ok = shutil.which(settings.ffmpeg_path) is not None
    checks.append(("✓ FFmpeg" if ffmpeg_ok else "✗ FFmpeg", ffmpeg_ok))
    
    # Data dir
    data_dir_ok = False
    try:
        ensure_dir_exists(settings.data_dir)
        data_dir_ok = True
        checks.append(("✓ Diretório de dados", True))
    except Exception as e:
        checks.append(("✗ Diretório de dados", False))
        logger.error(f"Erro ao criar diretório: {e}")
    
    # Mostra checks
    for status, ok in checks:
        print(status)
    
    # Valida
    if not all(ok for _, ok in checks):
        print("\n❌ Ambiente inválido. Verifique os erros acima.")
        sys.exit(1)
    
    print("\n✓ Configuração carregada")
    print(f"  Prefix: {settings.prefix}")
    print(f"  Data dir: {settings.data_dir}")
    print(f"  Playlist limit: {settings.playlist_limit}")
    print(f"  Idle timeout: {settings.idle_timeout}s")
    
    if settings.bgutil_url:
        print(f"  BGUtil: {settings.bgutil_url}")
    
    print("\n🚀 Iniciando bot...\n")
    
    return settings


class MusicBot(commands.Bot):
    """Bot principal com eventos customizados."""
    
    def __init__(self, settings: Settings, **kwargs):
        self.settings = settings
        super().__init__(**kwargs)
    
    async def on_ready(self):
        """Evento: bot está pronto."""
        logger.info(f"✓ Bot conectado como {self.user}")
        logger.info(f"  ID: {self.user.id}")
        logger.info(f"  Servidores: {len(self.guilds)}")
    
    async def on_guild_join(self, guild: discord.Guild):
        """Evento: bot entrou em um servidor."""
        logger.info(f"✓ Entrou no servidor: {guild.name} ({guild.id})")
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Evento: bot saiu de um servidor."""
        logger.info(f"✗ Saiu do servidor: {guild.name} ({guild.id})")
        
        # Limpa estado do servidor
        try:
            await queue_manager.delete_queue(guild.id)
        except Exception as e:
            logger.error(f"Erro ao limpar fila: {e}")
    
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Evento: usuário entrou/saiu de canal de voz."""
        # Desconecta se bot ficar sozinho (implementar idle timeout)
        if not member.bot and before.channel and not after.channel:
            # Membro saiu de canal
            if member.guild.voice_client and member.guild.voice_client.channel:
                channel = member.guild.voice_client.channel
                
                # Verifica se tem alguém no canal
                members_in_channel = [
                    m for m in channel.members if not m.bot
                ]
                
                if not members_in_channel:
                    logger.info(f"[{member.guild.id}] Ninguém no canal. Desconectando...")
                    queue = await queue_manager.get_queue(member.guild.id)
                    await queue.reset()
                    await member.guild.voice_client.disconnect()
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Trata erros de comando."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"❌ Comando não encontrado. Use `{self.settings.prefix}ajuda`")
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Argumentos faltando. Use `{self.settings.prefix}ajuda {ctx.command.name}`")
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Aguarde {error.retry_after:.1f}s")
        
        else:
            logger.error(f"Erro não tratado: {error}", exc_info=True)
            await ctx.send("❌ Erro ao executar comando")


async def main():
    """Função principal."""
    
    # Valida setup
    settings = await validate_setup()
    
    # Setup logging
    setup_logging(
        log_level=settings.log_level,
        log_file=settings.data_dir / "bot.log",
    )
    
    logger = get_logger("bot")
    
    # Inicializa services
    logger.info("Inicializando services...")
    init_player_manager(settings.ffmpeg_path)
    init_favorites(settings.data_dir)
    
    # Intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.reactions = True
    intents.guild_messages = True
    intents.dm_messages = True
    
    # Cria bot
    bot = MusicBot(
        settings=settings,
        command_prefix=settings.prefix,
        intents=intents,
        help_command=None,  # Usa comando customizado
    )
    
    # Carrega cogs
    logger.info("Carregando cogs...")
    await load_cogs(bot)
    logger.info("✓ Cogs carregados")
    
    # Conecta ao Discord
    try:
        logger.info("Conectando ao Discord...")
        await bot.start(settings.discord_token)
    except discord.LoginFailure:
        logger.error("❌ Token de Discord inválido")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
        await bot.close()
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot desligado")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}", file=sys.stderr)
        sys.exit(1)
