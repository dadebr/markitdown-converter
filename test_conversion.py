#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converter.file_converter import FileConverter
from utils.security import SecurityValidator

def test_document_conversion():
    """Testa a conversão do documento problemático"""
    
    # Caminho do documento problemático
    document_path = "Reunião Técnica - Estruturação SUAS.docx"
    
    if not os.path.exists(document_path):
        print(f"❌ Arquivo não encontrado: {document_path}")
        return False
    
    print(f"📄 Testando conversão do arquivo: {document_path}")
    print(f"📊 Tamanho do arquivo: {os.path.getsize(document_path)} bytes")
    
    try:
        # Inicializar validador de segurança
        security_validator = SecurityValidator()
        
        # Validar segurança do arquivo
        print("🔒 Validando segurança do arquivo...")
        is_safe = security_validator.validate_file_path(document_path)
        
        if not is_safe:
            print(f"❌ Falha na validação de segurança: Arquivo não passou na validação")
            return False
        
        print(f"✅ Arquivo aprovado na validação de segurança")
        
        # Inicializar conversor
        converter = FileConverter()
        
        # Tentar conversão
        print("🔄 Iniciando conversão...")
        
        # Criar diretório de saída se não existir
        output_dir = "output_test"
        os.makedirs(output_dir, exist_ok=True)
        
        # Definir opções de conversão
        options = {
            'clean_text': True,
            'extract_tables': True
        }
        
        # Executar conversão
        output_file = converter.convert_file(
            input_path=document_path,
            output_path=output_dir,
            options=options
        )
        
        if output_file:
            print(f"✅ Conversão bem-sucedida!")
            print(f"📁 Arquivo de saída: {output_file}")
            
            # Verificar se o arquivo foi criado
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📊 Tamanho do arquivo convertido: {file_size} bytes")
                
                # Mostrar primeiras linhas do arquivo convertido
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # Primeiros 500 caracteres
                    print(f"📖 Primeiras linhas do conteúdo convertido:")
                    print("-" * 50)
                    print(content)
                    print("-" * 50)
            else:
                print(f"❌ Arquivo de saída não foi criado: {output_file}")
                return False
        else:
            print(f"❌ Falha na conversão - método retornou None")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        print(f"🔍 Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de conversão...")
    print("=" * 60)
    
    success = test_document_conversion()
    
    print("=" * 60)
    if success:
        print("✅ Teste concluído com sucesso!")
    else:
        print("❌ Teste falhou - verifique os erros acima")