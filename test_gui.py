#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para identificar problemas na interface gráfica
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Testa todos os imports necessários"""
    print("Testando imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar tkinter: {e}")
        return False
    
    try:
        from tkinter import ttk, filedialog, messagebox
        print("✓ Componentes tkinter importados com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar componentes tkinter: {e}")
        return False
    
    try:
        from converter.file_converter import FileConverter
        print("✓ FileConverter importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar FileConverter: {e}")
        return False
    
    try:
        from utils.security import SecurityValidator
        print("✓ SecurityValidator importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar SecurityValidator: {e}")
        return False
    
    try:
        from utils.logger import setup_logger
        print("✓ Logger importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar Logger: {e}")
        return False
    
    return True

def test_tkinter_basic():
    """Testa se o tkinter funciona básicamente"""
    print("\nTestando tkinter básico...")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Esconde a janela
        root.destroy()
        print("✓ tkinter funciona corretamente")
        return True
    except Exception as e:
        print(f"✗ Erro no tkinter básico: {e}")
        traceback.print_exc()
        return False

def test_file_converter():
    """Testa se o FileConverter pode ser instanciado"""
    print("\nTestando FileConverter...")
    
    try:
        from converter.file_converter import FileConverter
        converter = FileConverter()
        print("✓ FileConverter instanciado com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao instanciar FileConverter: {e}")
        traceback.print_exc()
        return False

def test_main_window_import():
    """Testa se a janela principal pode ser importada"""
    print("\nTestando import da janela principal...")
    
    try:
        from ui.main_window import MarkitdownConverterApp
        print("✓ MarkitdownConverterApp importado com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao importar MarkitdownConverterApp: {e}")
        traceback.print_exc()
        return False

def test_main_window_creation():
    """Testa se a janela principal pode ser criada"""
    print("\nTestando criação da janela principal...")
    
    try:
        import tkinter as tk
        from ui.main_window import MarkitdownConverterApp
        
        root = tk.Tk()
        root.withdraw()  # Esconde a janela
        
        app = MarkitdownConverterApp(root)
        print("✓ MarkitdownConverterApp criado com sucesso")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ Erro ao criar MarkitdownConverterApp: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("=== TESTE DE DIAGNÓSTICO DA INTERFACE GRÁFICA ===")
    print(f"Python: {sys.version}")
    print(f"Diretório atual: {Path.cwd()}")
    print()
    
    tests = [
        test_imports,
        test_tkinter_basic,
        test_file_converter,
        test_main_window_import,
        test_main_window_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Erro inesperado no teste {test.__name__}: {e}")
            traceback.print_exc()
            results.append(False)
    
    print("\n=== RESUMO DOS TESTES ===")
    passed = sum(results)
    total = len(results)
    print(f"Testes aprovados: {passed}/{total}")
    
    if passed == total:
        print("✓ Todos os testes passaram! O problema pode estar em outro lugar.")
    else:
        print("✗ Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro fatal: {e}")
        traceback.print_exc()
        sys.exit(1)