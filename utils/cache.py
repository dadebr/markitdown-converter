import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

class FileCache:
    """Sistema de cache para arquivos processados.
    
    Armazena metadados dos arquivos processados para evitar reprocessamento
    desnecessário quando o arquivo não foi modificado.
    """
    
    def __init__(self, cache_dir: str = ".cache", max_age_days: int = 30):
        """Inicializa o sistema de cache.
        
        Args:
            cache_dir: Diretório para armazenar o cache
            max_age_days: Idade máxima dos itens do cache em dias
        """
        self.cache_dir = Path(cache_dir)
        self.max_age_days = max_age_days
        self.cache_file = self.cache_dir / "file_cache.json"
        self.logger = logging.getLogger(__name__)
        
        # Criar diretório de cache se não existir
        self.cache_dir.mkdir(exist_ok=True)
        
        # Carregar cache existente
        self._cache_data = self._load_cache()
        
        # Limpar itens expirados
        self._cleanup_expired()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Carrega dados do cache do arquivo."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Erro ao carregar cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Salva dados do cache no arquivo."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Erro ao salvar cache: {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calcula hash do arquivo para detectar mudanças."""
        try:
            stat = os.stat(file_path)
            # Usar tamanho + data de modificação para hash rápido
            content = f"{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except OSError:
            return ""
    
    def _cleanup_expired(self) -> None:
        """Remove itens expirados do cache."""
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        expired_keys = []
        for key, data in self._cache_data.items():
            if data.get('timestamp', 0) < cutoff_timestamp:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache_data[key]
        
        if expired_keys:
            self.logger.info(f"Removidos {len(expired_keys)} itens expirados do cache")
            self._save_cache()
    
    def is_cached(self, input_path: str, output_path: str) -> bool:
        """Verifica se o arquivo já foi processado e está atualizado.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            
        Returns:
            True se o arquivo está em cache e atualizado
        """
        try:
            # Verificar se arquivo de entrada existe
            if not os.path.exists(input_path):
                return False
            
            # Verificar se arquivo de saída existe
            if not os.path.exists(output_path):
                return False
            
            # Gerar chave do cache
            cache_key = self._get_cache_key(input_path, output_path)
            
            # Verificar se está no cache
            if cache_key not in self._cache_data:
                return False
            
            cached_data = self._cache_data[cache_key]
            
            # Verificar se o hash do arquivo mudou
            current_hash = self._get_file_hash(input_path)
            if current_hash != cached_data.get('file_hash', ''):
                return False
            
            # Verificar se não expirou
            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
            if cached_data.get('timestamp', 0) < cutoff_date.timestamp():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar cache: {e}")
            return False
    
    def add_to_cache(self, input_path: str, output_path: str, 
                    conversion_options: Optional[Dict] = None) -> None:
        """Adiciona arquivo ao cache.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída
            conversion_options: Opções usadas na conversão
        """
        try:
            cache_key = self._get_cache_key(input_path, output_path)
            
            self._cache_data[cache_key] = {
                'input_path': input_path,
                'output_path': output_path,
                'file_hash': self._get_file_hash(input_path),
                'timestamp': datetime.now().timestamp(),
                'conversion_options': conversion_options or {}
            }
            
            self._save_cache()
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar ao cache: {e}")
    
    def _get_cache_key(self, input_path: str, output_path: str) -> str:
        """Gera chave única para o cache."""
        key_content = f"{input_path}_{output_path}"
        return hashlib.md5(key_content.encode()).hexdigest()
    
    def remove_from_cache(self, input_path: str, output_path: str) -> None:
        """Remove arquivo do cache."""
        try:
            cache_key = self._get_cache_key(input_path, output_path)
            if cache_key in self._cache_data:
                del self._cache_data[cache_key]
                self._save_cache()
        except Exception as e:
            self.logger.error(f"Erro ao remover do cache: {e}")
    
    def clear_cache(self) -> None:
        """Limpa todo o cache."""
        self._cache_data.clear()
        self._save_cache()
        self.logger.info("Cache limpo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        return {
            'total_items': len(self._cache_data),
            'cache_file': str(self.cache_file),
            'max_age_days': self.max_age_days
        }