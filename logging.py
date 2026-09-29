"""
Sistema de logging estruturado.
Substituiu print() por logging apropriado.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configura o sistema de logging.
    
    Args:
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Arquivo para salvar logs (opcional).
        
    Returns:
        Logger configurado.
    """
    
    # Converte string para nível
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Logger raiz
    logger = logging.getLogger("discord_music_bot")
    logger.setLevel(level)
    
    # Limpa handlers anteriores
    logger.handlers.clear()
    
    # Formato
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (opcional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Silencia loggers do discord.py (muito verbosos)
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger para um módulo específico."""
    return logging.getLogger(f"discord_music_bot.{name}")
