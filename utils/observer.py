"""Implementação do padrão Observer para atualizações de progresso."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import threading


class Observer(ABC):
    """Interface para observadores."""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Método chamado quando um evento é notificado.
        
        Args:
            event_type: Tipo do evento (ex: 'progress', 'error', 'complete')
            data: Dados do evento
        """
        pass


class Subject:
    """Classe base para objetos observáveis."""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._lock = threading.Lock()
    
    def attach(self, observer: Observer) -> None:
        """Adiciona um observador."""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Remove um observador."""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Notifica todos os observadores sobre um evento."""
        if data is None:
            data = {}
        
        with self._lock:
            observers_copy = self._observers.copy()
        
        # Notificar fora do lock para evitar deadlocks
        for observer in observers_copy:
            try:
                observer.update(event_type, data)
            except Exception as e:
                # Log do erro mas não interrompe outros observadores
                print(f"Erro ao notificar observador: {e}")


class ProgressObserver(Observer):
    """Observador específico para atualizações de progresso."""
    
    def __init__(self, progress_callback=None, status_callback=None, error_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.error_callback = error_callback
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Processa diferentes tipos de eventos."""
        if event_type == 'progress' and self.progress_callback:
            completed = data.get('completed', 0)
            total = data.get('total', 1)
            current_file = data.get('current_file', '')
            self.progress_callback(completed, total, current_file)
        
        elif event_type == 'status' and self.status_callback:
            message = data.get('message', '')
            self.status_callback(message)
        
        elif event_type == 'error' and self.error_callback:
            error = data.get('error', '')
            file_path = data.get('file', '')
            self.error_callback(error, file_path)
        
        elif event_type == 'file_complete' and self.status_callback:
            file_path = data.get('file', '')
            success = data.get('success', False)
            output_file = data.get('output_file', '')
            if success:
                self.status_callback(f"✓ Concluído: {output_file}")
            else:
                error = data.get('error', 'Erro desconhecido')
                self.status_callback(f"❌ Falha em {file_path}: {error}")


class EventBus(Subject):
    """Sistema centralizado de eventos usando padrão Observer."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementação Singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
    
    def emit(self, event_type: str, **kwargs) -> None:
        """Emite um evento para todos os observadores."""
        self.notify(event_type, kwargs)
    
    def subscribe(self, observer: Observer) -> None:
        """Inscreve um observador no bus de eventos."""
        self.attach(observer)
    
    def unsubscribe(self, observer: Observer) -> None:
        """Remove um observador do bus de eventos."""
        self.detach(observer)