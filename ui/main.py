#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ui.main_window import MarkitdownConverterApp
from utils.logger import setup_logger

def main():
    logger = setup_logger()
    logger.info("Iniciando Markitdown Converter...")
    app = MarkitdownConverterApp(logger)
    app.run()

if __name__ == "__main__":
    main()
