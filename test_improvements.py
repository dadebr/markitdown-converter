#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar as melhorias implementadas na conversão de PDF.
Reconverte o arquivo 707710_RA175135.pdf e compara com a versão anterior.
"""

import os
import sys
from datetime import datetime
from converter.file_converter import FileConverter
from utils.logger import setup_logger

def test_pdf_conversion_improvements():
    """Testa as melhorias na conversão de PDF."""
    
    # Setup do logger
    logger = setup_logger()
    logger.info("Iniciando teste das melhorias na conversão de PDF...")
    
    # Caminhos dos arquivos
    pdf_file = "707710_RA175135.pdf"
    old_md_file = "707710_RA175135.md"
    new_md_file = "707710_RA175135_melhorado.md"
    
    # Verificar se o arquivo PDF existe
    if not os.path.exists(pdf_file):
        logger.error(f"Arquivo PDF não encontrado: {pdf_file}")
        return False
    
    # Fazer backup do arquivo MD original se existir
    if os.path.exists(old_md_file):
        backup_file = f"707710_RA175135_original_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        os.rename(old_md_file, backup_file)
        logger.info(f"Backup do arquivo original criado: {backup_file}")
    
    try:
        # Inicializar o conversor
        converter = FileConverter()
        
        # Converter o arquivo PDF com as melhorias
        logger.info(f"Convertendo {pdf_file} com as melhorias implementadas...")
        
        # Definir arquivo de saída com sufixo melhorado
        output_file = new_md_file
        
        # Realizar a conversão
        success = converter.convert_file(pdf_file, output_file)
        
        if success:
            logger.info(f"Conversão concluída com sucesso: {output_file}")
            
            # Verificar se o arquivo foi criado
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"Arquivo gerado: {output_file} ({file_size} bytes)")
                
                # Ler as primeiras linhas para verificação rápida
                with open(output_file, 'r', encoding='utf-8') as f:
                    first_lines = [f.readline().strip() for _ in range(10)]
                    logger.info("Primeiras linhas do arquivo gerado:")
                    for i, line in enumerate(first_lines, 1):
                        if line:
                            logger.info(f"  {i}: {line[:100]}...")
                
                return True
            else:
                logger.error(f"Arquivo de saída não foi criado: {output_file}")
                return False
        else:
            logger.error("Falha na conversão do arquivo PDF")
            return False
            
    except Exception as e:
        logger.error(f"Erro durante a conversão: {str(e)}")
        return False

def analyze_conversion_quality(file_path):
    """Analisa a qualidade da conversão do arquivo."""
    
    logger = setup_logger()
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return
    
    logger.info(f"Analisando qualidade da conversão: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Estatísticas básicas
        total_chars = len(content)
        total_lines = len(content.split('\n'))
        total_words = len(content.split())
        
        logger.info(f"Estatísticas do arquivo:")
        logger.info(f"  - Total de caracteres: {total_chars}")
        logger.info(f"  - Total de linhas: {total_lines}")
        logger.info(f"  - Total de palavras: {total_words}")
        
        # Verificar problemas específicos
        issues = []
        
        # Palavras fragmentadas comuns
        fragmented_words = ['REPÚ BLICA', 'BRAS IL', 'MINIS TÉRIO', 'CONTRO LADORIA']
        for word in fragmented_words:
            if word in content:
                issues.append(f"Palavra fragmentada encontrada: '{word}'")
        
        # Caracteres duplicados
        duplicate_patterns = ['..', ',,', '  ', 'ôô', 'nn', 'bb', 'uu', 'ss']
        for pattern in duplicate_patterns:
            count = content.count(pattern)
            if count > 5:  # Threshold para considerar problemático
                issues.append(f"Padrão duplicado '{pattern}' encontrado {count} vezes")
        
        # Cabeçalhos mal formatados
        lines = content.split('\n')
        malformed_headers = 0
        for line in lines:
            if line.strip() and not line.startswith('#') and line.isupper() and len(line.strip()) < 50:
                malformed_headers += 1
        
        if malformed_headers > 10:
            issues.append(f"Possíveis cabeçalhos mal formatados: {malformed_headers}")
        
        # Relatório de qualidade
        if issues:
            logger.warning(f"Problemas identificados ({len(issues)}):")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("Nenhum problema óbvio identificado na conversão")
        
        return len(issues)
        
    except Exception as e:
        logger.error(f"Erro ao analisar arquivo: {str(e)}")
        return -1

if __name__ == "__main__":
    print("=== Teste das Melhorias na Conversão de PDF ===")
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testar a conversão
    success = test_pdf_conversion_improvements()
    
    if success:
        print("\n=== Análise de Qualidade ===")
        
        # Analisar o arquivo gerado
        issues_count = analyze_conversion_quality("707710_RA175135_melhorado.md")
        
        if issues_count >= 0:
            print(f"\nAnálise concluída. Problemas identificados: {issues_count}")
            
            if issues_count == 0:
                print("✅ Conversão de alta qualidade!")
            elif issues_count <= 3:
                print("⚠️ Conversão com qualidade boa, poucos problemas")
            elif issues_count <= 10:
                print("⚠️ Conversão com qualidade média, alguns problemas")
            else:
                print("❌ Conversão com qualidade baixa, muitos problemas")
        
        print(f"\nArquivo gerado: 707710_RA175135_melhorado.md")
        print("Compare manualmente com o arquivo original para avaliar as melhorias.")
    else:
        print("❌ Falha na conversão do arquivo PDF")
    
    print(f"\nTeste concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")