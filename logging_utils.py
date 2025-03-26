import logging

class ColoredFormatter(logging.Formatter):
    """
    Formattatore per i log con colori in base al livello di debug.
    """
    debug = "\x1b[37;20m"    # bianco per DEBUG
    success = "\x1b[32;20m"  # Verde per SUCCESS
    info = "\x1b[36;20m"     # Azzurro per INFO
    warning = "\x1b[33;20m"  # Giallo per WARNING
    error = "\x1b[31;20m"    # Rosso per ERROR
    reset = "\x1b[0m"        # Reset colore
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    FORMATS = {
        logging.DEBUG: debug + format + reset,
        logging.INFO: info + format + reset,
        logging.WARNING: warning + format + reset,
        logging.ERROR: error + format + reset,
        logging.CRITICAL: error + format + reset
    }


    def format(self, record):
        """
        Formatta il messaggio di log con il colore appropriato.
        :param record: Record di log da formattare.
        :return: Messaggio di log formattato.
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

def get_logger(name):
    """
    Restituisce un logger specifico per il modulo con formattazione colorata.
    :param name: Nome del modulo.
    :return: Logger configurato.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Rimuovi handler esistenti per evitare duplicati
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Aggiungi handler con formattazione colorata
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColoredFormatter())
    logger.addHandler(ch)

    return logger

def get_log_message(message):
    """
    Restituisce il messaggio di log senza prefisso.
    :param message: Messaggio di log.
    :return: Messaggio di log senza prefisso.
    """
    return message