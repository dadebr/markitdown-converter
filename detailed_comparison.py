#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para análise comparativa detalhada entre arquivos MD original e melhorado
"""

import re
from pathlib import Path

def analyze_file_quality(file_path):
    """Analisa a qualidade de um arquivo MD"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Problemas específicos identificados
    issues = {
        'palavras_fragmentadas': [],
        'caracteres_duplicados': {},
        'espacamento_irregular': 0,
        'tabelas_fragmentadas': 0,
        'cabeçalhos_mal_formatados': 0
    }
    
    lines = content.split('\n')
    
    # 1. Detectar palavras fragmentadas (palavras com espaços no meio)
    fragmented_patterns = [
        r'\b[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]\s+[a-záéíóúâêîôûàèìòùãõç]+',  # REPÚ BLICA
        r'\b[a-záéíóúâêîôûàèìòùãõç]+\s+[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ]+',  # ônni BBUS
        r'\b\w{1,3}\s+\w{1,3}\b',  # palavras muito curtas separadas
    ]
    
    for line_num, line in enumerate(lines, 1):
        for pattern in fragmented_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                issues['palavras_fragmentadas'].append({
                    'linha': line_num,
                    'texto': match,
                    'contexto': line.strip()[:100]
                })
    
    # 2. Detectar caracteres duplicados específicos
    duplicate_patterns = {
        '..': r'\.{2,}',
        ',,': r',{2,}',
        '  ': r' {3,}',  # 3 ou mais espaços
        'nn': r'nn{2,}',
        'ss': r'ss{2,}',
        'cc': r'cc{2,}',
        'oo': r'oo{3,}',  # 3 ou mais 'o'
    }
    
    for pattern_name, pattern in duplicate_patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            issues['caracteres_duplicados'][pattern_name] = len(matches)
    
    # 3. Detectar espaçamento irregular em tabelas
    table_lines = [line for line in lines if '|' in line]
    for line in table_lines:
        # Contar espaços irregulares em células de tabela
        cells = line.split('|')
        for cell in cells:
            if re.search(r'\s{3,}', cell):  # 3 ou mais espaços consecutivos
                issues['espacamento_irregular'] += 1
    
    # 4. Detectar tabelas fragmentadas (cabeçalhos divididos)
    for i, line in enumerate(lines):
        if '|' in line and i < len(lines) - 1:
            next_line = lines[i + 1]
            # Se uma linha de tabela é seguida por outra linha de tabela muito similar
            if '|' in next_line:
                cells1 = [cell.strip() for cell in line.split('|')]
                cells2 = [cell.strip() for cell in next_line.split('|')]
                if len(cells1) == len(cells2):
                    # Verificar se são fragmentos do mesmo cabeçalho
                    similar_count = 0
                    for c1, c2 in zip(cells1, cells2):
                        if c1 and c2 and (c1.lower() in c2.lower() or c2.lower() in c1.lower()):
                            similar_count += 1
                    if similar_count > len(cells1) * 0.3:  # 30% de similaridade
                        issues['tabelas_fragmentadas'] += 1
    
    # 5. Detectar cabeçalhos mal formatados
    for line in lines:
        # Cabeçalhos com espaços irregulares
        if line.startswith('#'):
            if re.search(r'#\s{2,}', line) or re.search(r'\s{2,}#', line):
                issues['cabeçalhos_mal_formatados'] += 1
        # Texto que parece cabeçalho mas não está formatado
        elif re.match(r'^[A-ZÁÉÍÓÚÂÊÎÔÛÀÈÌÒÙÃÕÇ\s]{10,50}$', line.strip()):
            if not line.startswith('|') and line.strip():
                issues['cabeçalhos_mal_formatados'] += 1
    
    return issues

