#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converter Package - Markitdown Converter

Módulos responsáveis pela conversão de arquivos para Markdown.

Módulos disponíveis:
- file_converter: Conversão de arquivos individuais
- batch_processor: Processamento em lote de múltiplos arquivos

Author: dadebr
GitHub: https://github.com/dadebr/markitdown-converter
"""

from .file_converter import FileConverter

__version__ = "1.0.0"
__author__ = "dadebr"
__email__ = "dadebr@github.com"
__all__ = ["FileConverter"]
