"""
Configuração centralizada do bot musical Discord.
Carrega variáveis do .env e valida na inicialização.
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv


# Carrega variáveis do .env
load_dotenv()


@dataclass
class Settings:
    """Configurações do bot."""
    
    # Discord
    discord_token: str
    prefix: str
    
    # Diretório de dados
    data_dir: Path
    
    # yt-dlp
    bgutil_url: str | None
    cookies_file: str | None
    
    # FFmpeg
    ffmpeg_path: str
    
    # Fila e inatividade
    playlist_limit: int
    idle_timeout: int
    
    # Logging
    log_level: str
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Carrega configurações do .env e valida.
        
        Raises:
            RuntimeError: Se uma variável obrigatória estiver ausente.
        """
        
        # Variáveis obrigatórias
        discord_token = os.getenv("DISCORD_TOKEN", "").strip()
        if not discord_token:
            raise RuntimeError(
                "❌ DISCORD_TOKEN não está configurado no .env\n"
                "   Adicione: DISCORD_TOKEN=seu_token_aqui"
            )
        
        # Variáveis com padrão
        prefix = os.getenv("PREFIX", "!").strip()
        data_dir = Path(os.getenv("DATA_DIR", "./data")).expanduser()
        
        bgutil_url = os.getenv("BGUTIL_URL", "").strip() or None
        cookies_file = os.getenv("COOKIES_FILE", "").strip() or None
        
        ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg").strip()
        
        try:
            playlist_limit = int(os.getenv("PLAYLIST_LIMIT", "200"))
            if playlist_limit < 1:
                raise ValueError("PLAYLIST_LIMIT deve ser >= 1")
        except ValueError as e:
            raise RuntimeError(f"❌ PLAYLIST_LIMIT inválido: {e}")
        
        try:
            idle_timeout = int(os.getenv("IDLE_TIMEOUT", "60"))
            if idle_timeout < 10:
                raise ValueError("IDLE_TIMEOUT deve ser >= 10")
        except ValueError as e:
            raise RuntimeError(f"❌ IDLE_TIMEOUT inválido: {e}")
        
        log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise RuntimeError(
                f"❌ LOG_LEVEL inválido: {log_level}\n"
                "   Use: DEBUG, INFO, WARNING, ERROR ou CRITICAL"
            )
        
        return cls(
            discord_token=discord_token,
            prefix=prefix,
            data_dir=data_dir,
            bgutil_url=bgutil_url,
            cookies_file=cookies_file,
            ffmpeg_path=ffmpeg_path,
            playlist_limit=playlist_limit,
            idle_timeout=idle_timeout,
            log_level=log_level,
        )


def validate_environment() -> Settings:
    """
    Valida o ambiente de execução.
    
    Returns:
        Settings: Configurações validadas.
        
    Raises:
        RuntimeError: Se o ambiente não atender aos requisitos.
    """
    import shutil
    import logging
    
    # Carrega configurações
    settings = Settings.from_env()
    
    # Verifica Python
    python_version = sys.version_info
    if python_version < (3, 11):
        raise RuntimeError(
            f"❌ Python 3.11+ necessário. Versão atual: {python_version.major}.{python_version.minor}"
        )
    
    # Verifica FFmpeg
    if not shutil.which(settings.ffmpeg_path):
        raise RuntimeError(
            f"❌ FFmpeg não encontrado em: {settings.ffmpeg_path}\n"
            "   Instale no Fedora com: sudo dnf install ffmpeg\n"
            "   Ou configure o caminho correto em FFMPEG_PATH no .env"
        )
    
    # Verifica diretório de dados
    try:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise RuntimeError(
            f"❌ Sem permissão para criar: {settings.data_dir}\n"
            "   Verifique as permissões de escrita do diretório."
        )
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao criar diretório de dados: {e}")
    
    return settings


# Instância global (carregada em bot.py)
settings: Settings | None = None


def init_settings() -> Settings:
    """Inicializa e retorna as configurações validadas."""
    global settings
    settings = validate_environment()
    return settings
