#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markitdown Converter - Main Application Entry Point

Conversor de arquivos para Markdown (.MD) utilizando a biblioteca markitdown.
Interface gráfica em Tkinter para conversão individual ou em lote.

Author: dadebr
GitHub: https://github.com/dadebr/markitdown-converter
"""

import sys
import os

# Adiciona o diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MarkitdownConverterApp
from utils.logger import setup_logger

def main():
    """
    Função principal da aplicação
    """
    try:
        # Configurar logging
        logger = setup_logger()
        logger.info("Iniciando Markitdown Converter...")
        
        # Criar e executar a aplicação
        app = MarkitdownConverterApp(logger)
        app.run()
        
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nAplicação interrompida pelo usuário.")
        sys.exit(0)

if __name__ == "__main__":
    main()
