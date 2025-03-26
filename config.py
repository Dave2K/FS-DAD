"""
Gestione centralizzata della configurazione con validazione integrata.
Include:
- Caricamento da file JSON
- Creazione configurazione di default
- Validazione avanzata
- Gestione dei placeholder
"""

import os
import json
import datetime
from logging_utils import get_logger, get_log_message

logger = get_logger(__name__)

class Config:
    """Classe per la gestione della configurazione con costanti unificate."""
    
    # Costanti per le chiavi di configurazione
    TARGET_PATH_FOLDER = "target_path_folder"
    OUTPUT_PATH_FILE = "output_path_file"
    INCLUDE_FOLDERS = "include_folders"
    EXCLUDE_FOLDERS = "exclude_folders"
    EXCLUDE_FILES = "exclude_files"
    SPLIT_CONTENT = "split_content"

    SUPPORTED_PLACEHOLDERS = ["{target}", "{timestamp}"]
    DEFAULT_FILE_NAME_CONFIG = "config.json"

    DEFAULT_CONFIG = {
        TARGET_PATH_FOLDER: "/Path/Target_Folder",
        OUTPUT_PATH_FILE: "{target}.xml",
        SPLIT_CONTENT: False,
        INCLUDE_FOLDERS: ["*"],
        EXCLUDE_FOLDERS: [
            "bin", 
            "obj", 
            "debug", 
            "release",
            "_backup", 
            "__pycache__", 
            ".vscode", 
            ".vs", 
            "*.git*", 
            "_artifacts"
        ],
        EXCLUDE_FILES: [
            ".gitignore", 
            ".gitattributes",
            "*.tmp", 
            "*.log", 
            "*.xml"
        ]
    }

    def __init__(self, config_file=None):
        """
        Inizializza la configurazione.
        :param config_file: Percorso del file di configurazione (opzionale)
        """
        self.config_file_name = config_file or Config.DEFAULT_FILE_NAME_CONFIG
        self.config = {}
        self.load()

    def load(self):
        """
        Carica la configurazione da file JSON.
        Se il file non esiste, crea una configurazione di default.
        """
        if os.path.exists(self.config_file_name):
            try:
                with open(self.config_file_name, "r") as f:
                    self.config = json.load(f)
                logger.debug(f"Configurazione caricata da {self.config_file_name}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Errore caricamento config: {str(e)}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """
        Crea una configurazione di default e la salva su file.
        """
        self.config = Config.DEFAULT_CONFIG
        try:
            self._write_file()
            logger.info(f"Creato file config di default: {self.config_file_name}")
        except Exception as e:
            logger.error(f"Errore creazione config: {str(e)}")

    def _write_file(self):
        """
        Scrive la configurazione su file JSON.
        """
        with open(self.config_file_name, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key):
        """
        Restituisce il valore di una chiave.
        :param key: Chiave da cercare
        :return: Valore della chiave o None se non esiste
        """
        return self.config.get(key)

    def _extract_placeholders(self, template):
        """
        Estrae i placeholder da un template.
        :param template: Stringa contenente i placeholder (es. "{target}.xml")
        :return: Lista di placeholder trovati (es. ["{target}"])
        """
        import re
        return re.findall(r"\{[^}]+\}", template)

    def get_output_file_path(self, target_path_folder):
        """
        Calcola il percorso del file di output sostituendo i placeholder.
        Verifica che i placeholder siano supportati.
        
        :param target_path_folder: Percorso della cartella target
        :return: Percorso del file di output
        :raises ValueError: Se il template contiene placeholder non supportati
        """
        logger.debug(f"Inizio calcolo percorso di output per: {target_path_folder}")

        # 1. Verifica che il percorso della cartella target sia valido
        if not target_path_folder:
            logger.error("Il percorso della cartella target è vuoto")
            raise ValueError("Il percorso della cartella target è vuoto")

        # 2. Ottieni il nome della cartella target
        target_name = os.path.basename(os.path.normpath(target_path_folder))
        logger.debug(f"Nome della cartella target: {target_name}")

        # 3. Ottieni il template di output dal file di configurazione
        output_template = self.get(self.OUTPUT_PATH_FILE)
        logger.debug(f"Template di output: {output_template}")

        # 4. Verifica che il template non sia vuoto
        if not output_template:
            logger.error("Il template di output è vuoto")
            raise ValueError("Il template di output è vuoto")

        # 5. Verifica che tutti i placeholder nel template siano supportati
        for placeholder in self._extract_placeholders(output_template):
            if placeholder not in self.SUPPORTED_PLACEHOLDERS:
                logger.error(
                    f"Il template di output '{output_template}' contiene placeholder non supportati. "
                    f"Placeholder supportati: {self.SUPPORTED_PLACEHOLDERS}"
                )
                raise ValueError(
                    f"Il template di output '{output_template}' contiene placeholder non supportati. "
                    f"Placeholder supportati: {self.SUPPORTED_PLACEHOLDERS}"
                )

        # 6. Prepara i valori per i placeholder
        placeholders = {
            "target": target_name,  # Nome della cartella target
            "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Timestamp opzionale
        }
        logger.debug(f"Placeholders: {placeholders}")

        # 7. Sostituisci i placeholder nel template
        try:
            output_file = output_template.format(**placeholders)
            logger.debug(f"Percorso di output generato: {output_file}")
        except KeyError as e:
            logger.error(f"Errore durante la sostituzione dei placeholder: {str(e)}")
            raise KeyError(f"Placeholder non valido nel template: {str(e)}")

        # 8. Restituisci il percorso di output generato
        return output_file

    def validate(self):
        """
        Valida la configurazione.
        :return: Tupla (successo: bool, messaggio: str)
        """
        required = [self.TARGET_PATH_FOLDER, self.OUTPUT_PATH_FILE]
        for field in required:
            if not self.config.get(field):
                return False, f"Campo mancante: {field}"
        return True, "Configurazione valida"

    def to_dict(self):
        """
        Restituisce la configurazione come dizionario.
        :return: Dizionario della configurazione
        """
        return self.config

    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza da un dizionario.
        :param data: Dizionario con i dati di configurazione
        :return: Tupla (istanza: Config, successo: bool, messaggio: str)
        """
        config = cls()
        config.config = data
        valid, msg = config.validate()
        return config if valid else None, valid, msg