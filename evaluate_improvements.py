#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para avaliar a qualidade das melhorias pontuais na conversão de PDF.
"""

import re
from pathlib import Path

def count_fragmented_words(text):
    """Conta palavras fragmentadas no texto."""
    # Padrões de fragmentação identificados
    patterns = [
        r'\bREPÚ\s+BLICA\b',
        r'\bCONTROLA\s+DORIA\b', 
        r'\bGERAL\s+DA\s+UNIÃO\b',
        r'\bFEDERAL\s+DO\s+BRASIL\b',
        r'\bMINISTÉRIO\s+DA\b',
        r'\bSECRETARIA\s+DE\b',
        r'\bDEPARTAMENTO\s+DE\b',
        # Outros padrões gerais
        r'\b[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]\s+[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]\s+[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]\b',
        r'\b[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]\s+[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]\b'
    ]
    
    total_fragments = 0
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        total_fragments += len(matches)
    
    return total_fragments

def count_duplicate_chars(text):
    """Conta caracteres duplicados no texto."""
    patterns = [
        r'[.,]{2,}',
        r'[;:]{2,}', 
        r'[!?]{2,}',
        r' {3,}'
    ]
    
    total_duplicates = 0
    for pattern in patterns:
        matches = re.findall(pattern, text)
        total_duplicates += len(matches)
    
    return total_duplicates

def analyze_table_structure(text):
    """Analisa a estrutura de tabelas no texto."""
    # Procura por padrões de tabelas fragmentadas
    table_issues = 0
    
    # Linhas com muitos espaços (possível fragmentação de tabela)
    fragmented_lines = re.findall(r'^.{1,10}\s{5,}.{1,10}\s{5,}', text, re.MULTILINE)
    table_issues += len(fragmented_lines)
    
    return table_issues

def evaluate_file_quality(file_path):
    """Avalia a qualidade de um arquivo convertido."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Métricas de qualidade
        total_words = len(content.split())
        fragmented_words = count_fragmented_words(content)
        duplicate_chars = count_duplicate_chars(content)
        table_issues = analyze_table_structure(content)
        
        # Calcular pontuação (0-10)
        fragmentation_penalty = min(fragmented_words / total_words * 100, 5.0)
        duplicate_penalty = min(duplicate_chars / 100, 2.0)
        table_penalty = min(table_issues / 50, 1.5)
        
        quality_score = 10.0 - fragmentation_penalty - duplicate_penalty - table_penalty
        quality_score = max(0.0, quality_score)
        
        return {
            'file': file_path.name,
            'total_words': total_words,
            'fragmented_words': fragmented_words,
            'duplicate_chars': duplicate_chars,
            'table_issues': table_issues,
            'quality_score': round(quality_score, 1)
        }
    
    except Exception as e:
        return {'error': str(e)}

def main():
    """Função principal."""
    print("=== Avaliação da Qualidade das Melhorias Pontuais ===")
    print()
    
    # Arquivos para comparação
    files_to_analyze = [
        '707710_RA175135.md',  # Original
        '707710_RA175135_melhorado.md',  # Com melhorias complexas (ineficazes)
        '707710_RA175135_revertido.md',  # Com melhorias pontuais básicas
        '707710_RA175135_final.md'  # Com todas as melhorias implementadas
    ]
    
    results = []
    
    for filename in files_to_analyze:
        file_path = Path(filename)
        if file_path.exists():
            result = evaluate_file_quality(file_path)
            results.append(result)
            
            if 'error' not in result:
                print(f"Arquivo: {result['file']}")
                print(f"  Palavras totais: {result['total_words']:,}")
                print(f"  Palavras fragmentadas: {result['fragmented_words']}")
                print(f"  Caracteres duplicados: {result['duplicate_chars']}")
                print(f"  Problemas de tabela: {result['table_issues']}")
                print(f"  Pontuação de qualidade: {result['quality_score']}/10")
                print()
            else:
                print(f"Erro ao analisar {filename}: {result['error']}")
                print()
        else:
            print(f"Arquivo não encontrado: {filename}")
            print()
    
    # Comparação final
    if len(results) >= 2:
        print("=== Comparação de Resultados ===")
        for i, result in enumerate(results):
            if 'error' not in result:
                print(f"{i+1}. {result['file']}: {result['quality_score']}/10")
        
        # Verificar se houve melhoria
        if len(results) >= 3 and 'error' not in results[0] and 'error' not in results[2]:
            original_score = results[0]['quality_score']
            improved_score = results[2]['quality_score']
            improvement = improved_score - original_score
            
            print(f"\nMelhoria com correções pontuais: {improvement:+.1f} pontos")
            if improvement > 0:
                print("✅ As melhorias pontuais foram EFICAZES!")
            else:
                print("❌ As melhorias pontuais não foram eficazes.")

if __name__ == '__main__':
    main()