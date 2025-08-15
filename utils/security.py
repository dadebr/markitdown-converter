"""Módulo de segurança para validação e sanitização de entrada."""

import os
import re
from pathlib import Path
from typing import Optional, List


class SecurityValidator:
    """Classe para validação de segurança e sanitização de entrada."""
    
    # Caracteres perigosos para nomes de arquivo
    DANGEROUS_CHARS = r'[<>:"/\|?*\x00-\x1f]'
    
    # Nomes de arquivo reservados no Windows
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # Extensões de arquivo permitidas
    ALLOWED_EXTENSIONS = {
        '.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.csv', '.json', '.md'
    }
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Valida se um caminho de arquivo é seguro.
        
        Args:
            file_path: Caminho do arquivo a ser validado
            
        Returns:
            True se o caminho é válido e seguro, False caso contrário
        """
        if not file_path or not isinstance(file_path, str):
            return False
            
        try:
            path = Path(file_path).resolve()
            
            # Verificar se o arquivo existe
            if not path.exists():
                return False
                
            # Verificar se é um arquivo (não diretório)
            if not path.is_file():
                return False
                
            # Verificar extensão permitida
            if path.suffix.lower() not in SecurityValidator.ALLOWED_EXTENSIONS:
                return False
                
            # Verificar se não há path traversal
            if '..' in str(path) or str(path).startswith('/'):
                return False
                
            return True
            
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def validate_directory_path(dir_path: str) -> bool:
        """Valida se um caminho de diretório é seguro.
        
        Args:
            dir_path: Caminho do diretório a ser validado
            
        Returns:
            True se o caminho é válido e seguro, False caso contrário
        """
        if not dir_path or not isinstance(dir_path, str):
            return False
            
        try:
            path = Path(dir_path).resolve()
            
            # Verificar se o diretório existe
            if not path.exists():
                return False
                
            # Verificar se é um diretório
            if not path.is_dir():
                return False
                
            # Verificar se não há path traversal
            if '..' in str(path):
                return False
                
            # Verificar permissões de escrita
            if not os.access(path, os.W_OK):
                return False
                
            return True
            
        except (OSError, ValueError):
            return False
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """Sanitiza um nome de arquivo removendo caracteres perigosos.
        
        Args:
            filename: Nome do arquivo a ser sanitizado
            max_length: Comprimento máximo do nome do arquivo
            
        Returns:
            Nome do arquivo sanitizado
        """
        if not filename or not isinstance(filename, str):
            return "arquivo_sem_nome"
            
        # Remover caracteres perigosos
        sanitized = re.sub(SecurityValidator.DANGEROUS_CHARS, '_', filename)
        
        # Remover espaços no início e fim
        sanitized = sanitized.strip()
        
        # Verificar nomes reservados
        name_without_ext = Path(sanitized).stem.upper()
        if name_without_ext in SecurityValidator.RESERVED_NAMES:
            sanitized = f"file_{sanitized}"
            
        # Limitar comprimento
        if len(sanitized) > max_length:
            name = Path(sanitized).stem
            ext = Path(sanitized).suffix
            max_name_length = max_length - len(ext)
            sanitized = name[:max_name_length] + ext
            
        # Garantir que não termine com ponto ou espaço
        sanitized = sanitized.rstrip('. ')
        
        # Se ficou vazio, usar nome padrão
        if not sanitized:
            sanitized = "arquivo_sanitizado"
            
        return sanitized
    
    @staticmethod
    def validate_file_list(file_paths: List[str]) -> List[str]:
        """Valida uma lista de caminhos de arquivo.
        
        Args:
            file_paths: Lista de caminhos de arquivo
            
        Returns:
            Lista de caminhos válidos
        """
        if not file_paths or not isinstance(file_paths, list):
            return []
            
        valid_files = []
        for file_path in file_paths:
            if SecurityValidator.validate_file_path(file_path):
                valid_files.append(file_path)
                
        return valid_files
    
    @staticmethod
    def check_file_permissions(file_path: str) -> dict:
        """Verifica as permissões de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com informações de permissões
        """
        permissions = {
            'readable': False,
            'writable': False,
            'executable': False,
            'exists': False
        }
        
        try:
            path = Path(file_path)
            if path.exists():
                permissions['exists'] = True
                permissions['readable'] = os.access(path, os.R_OK)
                permissions['writable'] = os.access(path, os.W_OK)
                permissions['executable'] = os.access(path, os.X_OK)
                
        except (OSError, ValueError):
            pass
            
        return permissions
    
    @staticmethod
    def get_safe_output_path(input_path: str, output_dir: str, new_extension: str = '.md') -> Optional[str]:
        """Gera um caminho de saída seguro para um arquivo.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_dir: Diretório de saída
            new_extension: Nova extensão do arquivo
            
        Returns:
            Caminho de saída seguro ou None se inválido
        """
        if not SecurityValidator.validate_file_path(input_path):
            return None
            
        if not SecurityValidator.validate_directory_path(output_dir):
            return None
            
        try:
            input_file = Path(input_path)
            output_name = input_file.stem + new_extension
            sanitized_name = SecurityValidator.sanitize_filename(output_name)
            
            output_path = Path(output_dir) / sanitized_name
            
            # Verificar se o arquivo já existe e gerar nome único se necessário
            counter = 1
            original_path = output_path
            while output_path.exists():
                name_part = original_path.stem
                ext_part = original_path.suffix
                output_path = original_path.parent / f"{name_part}_{counter}{ext_part}"
                counter += 1
                
            return str(output_path)
            
        except (OSError, ValueError):
            return None