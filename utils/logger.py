import logging

def setup_logger():
    logger = logging.getLogger("markitdown-converter")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(message)s')
    ch.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(ch)
    return logger

def get_logger(name: str | None = None):
    """
    Obtém um logger nomeado usando o namespace base "markitdown-converter".
    Se o logger base ainda não tiver handlers (setup_logger não foi chamado),
    um handler padrão de StreamHandler é configurado para evitar logs silenciosos.
    """
    base_name = "markitdown-converter"
    logger_name = f"{base_name}.{name}" if name else base_name
    logger = logging.getLogger(logger_name)

    base_logger = logging.getLogger(base_name)
    if not logger.handlers and not base_logger.handlers:
        # Configuração mínima para evitar ausência de handlers
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s | %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.setLevel(logging.INFO)

    return logger