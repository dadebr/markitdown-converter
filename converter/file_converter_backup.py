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
from typing import Optional, Dict, Any, List, Callable

import pdfplumber
import re
from unstructured.partition.pdf import partition_pdf

try:
    from markitdown import MarkItDown
except ImportError:
    print("Erro: markitdown não está instalado. Execute: pip install markitdown")
    sys.exit(1)

from utils.logger import get_logger
from utils.file_handler import FileHandler
from utils.security import SecurityValidator
from utils.cache import FileCache
from utils.async_processor import AsyncProcessor

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
    
    def __init__(self, log_callback=None, use_cache=True, max_workers=4):
        """
        Inicializa o conversor de arquivos.
        Args:
            log_callback (function, optional): Função de callback para logs.
            use_cache (bool): Se deve usar sistema de cache.
            max_workers (int): Número máximo de threads para processamento assíncrono.
        """
        self.log_callback = log_callback
        self.logger = get_logger(__name__) if log_callback is None else None
        self.file_handler = FileHandler()
        self.markitdown = MarkItDown()
        self.use_cache = use_cache
        self.cache = FileCache() if use_cache else None
        self.async_processor = AsyncProcessor(max_workers=max_workers, log_callback=log_callback)

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
    
    def clean_text(self, text):
        """Limpa e formata o texto extraído com melhorias robustas para corrigir palavras incompletas."""
        if not text:
            return ""
        
        # 1. Corrigir caracteres duplicados e malformados
        text = self._fix_duplicate_characters(text)
        
        # 2. Reconstruir palavras fragmentadas
        text = self._reconstruct_fragmented_words(text)
        
        # 3. Unir palavras divididas por hifens ou quebras de linha
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # 4. Corrigir fragmentação de texto - unir linhas que não terminam com pontuação
        text = re.sub(r'([^.!?:])\n([a-z])', r'\1 \2', text)
        
        # 5. Unir texto dividido por espaços inadequados
        text = self._join_split_text(text)
        
        # 6. Normalizar espaçamento - remover quebras excessivas mas preservar parágrafos
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 7. Remover números de linha e marcadores indesejados
        text = re.sub(r'^\d+\s*\|', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # 8. Corrigir espaçamento irregular
        text = re.sub(r'\s+', ' ', text)  # Múltiplos espaços para um
        text = re.sub(r'\n ', '\n', text)  # Remover espaços no início de linhas
        
        # 9. Preservar quebras de parágrafo importantes
        text = re.sub(r'([.!?])\s*\n([A-Z])', r'\1\n\n\2', text)
        
        # 10. Validação final de qualidade
        text = self._validate_text_quality(text)
        
        return text.strip()
    
    def _fix_duplicate_characters(self, text):
        """Corrige caracteres duplicados e malformados."""
        if not text:
            return ""
        
        # Corrigir caracteres duplicados consecutivos (ex: 'ôônniibbuuss' -> 'ônibus')
        text = re.sub(r'(.)\1{2,}', r'\1', text)
        
        # Corrigir padrões específicos de duplicação
        text = re.sub(r'([aeiouáéíóúâêîôûàèìòùãõç])\1+', r'\1', text, flags=re.IGNORECASE)
        
        # Corrigir sequências malformadas comuns
        text = re.sub(r'ccoomm', 'com', text, flags=re.IGNORECASE)
        text = re.sub(r'lluuggaarreess', 'lugares', text, flags=re.IGNORECASE)
        text = re.sub(r'ppeerrííooddoo', 'período', text, flags=re.IGNORECASE)
        
        return text
    
    def _reconstruct_fragmented_words(self, text):
        """Reconstrói palavras fragmentadas usando análise de contexto."""
        if not text:
            return ""
        
        # Dicionário de palavras comuns fragmentadas
        word_fragments = {
            r'\bREPÚ\s+BLICA\b': 'REPÚBLICA',
            r'\bCONTROLA\s+DORIA\b': 'CONTROLADORIA',
            r'\bCÓ\s+DIGO\b': 'CÓDIGO',
            r'\bGESTÃO\s+DE\s+RECURSOS\s+HUMA\b': 'GESTÃO DE RECURSOS HUMANOS',
            r'\bGESTÃO\s+DO\s+SUPRIMENTO\s+DE\s+B\b': 'GESTÃO DO SUPRIMENTO DE BENS',
            r'\bCU\s+ÇÃO\b': 'CUÇÃO',
            r'\bseguridade\s+soc\s+ial\b': 'seguridade social',
            r'\bcontr\s+n\b': 'contrn',
            r'\bNega\s+tiva\b': 'Negativa',
            r'\bap\s+con\b': 'apcon',
            r'\bor\s+encont\s+rava\b': 'or encontrava',
            r'\bentanto\s+as\b': 'entanto as',
            r'\batualização\s+tidões\b': 'atualização tidões',
            r'\bivado\s+et\b': 'ivado et',
            r'\btratada\s+seguridade\b': 'tratada seguridade',
            r'\beixamos\s+ecedor\b': 'eixamos ecedor',
            r'\bente\s+ava\s+ar\s+mento\b': 'ente ava ar mento',
            r'\blaridade\s+onforme\b': 'laridade onforme',
            r'\brico\s+ferente\b': 'rico ferente',
            r'\bresa\s+ônibus\b': 'resa ônibus'
        }
        
        # Aplicar correções de fragmentos
        for pattern, replacement in word_fragments.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Corrigir fragmentação de palavras simples (letras isoladas)
        text = re.sub(r'\b([a-záéíóúâêîôûàèìòùãõç])\s+([a-záéíóúâêîôûàèìòùãõç]{2,})\b', r'\1\2', text, flags=re.IGNORECASE)
        
        return text
    
    def _join_split_text(self, text):
        """Une texto dividido inadequadamente."""
        if not text:
            return ""
        
        # Unir palavras que foram divididas por espaços
        text = re.sub(r'\b([a-záéíóúâêîôûàèìòùãõç]{1,2})\s+([a-záéíóúâêîôûàèìòùãõç]{2,})\b', r'\1\2', text, flags=re.IGNORECASE)
        
        # Corrigir números fragmentados
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
        text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', text)
        text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', text)
        
        # Unir prefixos comuns
        text = re.sub(r'\b(an|con|des|pre|pro|sub|super)\s+([a-záéíóúâêîôûàèìòùãõç]{3,})\b', r'\1\2', text, flags=re.IGNORECASE)
        
        return text
    
    def _validate_text_quality(self, text):
        """Valida e melhora a qualidade final do texto com verificações aprimoradas."""
        if not text:
            return ""
        
        quality_issues = []
        
        # Verificar se há muitas palavras fragmentadas
        words = text.split()
        if words:
            short_words = [w for w in words if len(w) <= 2 and w.isalpha()]
            fragmentation_ratio = len(short_words) / len(words)
            
            if fragmentation_ratio > 0.25:  # Mais de 25% de palavras muito curtas
                quality_issues.append(f"Alta fragmentação: {fragmentation_ratio:.2%}")
        
        # Verificar caracteres duplicados excessivos
        duplicate_pattern = re.compile(r'(.)\1{4,}')
        duplicate_matches = duplicate_pattern.findall(text)
        if duplicate_matches:
            quality_issues.append(f"Caracteres duplicados: {len(duplicate_matches)} ocorrências")
        
        # Verificar palavras incompletas comuns
        incomplete_patterns = [
            r'\b[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]{1,3}\b',  # Palavras muito curtas em maiúscula
            r'\b\w{1,2}[çãõáéíóúâêîôûàèìòù]\b',    # Palavras curtas com acentos
            r'\b[bcdfghjklmnpqrstvwxyz]{3,}\b',      # Sequências de consoantes
        ]
        
        incomplete_count = 0
        for pattern in incomplete_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            incomplete_count += len(matches)
        
        if incomplete_count > len(words) * 0.1:  # Mais de 10% de palavras suspeitas
            quality_issues.append(f"Palavras incompletas: {incomplete_count} detectadas")
        
        # Verificar espaçamento irregular
        irregular_spacing = re.findall(r'\s{3,}', text)
        if len(irregular_spacing) > 10:
            quality_issues.append(f"Espaçamento irregular: {len(irregular_spacing)} ocorrências")
        
        # Verificar caracteres especiais excessivos
        special_chars = re.findall(r'[^\w\s\.,;:!?\-()\[\]{}"\']', text)
        if len(special_chars) > len(text) * 0.05:  # Mais de 5% de caracteres especiais
            quality_issues.append(f"Caracteres especiais excessivos: {len(special_chars)}")
        
        # Log dos problemas encontrados
        if quality_issues:
            self._log(f"Problemas de qualidade detectados: {'; '.join(quality_issues)}", level='warning')
        
        # Remover linhas com apenas caracteres isolados
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Pular linhas com apenas 1-2 caracteres isolados
            if len(line) <= 2 and line.isalpha():
                continue
            # Pular linhas com apenas números isolados
            if line.isdigit() and len(line) <= 3:
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Corrigir espaçamento final
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def detect_headings_and_format(self, text):
        """Detecta e formata cabeçalhos com melhor precisão."""
        if not text:
            return ""
        
        lines = text.split('\n')
        formatted = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                formatted.append('')
                continue
            
            # Detectar diferentes tipos de cabeçalhos
            is_heading = False
            
            # 1. Texto em maiúsculas (títulos principais)
            if line.isupper() and len(line) > 5 and len(line) < 100:
                formatted.append(f'# {line}')
                is_heading = True
            
            # 2. Texto que começa com maiúscula e é curto (subtítulos)
            elif (line[0].isupper() and len(line) < 80 and 
                  not line.endswith('.') and not line.endswith(',') and
                  not any(char.isdigit() for char in line[:10])):
                # Verificar se a próxima linha está vazia ou é diferente
                next_line = lines[i+1].strip() if i+1 < len(lines) else ''
                if not next_line or next_line[0].isupper():
                    formatted.append(f'## {line}')
                    is_heading = True
            
            # 3. Linhas que parecem ser seções numeradas
            elif re.match(r'^\d+\.\s+[A-Z][^.]*$', line):
                formatted.append(f'### {line}')
                is_heading = True
            
            if not is_heading:
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    def _process_pdf_elements(self, elements):
        """Processa elementos PDF preservando estrutura e hierarquia."""
        if not elements:
            return ""
        
        processed_content = []
        current_section = []
        
        for element in elements:
            if not element or not hasattr(element, 'text') or not element.text:
                continue
            
            element_text = element.text.strip()
            if not element_text:
                continue
            
            # Identificar tipo de elemento para melhor estruturação
            element_type = str(type(element).__name__)
            
            # Títulos e cabeçalhos (Title, Header)
            if 'Title' in element_type or 'Header' in element_type:
                # Finalizar seção anterior se existir
                if current_section:
                    processed_content.extend(current_section)
                    processed_content.append('')  # Linha vazia entre seções
                    current_section = []
                
                # Adicionar título com formatação apropriada
                if len(element_text) > 50:
                    processed_content.append(f'## {element_text}')
                else:
                    processed_content.append(f'# {element_text}')
                processed_content.append('')
            
            # Texto normal e parágrafos
            elif 'Text' in element_type or 'NarrativeText' in element_type:
                current_section.append(element_text)
            
            # Listas
            elif 'List' in element_type:
                if current_section:
                    processed_content.extend(current_section)
                    current_section = []
                processed_content.append(f'- {element_text}')
            
            # Tabelas (serão processadas separadamente)
            elif 'Table' in element_type:
                if current_section:
                    processed_content.extend(current_section)
                    current_section = []
                processed_content.append(f'**Tabela:** {element_text}')
                processed_content.append('')
            
            # Outros elementos
            else:
                current_section.append(element_text)
        
        # Adicionar última seção
        if current_section:
            processed_content.extend(current_section)
        
        return '\n'.join(processed_content)
    
    def _extract_pdf_content_optimized(self, pdf_path, options):
        """Extrai conteúdo do PDF de forma otimizada preservando estrutura."""
        try:
            # Usar unstructured para extração principal
            elements = partition_pdf(str(pdf_path))
            self._log(f"Elementos extraídos do PDF: {len(elements)}", level='info')
            
            # Processar elementos preservando estrutura e hierarquia
            markdown_content = self._process_pdf_elements(elements)
            self._log(f"Conteúdo processado com {len(markdown_content.split())} palavras", level='info')
            
            # Pós-processamento melhorado
            if options.get('clean_text', True):
                markdown_content = self.clean_text(markdown_content)
            
            # Aplicar formatação de cabeçalhos após limpeza
            markdown_content = self.detect_headings_and_format(markdown_content)
            
            # Extrair tabelas se solicitado (uma única abertura do PDF)
            if options.get('extract_tables', True):
                tables = self._extract_tables_optimized(pdf_path)
                if tables:
                    markdown_content += '\n\n## Tabelas Extraídas\n' + tables
            
            return markdown_content
            
        except FileNotFoundError as e:
            self._log(f"PDF não encontrado: {pdf_path} - {str(e)}", level='error')
            return None
        except PermissionError as e:
            self._log(f"Sem permissão para ler PDF: {pdf_path} - {str(e)}", level='error')
            return None
        except ImportError as e:
            self._log(f"Biblioteca necessária não encontrada para PDF: {str(e)}", level='error')
            return None
        except Exception as e:
            self._log(f"Erro ao extrair conteúdo do PDF {pdf_path}: {type(e).__name__} - {str(e)}", level='error')
            if self.logger:
                self.logger.exception(f"Stack trace para extração de PDF {pdf_path}:")
            return None
    
    def _extract_tables_optimized(self, pdf_path):
        """Extrai tabelas do PDF com formatação melhorada e detecção aprimorada."""
        md_tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Configurações aprimoradas para detecção de tabelas
                        table_settings = {
                            "vertical_strategy": "lines_strict",
                            "horizontal_strategy": "lines_strict",
                            "snap_tolerance": 3,
                            "join_tolerance": 3,
                            "edge_min_length": 3,
                            "min_words_vertical": 1,
                            "min_words_horizontal": 1,
                            "intersection_tolerance": 3
                        }
                        
                        tables = page.extract_tables(table_settings)
                        
                        # Se não encontrar tabelas com configuração estrita, tentar configuração mais flexível
                        if not tables:
                            flexible_settings = {
                                "vertical_strategy": "text",
                                "horizontal_strategy": "text",
                                "snap_tolerance": 5,
                                "join_tolerance": 5
                            }
                            tables = page.extract_tables(flexible_settings)
                        
                        for table_num, table in enumerate(tables):
                            if table and len(table) > 1:  # Pelo menos cabeçalho + 1 linha
                                # Limpar e validar células da tabela com melhorias
                                cleaned_table = self._clean_table_data(table)
                                
                                if len(cleaned_table) > 1:
                                    # Converter para markdown com formatação aprimorada
                                    md_table = self._format_table_to_markdown(cleaned_table)
                                    md_tables.append(f'\n**Tabela {table_num + 1} (Página {page_num + 1}):**\n\n{md_table}')
                    except Exception as e:
                        self._log(f"Erro ao extrair tabelas da página {page_num + 1}: {str(e)}", level='warning')
                        continue
        except ImportError as e:
            self._log(f"Biblioteca pdfplumber não encontrada: {str(e)}", level='error')
        except PermissionError as e:
            self._log(f"Sem permissão para ler PDF para extração de tabelas: {str(e)}", level='error')
        except Exception as e:
            self._log(f"Erro ao extrair tabelas do PDF: {type(e).__name__} - {str(e)}", level='error')
            if self.logger:
                self.logger.exception(f"Stack trace para extração de tabelas:")
        
        return '\n\n'.join(md_tables)
    
    def _clean_table_data(self, table):
        """Limpa e valida dados da tabela com melhorias."""
        cleaned_table = []
        
        for row in table:
            if row:
                cleaned_row = []
                for cell in row:
                    if cell is not None:
                        # Limpar texto da célula com melhorias
                        clean_cell = str(cell).strip()
                        
                        # Corrigir caracteres duplicados na célula
                        clean_cell = self._fix_duplicate_characters(clean_cell)
                        
                        # Reconstruir palavras fragmentadas na célula
                        clean_cell = self._reconstruct_fragmented_words(clean_cell)
                        
                        # Normalizar espaçamento
                        clean_cell = re.sub(r'\s+', ' ', clean_cell)
                        clean_cell = clean_cell.replace('\n', ' ').replace('\r', ' ')
                        
                        # Remover caracteres de controle
                        clean_cell = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', clean_cell)
                        
                        cleaned_row.append(clean_cell)
                    else:
                        cleaned_row.append('')
                
                # Só adicionar se a linha não estiver completamente vazia
                if any(cell.strip() for cell in cleaned_row):
                    cleaned_table.append(cleaned_row)
        
        return cleaned_table
    
    def _format_table_to_markdown(self, table):
        """Formata tabela para markdown com melhorias."""
        if not table or len(table) < 1:
            return ""
        
        # Normalizar número de colunas
        max_cols = max(len(row) for row in table)
        normalized_table = []
        
        for row in table:
            # Preencher colunas faltantes
            while len(row) < max_cols:
                row.append('')
            # Truncar colunas extras
            normalized_table.append(row[:max_cols])
        
        # Verificar se há pelo menos uma coluna
        if max_cols == 0:
            return ""
        
        # Construir markdown
        md_table = ""
        
        # Cabeçalho
        header_row = normalized_table[0]
        md_table += "| " + " | ".join(header_row) + " |\n"
        
        # Separador
        md_table += "| " + " | ".join(["---"] * max_cols) + " |\n"
        
        # Linhas de dados
        for row in normalized_table[1:]:
            md_table += "| " + " | ".join(row) + " |\n"
        
        return md_table
    
    def convert_file(self, input_path: str, output_path: Optional[str] = None, options: Dict[str, bool] = None) -> Optional[str]:
        """
        Converte um arquivo para Markdown
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída (opcional)
            
        Returns:
            str: Caminho do arquivo convertido ou None se falhar
        """
        options = options or {}
        try:
            # Validação de segurança
            if not SecurityValidator.validate_file_path(input_path):
                self._log(f"Caminho de arquivo inválido ou inseguro: {input_path}", level='error')
                return None
                
            # Verificar permissões do arquivo
            permissions = SecurityValidator.check_file_permissions(input_path)
            if not permissions['readable']:
                self._log(f"Sem permissão de leitura para o arquivo: {input_path}", level='error')
                return None
            
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
            
            # Resolver caminho de saída: aceitar diretório ou arquivo
            if output_path is None:
                output_file = input_file.with_suffix('.md')
            else:
                # Validar diretório de saída
                output_base = Path(output_path)
                if output_base.exists() and output_base.is_dir():
                    if not SecurityValidator.validate_directory_path(str(output_base)):
                        self._log(f"Diretório de saída inválido ou sem permissões: {output_base}", level='error')
                        return None
                    output_file = output_base / input_file.with_suffix('.md').name
                elif output_base.suffix == "":
                    if not SecurityValidator.validate_directory_path(str(output_base)):
                        self._log(f"Diretório de saída inválido ou sem permissões: {output_base}", level='error')
                        return None
                    output_file = output_base / input_file.with_suffix('.md').name
                else:
                    output_file = output_base

            # Criar diretório de saída se necessário
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar cache se habilitado
            conversion_options = options or {}
            if self.cache and self.cache.is_cached(input_path, str(output_file)):
                self._log(f"Arquivo já processado (cache): {input_file.name}")
                return str(output_file)
            
            self._log(f"Convertendo {input_file.name} ({self.get_file_type(input_path)})...")
            
            # Realizar a conversão
            try:
                if input_file.suffix.lower() == '.pdf':
                    # Usar método otimizado para PDF
                    markdown_content = self._extract_pdf_content_optimized(input_path, options)
                else:
                    # Manter markitdown para outros formatos
                    result = self.markitdown.convert(str(input_path))
                    markdown_content = getattr(result, 'text_content', None) or getattr(result, 'markdown', None)
                
                if not markdown_content:
                    self._log(f"Conteúdo vazio após conversão: {input_path}", level='warning')
                    return None
                    
            except Exception as e:
                self._log(f"Erro durante a conversão de {input_file.name}: {str(e)}", level='error')
                return None
            
            # Salvar o arquivo markdown
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                # Adicionar ao cache se habilitado
                if self.cache:
                    self.cache.add_to_cache(input_path, str(output_file), conversion_options)
                    
                self._log(f"Arquivo convertido salvo em: {output_file}")
                return str(output_file)
                
            except Exception as e:
                self._log(f"Erro ao salvar arquivo: {str(e)}", level='error')
                return None
                
        except FileNotFoundError as e:
            self._log(f"Arquivo não encontrado: {input_path} - {str(e)}", level='error')
            return None
        except PermissionError as e:
            self._log(f"Sem permissão para acessar arquivo: {input_path} - {str(e)}", level='error')
            return None
        except OSError as e:
            self._log(f"Erro do sistema ao processar arquivo: {input_path} - {str(e)}", level='error')
            return None
        except UnicodeDecodeError as e:
            self._log(f"Erro de codificação no arquivo: {input_path} - {str(e)}", level='error')
            return None
        except ImportError as e:
            self._log(f"Dependência não encontrada para processar {input_path}: {str(e)}", level='error')
            return None
        except Exception as e:
            self._log(f"Erro inesperado ao converter {input_path}: {type(e).__name__} - {str(e)}", level='error')
            if self.logger:
                self.logger.exception(f"Stack trace completo para {input_path}:")
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
    
    def convert_files_async(self, 
                           files: List[str], 
                           output_dir: str, 
                           options: Dict[str, Any] = None,
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Converte múltiplos arquivos de forma assíncrona.
        
        Args:
            files: Lista de caminhos de arquivos para converter
            output_dir: Diretório de saída
            options: Opções de conversão
            progress_callback: Callback para atualização de progresso
            
        Returns:
            Dict com resultados do processamento
        """
        if not files:
            return {'success': [], 'errors': [], 'cancelled': False}
        
        # Validar diretório de saída
        if not SecurityValidator.validate_directory_path(output_dir):
            self._log(f"Diretório de saída inválido: {output_dir}", level='error')
            return {'success': [], 'errors': [{'file': 'N/A', 'error': 'Diretório de saída inválido'}], 'cancelled': False}
        
        # Filtrar apenas arquivos suportados e válidos
        valid_files = []
        for file_path in files:
            if SecurityValidator.validate_file_path(file_path) and self.is_supported_file(file_path):
                valid_files.append(file_path)
            else:
                self._log(f"Arquivo inválido ou não suportado ignorado: {file_path}", level='warning')
        
        if not valid_files:
            return {'success': [], 'errors': [{'file': 'N/A', 'error': 'Nenhum arquivo válido para processar'}], 'cancelled': False}
        
        self._log(f"Iniciando conversão assíncrona de {len(valid_files)} arquivos")
        
        # Usar o processador assíncrono
        return self.async_processor.process_files_async(
            files=valid_files,
            converter_func=self.convert_file,
            output_dir=output_dir,
            options=options,
            progress_callback=progress_callback
        )
    
    def cancel_async_operations(self):
        """
        Cancela todas as operações assíncronas em andamento.
        """
        self.async_processor.cancel_all_operations()
    
    def is_processing_async(self) -> bool:
        """
        Verifica se há processamento assíncrono em andamento.
        
        Returns:
            True se há operações ativas, False caso contrário
        """
        return self.async_processor.is_processing()
    
    def get_active_tasks_count(self) -> int:
        """
        Retorna o número de tarefas ativas no processamento assíncrono.
        
        Returns:
            Número de tarefas em execução
        """
        return self.async_processor.get_active_tasks_count()
    
    def shutdown_async_processor(self, wait: bool = True):
        """
        Encerra o processador assíncrono.
        
        Args:
            wait: Se deve aguardar a conclusão das tarefas
        """
        self.async_processor.shutdown(wait=wait)
    
    def __del__(self):
        """Destrutor para garantir limpeza de recursos."""
        try:
            self.shutdown_async_processor(wait=False)
        except:
            pass  # Ignorar erros durante destruição
