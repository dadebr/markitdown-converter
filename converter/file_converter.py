#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Converter - Markitdown Converter

Módulo responsável pela conversão de arquivos individuais para Markdown.
Suporta vários formatos: PDF, DOCX, PPTX, XLSX, JSON, TXT, CSV.

Author: dadebr
GitHub: https://github.com/dadebr/markitdown-converter
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from markitdown import MarkItDown
except ImportError:
    print("Erro: markitdown não está instalado. Execute: pip install markitdown")
    sys.exit(1)

from utils.logger import get_logger
from utils.file_handler import FileHandler

class FileConverter:
    """
    Classe para conversão de arquivos individuais para Markdown
    """
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'PDF Document',
        '.docx': 'Word Document', 
        '.pptx': 'PowerPoint Presentation',
        '.xlsx': 'Excel Spreadsheet',
        '.json': 'JSON File',
        '.txt': 'Text File',
        '.csv': 'CSV File'
    }
    
    def __init__(self, log_callback=None):
        """
        Inicializa o conversor de arquivos.
        Args:
            log_callback (function, optional): Função de callback para logs.
        """
        self.log_callback = log_callback
        self.logger = get_logger(__name__) if log_callback is None else None
        self.file_handler = FileHandler()
        self.markitdown = MarkItDown()

    def _log(self, message, level='info'):
        """
        Registra uma mensagem de log usando o callback ou o logger padrão.
        """
        if self.log_callback:
            self.log_callback(message)
        elif self.logger:
            getattr(self.logger, level)(message)
        
    def is_supported_file(self, file_path: str) -> bool:
        """
        Verifica se o arquivo é suportado
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            bool: True se suportado, False caso contrário
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.SUPPORTED_EXTENSIONS
    
    def get_file_type(self, file_path: str) -> str:
        """
        Obtém o tipo do arquivo
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            str: Tipo do arquivo ou 'Unknown'
        """
        file_ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(file_ext, 'Unknown')
    
    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Converte um arquivo para Markdown
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída (opcional)
            
        Returns:
            str: Caminho do arquivo convertido ou None se falhar
        """
        try:
            input_file = Path(input_path)
            
            # Verificar se o arquivo existe
            if not input_file.exists():
                self._log(f"Arquivo não encontrado: {input_path}", level='error')
                return None
                
            # Verificar se o arquivo é suportado
            if not self.is_supported_file(input_path):
                file_ext = input_file.suffix.lower()
                self._log(f"Formato não suportado: {file_ext}", level='error')
                return None
            
            # Definir arquivo de saída se não especificado
            if output_path is None:
                output_path = input_file.with_suffix('.md')
            else:
                output_path = Path(output_path)
                
            # Criar diretório de saída se necessário
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._log(f"Convertendo {input_file.name} ({self.get_file_type(input_path)})...")
            
            # Realizar a conversão
            try:
                result = self.markitdown.convert(str(input_path))
                markdown_content = result.text_content
                
                if not markdown_content:
                    self._log(f"Conteúdo vazio após conversão: {input_path}", level='warning')
                    return None
                    
            except Exception as e:
                self._log(f"Erro durante a conversão: {str(e)}", level='error')
                return None
            
            # Salvar o arquivo markdown
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                    
                self._log(f"Arquivo convertido salvo em: {output_path}")
                return str(output_path)
                
            except Exception as e:
                self._log(f"Erro ao salvar arquivo: {str(e)}", level='error')
                return None
                
        except Exception as e:
            self._log(f"Erro inesperado durante conversão: {str(e)}", level='error')
            return None
    
    def get_conversion_info(self, file_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um arquivo para conversão
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            dict: Informações do arquivo
        """
        file_info = self.file_handler.get_file_info(file_path)
        file_info['supported'] = self.is_supported_file(file_path)
        file_info['type'] = self.get_file_type(file_path)
        
        return file_info
