"""
Main script per la generazione di XML da filesystem.
Include:
- Gestione parametri CLI
- Integrazione con configurazione
- Logging avanzato
"""

import json
import os
import argparse
from config import Config
from xml_generator import create_xml_with_indent
from logging_utils import get_logger, get_log_message

logger = get_logger(__name__)

def load_or_create_config(config_file):
    """
    Carica o crea la configurazione.
    :param config_file: Percorso del file di configurazione
    :return: Tupla (config: Config, messaggio: str)
    """
    try:
        if not os.path.exists(config_file):
            default_config = Config()
            # default_config.insert(Config.INCLUDE_FOLDERS, ["*"])
            with open(config_file, "w") as f:
                json.dump(default_config.to_dict(), f, indent=4)
            return None, f"File {config_file} non trovato. File config di default creato: {config_file}"
        
        with open(config_file, "r") as f:
            config_data = json.load(f)
            config, success, msg = Config.from_dict(config_data)
            return config if success else None, msg
    except Exception as e:
        return None, f"Errore critico: {str(e)}"

def main():
    """Punto di ingresso principale."""
    parser = argparse.ArgumentParser(description="Genera XML da struttura cartelle")
    parser.add_argument("--config", help="Percorso file configurazione")
    parser.add_argument("--target", help="Cartella target")
    parser.add_argument("--output", help="File output XML")
    parser.add_argument("--include", help="Pattern inclusione cartelle (separati da virgola)")
    parser.add_argument("--split-content", help="Parametro opzionale per gestire il contenuto")
    args = parser.parse_args()

    # Caricamento configurazione
    config_file = args.config
    if not config_file:
        logger.debug(f"parametro config non trovato. Impostazione predefinita {Config.DEFAULT_FILE_NAME_CONFIG}")
        config_file = Config.DEFAULT_FILE_NAME_CONFIG
    
    config, msg = load_or_create_config(config_file)
    if not config:
        logger.error(f"Errore configurazione: {msg}")
        return

    # Gestione parametri
    target_path = args.target or config.get(Config.TARGET_PATH_FOLDER)
    if os.path.isfile(target_path):
        logger.error(f"{target_path} è un file, deve essere un cartella")
        return
    elif not os.path.exists(target_path):
        logger.error(f"Cartella non trovata: {target_path}")
        return                

    output_file = args.output or config.get_output_file_path(target_path)
    include_folders = args.include.split(",") if args.include else config.get(Config.INCLUDE_FOLDERS)
    split_content = args.split_content if args.split_content else config.get(Config.SPLIT_CONTENT)

    # Generazione XML
    success, message = create_xml_with_indent(
        target_path_folder=target_path,
        output_file=output_file,
        ignore_folders=config.get(Config.EXCLUDE_FOLDERS),
        ignore_files=config.get(Config.EXCLUDE_FILES),
        indent="  ",
        include_folders=include_folders,
        split_content=split_content
    )
    if(success):
        logger.info(message)
    else:
        logger.error(message)

if __name__ == "__main__":
    main()