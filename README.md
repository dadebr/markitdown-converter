# Markitdown Converter

## Descrição

Conversor de arquivos para Markdown (.MD) utilizando a biblioteca markitdown. Este aplicativo oferece uma interface gráfica elegante em Tkinter para converter diversos formatos de arquivo em Markdown, com opções de conversão individual ou em lote.

## Objetivos do Projeto

- **Conversão Universal**: Transformar arquivos PDF, PPT, DOCX, JSON, TXT, CSV e XLSX em formato Markdown
- **Interface Amigável**: Proporcionar uma experiência de usuário intuitiva com interface gráfica Tkinter
- **Flexibilidade**: Permitir conversão individual ou em lote de arquivos
- **Controle de Destino**: Possibilitar escolha do diretório de destino para os arquivos convertidos
- **Monitoramento**: Fornecer logs detalhados através de terminal integrado na interface
- **Eficiência**: Processar múltiplos formatos de forma rápida e confiável

## Funcionalidades Principais

### ✨ Formatos Suportados
- **PDF** - Documentos Portable Document Format
- **PPT/PPTX** - Apresentações PowerPoint
- **DOCX** - Documentos Microsoft Word
- **JSON** - Arquivos JavaScript Object Notation
- **TXT** - Arquivos de texto simples
- **CSV** - Arquivos Comma-Separated Values
- **XLSX** - Planilhas Microsoft Excel

### 🛠️ Características da Interface
- Interface gráfica intuitiva desenvolvida em Tkinter
- Seleção de arquivos individuais ou múltiplos
- Escolha de diretório de destino personalizado
- Terminal integrado para visualização de logs em tempo real
- Barra de progresso para acompanhamento da conversão
- Tratamento de erros com mensagens informativas

## Pré-requisitos

- Python 3.8+
- Biblioteca `markitdown`
- Biblioteca `tkinter` (geralmente incluída no Python)
- Dependências adicionais conforme necessário para cada formato

## Instalação

```bash
# Clone o repositório
git clone https://github.com/dadebr/markitdown-converter.git

# Entre no diretório do projeto
cd markitdown-converter

# Instale as dependências
pip install -r requirements.txt
```

## Uso

### Execução da Aplicação

```bash
# Execute o aplicativo
python main.py
```

### Fluxo de Trabalho

1. **Seleção de Arquivos**: Escolha um ou múltiplos arquivos através da interface
2. **Definição de Destino**: Selecione o diretório onde os arquivos .md serão salvos
3. **Conversão**: Inicie o processo e acompanhe o progresso no terminal integrado
4. **Resultados**: Acesse os arquivos convertidos no diretório especificado

## Estrutura do Projeto

```
markitdown-converter/
├── main.py              # Arquivo principal da aplicação
├── converter/           # Módulos de conversão
│   ├── __init__.py
│   ├── file_converter.py
│   └── batch_processor.py
├── ui/                  # Interface do usuário
│   ├── __init__.py
│   ├── main_window.py
│   └── components/
├── utils/               # Utilitários e helpers
│   ├── __init__.py
│   ├── logger.py
│   └── file_handler.py
├── requirements.txt     # Dependências do projeto
├── README.md           # Este arquivo
└── LICENSE            # Licença do projeto
```

## Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

- **Desenvolvedor**: dadebr
- **GitHub**: [https://github.com/dadebr](https://github.com/dadebr)
- **Projeto**: [https://github.com/dadebr/markitdown-converter](https://github.com/dadebr/markitdown-converter)

## Agradecimentos

- Biblioteca [markitdown](https://github.com/microsoft/markitdown) pela funcionalidade de conversão
- Comunidade Python pela documentação e recursos
- Todos os contribuidores que ajudam a melhorar este projeto
