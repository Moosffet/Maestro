"""
Exceções customizadas do bot.
Separadas em categorias lógicas com mensagens amigáveis.
"""


class BotError(Exception):
    """Exceção base do bot."""
    
    def __init__(self, message: str, user_message: str | None = None):
        """
        Args:
            message: Mensagem técnica para logging.
            user_message: Mensagem amigável para o usuário (padrão: message).
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message


# === Erros de YouTube/yt-dlp ===

class YouTubeError(BotError):
    """Erro ao processar YouTube/yt-dlp."""
    pass


class URLNotFoundError(YouTubeError):
    """URL não foi encontrada."""
    
    def __init__(self):
        super().__init__(
            "URL não encontrada",
            "❌ Não consegui encontrar essa URL. Verifique se o link está correto."
        )


class VideoNotFoundError(YouTubeError):
    """Vídeo não foi encontrado."""
    
    def __init__(self, query: str):
        super().__init__(
            f"Vídeo não encontrado: {query}",
            f"❌ Não encontrei nenhum vídeo para '{query}'. Tente outra busca."
        )


class PlaylistError(YouTubeError):
    """Erro ao processar playlist."""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Erro ao processar playlist: {reason}",
            f"❌ Não consegui carregar a playlist. {reason}"
        )


class StreamError(YouTubeError):
    """Erro ao obter stream do vídeo."""
    
    def __init__(self):
        super().__init__(
            "Falha ao obter stream",
            "❌ Não consegui reproduzir esta música. O vídeo pode estar indisponível."
        )


# === Erros de Reprodução ===

class PlayerError(BotError):
    """Erro de reprodução de áudio."""
    pass


class NotConnectedError(PlayerError):
    """Bot não está conectado a um canal de voz."""
    
    def __init__(self):
        super().__init__(
            "Bot não conectado ao canal de voz",
            "❌ O bot não está em um canal de voz. Use !conectar primeiro."
        )


class QueueEmptyError(PlayerError):
    """Fila de reprodução está vazia."""
    
    def __init__(self):
        super().__init__(
            "Fila vazia",
            "❌ Não há músicas na fila."
        )


class AlreadyPlayingError(PlayerError):
    """Já está tocando uma música."""
    
    def __init__(self):
        super().__init__(
            "Já tocando",
            "🎵 Já estou tocando uma música."
        )


class NotPausedError(PlayerError):
    """Música não está pausada."""
    
    def __init__(self):
        super().__init__(
            "Não pausado",
            "❌ A música não está pausada."
        )


# === Erros de Discord ===

class DiscordError(BotError):
    """Erro relacionado ao Discord."""
    pass


class VoiceChannelError(DiscordError):
    """Erro ao conectar ao canal de voz."""
    
    def __init__(self, reason: str = "desconhecido"):
        super().__init__(
            f"Erro ao conectar ao canal de voz: {reason}",
            f"❌ Não consegui conectar ao canal de voz. {reason}"
        )


class PermissionError(DiscordError):
    """Sem permissão para realizar ação."""
    
    def __init__(self, action: str):
        super().__init__(
            f"Sem permissão: {action}",
            f"❌ Não tenho permissão para {action}."
        )


# === Erros de Favoritos ===

class FavoritesError(BotError):
    """Erro ao gerenciar favoritos."""
    pass


class FavoriteNotFoundError(FavoritesError):
    """Favorito não encontrado."""
    
    def __init__(self, index: int):
        super().__init__(
            f"Favorito {index} não encontrado",
            f"❌ Não encontrei o favorito #{index}."
        )


class InvalidFavoriteError(FavoritesError):
    """Favorito inválido."""
    
    def __init__(self, reason: str = "desconhecido"):
        super().__init__(
            f"Favorito inválido: {reason}",
            f"❌ Favorito inválido. {reason}"
        )


# === Erros de Configuração ===

class ConfigError(BotError):
    """Erro de configuração."""
    pass


class FFmpegNotFoundError(ConfigError):
    """FFmpeg não foi encontrado."""
    
    def __init__(self, path: str):
        super().__init__(
            f"FFmpeg não encontrado: {path}",
            f"❌ FFmpeg não foi encontrado.\n"
            f"   Instale com: sudo dnf install ffmpeg"
        )


def format_error_for_user(error: BotError) -> str:
    """Formata erro para exibir ao usuário (sem detalhes técnicos)."""
    return error.user_message


def format_error_for_log(error: Exception) -> str:
    """Formata erro para logging (com detalhes técnicos)."""
    return f"{type(error).__name__}: {str(error)}"
