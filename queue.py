"""
Gerenciamento de fila de reprodução.
Cada servidor (guild) tem seu próprio estado isolado.
Usa locks para evitar race conditions.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional, List
from collections import deque
import logging

from services.youtube import VideoInfo


logger = logging.getLogger(__name__)


@dataclass
class QueueItem:
    """Item na fila de reprodução."""
    video_id: str
    title: str
    duration: int
    uploader: str
    url: str
    added_by: str
    added_by_id: int


@dataclass
class GuildQueue:
    """Estado da fila de um servidor específico."""
    
    guild_id: int
    
    # Controle de acesso
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    # Fila
    queue: deque[QueueItem] = field(default_factory=deque)
    current: Optional[QueueItem] = None
    history: deque[QueueItem] = field(default_factory=deque)
    
    # Estado
    is_playing: bool = False
    is_paused: bool = False
    loop: int = 0  # 0=off, 1=song, 2=queue
    volume: int = 100
    
    # Voz
    voice_channel_id: Optional[int] = None
    
    # Timers
    idle_task: Optional[asyncio.Task] = None
    skip_history: deque = field(default_factory=deque)  # para undo
    
    @property
    def total_duration(self) -> int:
        """Duração total da fila em segundos."""
        total = sum(item.duration for item in self.queue)
        if self.current:
            total += self.current.duration
        return total
    
    @property
    def queue_size(self) -> int:
        """Quantidade de itens na fila."""
        return len(self.queue) + (1 if self.current else 0)
    
    async def add(self, item: QueueItem) -> int:
        """
        Adiciona item à fila.
        
        Args:
            item: Item a adicionar.
            
        Returns:
            Posição na fila (1-based).
        """
        async with self.lock:
            self.queue.append(item)
            position = len(self.queue) + (1 if self.current else 0)
            logger.info(f"[{self.guild_id}] Adicionado à fila (#{position}): {item.title}")
            return position
    
    async def add_batch(self, items: List[QueueItem]) -> tuple[int, int]:
        """
        Adiciona vários itens.
        
        Args:
            items: Itens a adicionar.
            
        Returns:
            Tupla (posição_inicio, quantidade).
        """
        async with self.lock:
            start_pos = len(self.queue) + (1 if self.current else 0)
            self.queue.extend(items)
            count = len(items)
            logger.info(f"[{self.guild_id}] Adicionado lote de {count} itens à fila")
            return start_pos, count
    
    async def pop_next(self) -> Optional[QueueItem]:
        """
        Remove e retorna próximo item da fila.
        Move item atual para histórico.
        
        Returns:
            Próximo item ou None se fila vazia.
        """
        async with self.lock:
            if self.current and len(self.history) < 50:  # Limita histórico
                self.history.append(self.current)
            
            if self.queue:
                self.current = self.queue.popleft()
                logger.debug(f"[{self.guild_id}] Próximo: {self.current.title}")
                return self.current
            
            self.current = None
            return None
    
    async def skip(self, count: int = 1) -> Optional[QueueItem]:
        """
        Pula músicas.
        
        Args:
            count: Quantidade a pular.
            
        Returns:
            Próximo item após pulo.
        """
        async with self.lock:
            # Pula
            for _ in range(count - 1):
                if self.queue:
                    skipped = self.queue.popleft()
                    self.skip_history.append(skipped)
            
            # Retorna próximo
            if self.queue:
                self.current = self.queue.popleft()
                logger.info(f"[{self.guild_id}] Pulado para: {self.current.title}")
                return self.current
            
            self.current = None
            return None
    
    async def previous(self) -> Optional[QueueItem]:
        """
        Volta para música anterior.
        
        Returns:
            Música anterior ou None.
        """
        async with self.lock:
            if not self.history:
                return None
            
            # Move atual de volta para fila
            if self.current:
                self.queue.appendleft(self.current)
            
            # Restaura anterior
            self.current = self.history.pop()
            logger.info(f"[{self.guild_id}] Voltado para: {self.current.title}")
            return self.current
    
    async def remove_at(self, index: int) -> Optional[QueueItem]:
        """
        Remove item em posição específica.
        
        Args:
            index: Posição (1-based).
            
        Returns:
            Item removido ou None.
        """
        async with self.lock:
            if index == 1 and self.current:
                item = self.current
                self.current = None
            elif index - (1 if self.current else 0) > 0:
                pos = index - (1 if self.current else 0) - 1
                if 0 <= pos < len(self.queue):
                    items = list(self.queue)
                    item = items.pop(pos)
                    self.queue = deque(items)
                    logger.info(f"[{self.guild_id}] Removido (#{index}): {item.title}")
                    return item
            
            return None
    
    async def clear(self) -> None:
        """Limpa a fila (mantém música atual)."""
        async with self.lock:
            count = len(self.queue)
            self.queue.clear()
            logger.info(f"[{self.guild_id}] Fila limpa ({count} itens removidos)")
    
    async def shuffle(self) -> None:
        """Embaralha a fila."""
        async with self.lock:
            import random
            items = list(self.queue)
            random.shuffle(items)
            self.queue = deque(items)
            logger.info(f"[{self.guild_id}] Fila embaralhada")
    
    async def get_page(self, page: int = 1, per_page: int = 10) -> tuple[List[QueueItem], int]:
        """
        Retorna página da fila para exibição.
        
        Args:
            page: Página (1-based).
            per_page: Itens por página.
            
        Returns:
            Tupla (itens, total_pages).
        """
        async with self.lock:
            items = list(self.queue)
            total = len(items)
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            
            start = (page - 1) * per_page
            end = start + per_page
            
            page_items = items[start:end]
            
            return page_items, total_pages
    
    async def reset(self) -> None:
        """Reseta fila completamente."""
        async with self.lock:
            self.queue.clear()
            self.current = None
            self.history.clear()
            self.skip_history.clear()
            self.is_playing = False
            self.is_paused = False
            self.loop = 0
            self.voice_channel_id = None
            logger.info(f"[{self.guild_id}] Fila resetada")


class QueueManager:
    """Gerenciador de filas de todos os servidores."""
    
    def __init__(self):
        self.queues: dict[int, GuildQueue] = {}
        self.global_lock = asyncio.Lock()
    
    async def get_queue(self, guild_id: int) -> GuildQueue:
        """Obtém fila de um servidor, criando se não existir."""
        if guild_id not in self.queues:
            async with self.global_lock:
                if guild_id not in self.queues:
                    self.queues[guild_id] = GuildQueue(guild_id=guild_id)
        
        return self.queues[guild_id]
    
    async def delete_queue(self, guild_id: int) -> None:
        """Remove fila de um servidor."""
        if guild_id in self.queues:
            queue = self.queues[guild_id]
            await queue.reset()
            del self.queues[guild_id]
            logger.info(f"[{guild_id}] Fila deletada")


# Instância global
queue_manager = QueueManager()
