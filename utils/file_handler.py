#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitários de manipulação de arquivos para o Markitdown Converter.

Fornece informações básicas sobre arquivos usadas pela UI e pelo conversor.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class FileHandler:
    """
    Fornece operações utilitárias relacionadas a arquivos.
    """

    def get_file_info(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)

        info: Dict[str, Any] = {
            "path": str(path),
            "absolute_path": str(path.resolve()) if path.exists() else str(path.absolute()),
            "name": path.name,
            "stem": path.stem,
            "suffix": path.suffix.lower(),
            "parent": str(path.parent),
            "exists": path.exists(),
        }

        try:
            stat = path.stat()
            info.update(
                {
                    "size_bytes": stat.st_size,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
            )
        except Exception:
            # Arquivo pode não existir ou não ser acessível
            info.update({"size_bytes": None, "modified_time": None, "created_time": None})

        return info