def compare_files():
    """Compara os dois arquivos e gera relatório"""
    base_path = Path('C:/Users/luize/OneDrive - CGU/Trabalho/Desenvolvimento/1 - Assistente de Arquivos/markitdown-converter')
    
    original_file = base_path / '707710_RA175135_original_backup_20250815_192229.md'
    improved_file = base_path / '707710_RA175135_melhorado.md'
    
    print("=== ANÁLISE COMPARATIVA DE QUALIDADE ===\n")
    
    print("Analisando arquivo original...")
    original_issues = analyze_file_quality(original_file)
    
    print("Analisando arquivo melhorado...")
    improved_issues = analyze_file_quality(improved_file)
    
    print("\n=== RESULTADOS DA COMPARAÇÃO ===\n")
    
    # Comparar palavras fragmentadas
    print(f"1. PALAVRAS FRAGMENTADAS:")
    print(f"   Original: {len(original_issues['palavras_fragmentadas'])} ocorrências")
    print(f"   Melhorado: {len(improved_issues['palavras_fragmentadas'])} ocorrências")
    
    if len(original_issues['palavras_fragmentadas']) > 0:
        print(f"   Exemplos no original:")
        for i, issue in enumerate(original_issues['palavras_fragmentadas'][:5]):
            print(f"     - Linha {issue['linha']}: '{issue['texto']}'")
    
    if len(improved_issues['palavras_fragmentadas']) > 0:
        print(f"   Exemplos no melhorado:")
        for i, issue in enumerate(improved_issues['palavras_fragmentadas'][:5]):
            print(f"     - Linha {issue['linha']}: '{issue['texto']}'")
    
    improvement = len(original_issues['palavras_fragmentadas']) - len(improved_issues['palavras_fragmentadas'])
    print(f"   Melhoria: {improvement} palavras fragmentadas corrigidas\n")
    
    # Comparar caracteres duplicados
    print(f"2. CARACTERES DUPLICADOS:")
    for char_type in ['..', ',,', '  ', 'nn', 'ss', 'cc', 'oo']:
        orig_count = original_issues['caracteres_duplicados'].get(char_type, 0)
        impr_count = improved_issues['caracteres_duplicados'].get(char_type, 0)
        print(f"   {char_type}: Original={orig_count}, Melhorado={impr_count}, Melhoria={orig_count - impr_count}")
    
    # Comparar outros problemas
    print(f"\n3. ESPAÇAMENTO IRREGULAR EM TABELAS:")
    print(f"   Original: {original_issues['espacamento_irregular']}")
    print(f"   Melhorado: {improved_issues['espacamento_irregular']}")
    print(f"   Melhoria: {original_issues['espacamento_irregular'] - improved_issues['espacamento_irregular']}")
    
    print(f"\n4. TABELAS FRAGMENTADAS:")
    print(f"   Original: {original_issues['tabelas_fragmentadas']}")
    print(f"   Melhorado: {improved_issues['tabelas_fragmentadas']}")
    print(f"   Melhoria: {original_issues['tabelas_fragmentadas'] - improved_issues['tabelas_fragmentadas']}")
    
    print(f"\n5. CABEÇALHOS MAL FORMATADOS:")
    print(f"   Original: {original_issues['cabeçalhos_mal_formatados']}")
    print(f"   Melhorado: {improved_issues['cabeçalhos_mal_formatados']}")
    print(f"   Melhoria: {original_issues['cabeçalhos_mal_formatados'] - improved_issues['cabeçalhos_mal_formatados']}")
    
    # Calcular pontuação de qualidade
    def calculate_quality_score(issues):
        # Pontuação baseada na quantidade de problemas (quanto menos, melhor)
        score = 10.0
        score -= min(len(issues['palavras_fragmentadas']) * 0.1, 3.0)  # máximo -3 pontos
        score -= min(sum(issues['caracteres_duplicados'].values()) * 0.001, 2.0)  # máximo -2 pontos
        score -= min(issues['espacamento_irregular'] * 0.01, 1.0)  # máximo -1 ponto
        score -= min(issues['tabelas_fragmentadas'] * 0.05, 2.0)  # máximo -2 pontos
        score -= min(issues['cabeçalhos_mal_formatados'] * 0.02, 2.0)  # máximo -2 pontos
        return max(score, 0.0)
    
    original_score = calculate_quality_score(original_issues)
    improved_score = calculate_quality_score(improved_issues)
    
    print(f"\n=== PONTUAÇÃO DE QUALIDADE ===\n")
    print(f"Arquivo Original: {original_score:.1f}/10")
    print(f"Arquivo Melhorado: {improved_score:.1f}/10")
    print(f"Melhoria: +{improved_score - original_score:.1f} pontos")
    
    if improved_score >= 8.0:
        print("\n✅ OBJETIVO ALCANÇADO: Qualidade ≥ 8/10")
    elif improved_score > original_score:
        print(f"\n🔄 MELHORIA PARCIAL: Ainda faltam {8.0 - improved_score:.1f} pontos para atingir 8/10")
    else:
        print("\n❌ SEM MELHORIA SIGNIFICATIVA")
    
    return {
        'original_score': original_score,
        'improved_score': improved_score,
        'original_issues': original_issues,
        'improved_issues': improved_issues
    }

if __name__ == '__main__':
    results = compare_files()