import os
import mimetypes
from charset_normalizer import from_path
from logging_utils import get_logger, get_log_message

logger = get_logger(__name__)
class FileHandler:
    """Classe per gestire file, determinare tipo, encoding e leggere contenuto."""

    def __init__(self, file_path):
        """
        Inizializza l'istanza con il percorso del file.

        :param file_path: Il percorso completo del file da gestire
        """
        self.file_path = file_path
        self.has_info_been_read = False
        self.name = None
        self.size = None
        self.encoding = None
        self.coherence = None
        self.bom = None
        self.mime = None
        self.type = None

    def get_info(self):
        """
        Ottiene le informazioni del file, tra cui nome, dimensione, encoding, MIME, ecc.

        :return: Dizionario con le informazioni del file
        """
        # Ottieni nome e dimensione del file
        self.name = os.path.basename(self.file_path)
        self.size = os.path.getsize(self.file_path)

        # Determina tipo di file (testo o binario)
        result = from_path(self.file_path).best()
        if result:
            self.encoding = result.encoding
            self.bom = result.bom

        mime, _ = mimetypes.guess_type(self.file_path)
        self.mime = mime

        self.has_info_been_read = True

    def read(self):
        """
        Legge il contenuto del file.

        :return: Tupla (contenuto, errore)
        """
        try:
            if self.has_info_been_read:
                self.get_info()

            mode = "r" if self.is_text() else "rb"
            with open(self.file_path, mode) as f:
                content = f.read()
                return content, None
        except Exception as e:
            return None, f"Errore lettura file {self.file_path}: {str(e)}"

    def exists(self):
        """
        Verifica se il file esiste.
        
        :return: Tupla (success, errore)
        """
        value = True
        msg_err = None
        
        if not os.path.exists(self.file_path):
            msg_err = f"Il file {self.file_path} non esiste."
            logger.error(msg_err)
            value = False

        return value, msg_err
        
    def is_text(self):
        """
        Verifica se il file è di tipo testo in base al MIME type e all'encoding.

        :return: Tupla (True/False, errore) - True se il file è di tipo testo, False altrimenti,
                con eventuale messaggio di errore.
        """ 
        if self.has_info_been_read:
                self.get_info()
       
        value = None
        msg_err = None
        main_mime = None
        if self.mime:
            try:
                main_mime = self.mime.split('/')[0]                
            except Exception as e:
                msg_err = f"file: {self.name} errore: {str(e)}"
                logger.error(msg_err)


        match main_mime:
            case "text":
                value = True
            case _:
                match self.encoding:
                    case "ascii" | "utf_8": # | "utf_16" | "cp1252" | "cp1258" | "mac_roman" :
                        value = True
                    case _:
                        value = False

        if not value:
            msg_err = f"file {self.name} mime: {self.mime} encoding: {self.encoding}"
            # logger.warning(msg_err)

        return value, msg_err