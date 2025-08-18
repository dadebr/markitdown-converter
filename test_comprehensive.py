#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste Abrangente - Markitdown Converter
Testa todas as funcionalidades principais do aplicativo
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converter.file_converter import FileConverter
from utils.security import SecurityValidator
from utils.logger import get_logger

def test_file_conversion():
    """Testa conversão de diferentes tipos de arquivo"""
    print("\n=== TESTE DE CONVERSÃO DE ARQUIVOS ===")
    
    converter = FileConverter()
    test_files = [
        "Reunião Técnica - Estruturação SUAS.docx",
        # Adicione outros arquivos de teste aqui se disponíveis
    ]
    
    success_count = 0
    total_count = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            total_count += 1
            print(f"\nTestando: {test_file}")
            
            try:
                # Criar diretório de saída temporário
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_file = os.path.join(temp_dir, "output.md")
                    
                    # Converter arquivo
                    result = converter.convert_file(
                        input_path=test_file,
                        output_path=output_file
                    )
                    
                    if result and os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        print(f"✓ Conversão bem-sucedida! Arquivo gerado: {file_size} bytes")
                        
                        # Verificar conteúdo
                        with open(output_file, 'r', encoding='utf-8') as f:
                            content = f.read()[:200]
                            print(f"Prévia do conteúdo: {content}...")
                        
                        success_count += 1
                    else:
                        print("✗ Falha na conversão")
                        
            except Exception as e:
                print(f"✗ Erro durante conversão: {e}")
        else:
            print(f"⚠ Arquivo não encontrado: {test_file}")
    
    print(f"\nResultado: {success_count}/{total_count} conversões bem-sucedidas")
    return success_count, total_count

def test_security_validation():
    """Testa validação de segurança"""
    print("\n=== TESTE DE VALIDAÇÃO DE SEGURANÇA ===")
    
    validator = SecurityValidator()
    
    # Testes de caminhos seguros
    safe_paths = [
        "Reunião Técnica - Estruturação SUAS.docx",
        "requirements.txt",
        "./main.py"
    ]
    
    # Testes de caminhos inseguros
    unsafe_paths = [
        "../../../etc/passwd",
        "C:\\Windows\\System32\\config\\SAM",
        "\\\\network\\share\\file.txt"
    ]
    
    safe_count = 0
    unsafe_count = 0
    
    print("\nTestando caminhos seguros:")
    for path in safe_paths:
        try:
            if validator.validate_file_path(path):
                print(f"✓ {path} - Validado como seguro")
                safe_count += 1
            else:
                print(f"✗ {path} - Rejeitado incorretamente")
        except Exception as e:
            print(f"✗ {path} - Erro: {e}")
    
    print("\nTestando caminhos inseguros:")
    for path in unsafe_paths:
        try:
            if not validator.validate_file_path(path):
                print(f"✓ {path} - Corretamente rejeitado")
                unsafe_count += 1
            else:
                print(f"✗ {path} - Incorretamente aceito")
        except Exception as e:
            print(f"✓ {path} - Corretamente rejeitado com exceção: {e}")
            unsafe_count += 1
    
    print(f"\nResultado: {safe_count}/{len(safe_paths)} caminhos seguros validados")
    print(f"Resultado: {unsafe_count}/{len(unsafe_paths)} caminhos inseguros rejeitados")
    
    return safe_count, unsafe_count

def test_logger():
    """Testa sistema de logging"""
    print("\n=== TESTE DO SISTEMA DE LOGGING ===")
    
    try:
        logger = get_logger("test")
        
        # Testar diferentes níveis de log
        logger.info("Teste de log INFO")
        logger.warning("Teste de log WARNING")
        logger.error("Teste de log ERROR")
        
        print("✓ Sistema de logging funcionando corretamente")
        return True
    except Exception as e:
        print(f"✗ Erro no sistema de logging: {e}")
        return False

def test_file_operations():
    """Testa operações básicas de arquivo"""
    print("\n=== TESTE DE OPERAÇÕES DE ARQUIVO ===")
    
    try:
        # Criar arquivo temporário para teste
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Conteúdo de teste")
            temp_path = temp_file.name
        
        # Verificar se arquivo existe
        if os.path.exists(temp_path):
            print(f"✓ Arquivo temporário criado: {temp_path}")
            
            # Verificar leitura
            with open(temp_path, 'r') as f:
                content = f.read()
                if content == "Conteúdo de teste":
                    print("✓ Leitura de arquivo funcionando")
                else:
                    print("✗ Erro na leitura de arquivo")
                    return False
            
            # Limpar arquivo temporário
            os.unlink(temp_path)
            print("✓ Arquivo temporário removido")
            
            return True
        else:
            print("✗ Falha ao criar arquivo temporário")
            return False
            
    except Exception as e:
        print(f"✗ Erro nas operações de arquivo: {e}")
        return False

def main():
    """Função principal do teste"""
    print("=== TESTE ABRANGENTE DO MARKITDOWN CONVERTER ===")
    print(f"Python: {sys.version}")
    print(f"Diretório atual: {os.getcwd()}")
    
    # Executar todos os testes
    tests_results = []
    
    # Teste de operações de arquivo
    file_ops_result = test_file_operations()
    tests_results.append(("Operações de Arquivo", file_ops_result))
    
    # Teste de logging
    logger_result = test_logger()
    tests_results.append(("Sistema de Logging", logger_result))
    
    # Teste de validação de segurança
    safe_count, unsafe_count = test_security_validation()
    security_result = safe_count > 0 and unsafe_count > 0
    tests_results.append(("Validação de Segurança", security_result))
    
    # Teste de conversão de arquivos
    success_count, total_count = test_file_conversion()
    conversion_result = success_count > 0 if total_count > 0 else True
    tests_results.append(("Conversão de Arquivos", conversion_result))
    
    # Resumo final
    print("\n=== RESUMO DOS TESTES ===")
    passed_tests = 0
    total_tests = len(tests_results)
    
    for test_name, result in tests_results:
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nTestes aprovados: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 Todos os testes passaram! O aplicativo está funcionando corretamente.")
        return 0
    else:
        print("⚠ Alguns testes falharam. Verifique os logs acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())