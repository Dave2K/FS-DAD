"""
Generatore XML con supporto a:
- Pattern di inclusione/esclusione
- Gestione gerarchica delle cartelle
- CDATA per file di testo
- vuoto per file binari (non riconosciuti come testo)
"""

import os
import fnmatch
import datetime
from xmlnode import XMLNode
from FileHandler import FileHandler
from logging_utils import get_logger, get_log_message

logger = get_logger(__name__)

def create_xml_with_indent(
    target_path_folder,
    output_file,
    ignore_folders=[],
    ignore_files=[],
    indent="",
    include_folders=[ "*" ],
    split_content=True
):
    """
    Genera un XML rappresentante la struttura del filesystem.
    :param target_path_folder: Percorso della cartella da analizzare
    :param output_file: Percorso del file XML di output
    :param ignore_folders: Lista di cartelle da ignorare
    :param ignore_files: Lista di file da ignorare
    :param indent: Stringa di indentazione
    :param include_folders: Lista di pattern per includere cartelle
    :return: Tupla (successo: bool, messaggio: str)
    """
    
    def process_content(
            file_handler_instance : FileHandler,
            indent_level,
            indent="", 
            split_content=True 
        ):
        """
        Elabora il contenuto del file per l'inserimento in XML.
        :param file_info: Dizionario con le informazioni del file
        :param indent_level: Livello di indentazione
        :param indent: Stringa di indentazione (default: 2 spazi)
        :return: Contenuto formattato per CDATA
        """
        fh = file_handler_instance
        if not fh.has_info_been_read:
            fh.get_info()
        
        content_processed = ""

        try:
            content_file, _ = fh.read()
        except Exception as e:
            msg_err = f"read file: {fh.name} errore: {str(e)}"
            logger.error(msg_err)
        
        is_text, msgError = fh.is_text()
        if is_text:
            if split_content:
                indent_str = indent * (indent_level + 1)                

                lines = content_file.splitlines()

                formatted_content = "\n".join(f"{indent_str}{line}" for line in lines)                
                content_processed = f"<![CDATA[\n{formatted_content}\n{indent_str}]]>"
            else:
                try:
                    content_encoded = content_file.encode()
                except Exception as e:
                    msg_err = f"Errore encode {str(e)}"
                    logger.error(msg_err)
                content_processed = f"<![CDATA[{content_encoded}]]>"

        else:
            msg = f"File riconsciuto come binario Mime: {fh.mime}  Encoding: {fh.encoding}  File: {fh.file_path}"
            content_processed = msg
            logger.warning(msg)

        return content_processed

    def add_element(
            parent, 
            current_dir, 
            indent_level, 
            ignore_folders=[], ignore_files=[], 
            include_folders=["*"], 
            allow_files=False, 
            split_content=True
        ):
        """
        Aggiunge elementi all'XML in modo ricorsivo, ignorando le cartelle e i file specificati. 
        Forza l'inclusione di tutte le cartelle e i file, tranne quelli in ignore_folders e ignore_files.

        :param parent: Nodo XML genitore
        :param current_dir: Cartella corrente
        :param indent_level: Livello di indentazione
        :param ignore_folders: Lista di cartelle da ignorare
        :param ignore_files: Lista di file da ignorare
        :param include_folders: Lista di pattern per includere cartelle
        :param allow_files: Se True, permette il processamento dei file anche se la cartella non matcha include_folders
        """
        # Verifica se la cartella corrente matcha con include_folders
        current_folder_matches = any(fnmatch.fnmatch(os.path.basename(current_dir), pattern) for pattern in include_folders)
        allow_files = allow_files or current_folder_matches

        # Ottieni il nome della cartella corrente
        dir_name = os.path.basename(current_dir)
        logger.debug(f"Elaborazione della cartella: {dir_name}")

        # Crea il nodo XML per la cartella corrente
        folder_node = XMLNode("Folder", {"Name": dir_name})
        parent.add_child(folder_node)

        # Elabora tutte le cartelle e i file nella cartella corrente
        for entry in os.listdir(current_dir):
            entry_path = os.path.join(current_dir, entry)

            # Se è una cartella
            if os.path.isdir(entry_path):
                # Verifica se la cartella deve essere ignorata
                if any(fnmatch.fnmatch(entry, pattern) for pattern in ignore_folders):
                    logger.debug(f"Ignorata cartella: {entry}")
                    continue

                # Aggiungi la cartella all'XML (ricorsivamente)
                add_element(folder_node, entry_path, 
                            indent_level + 1, 
                            ignore_folders, ignore_files, include_folders, 
                            allow_files, split_content)

            # Se è un file
            else:
                # Verifica se il file deve essere ignorato
                if any(fnmatch.fnmatch(entry, pattern) for pattern in ignore_files):
                    logger.debug(f"Ignorato file: {entry}")
                    continue

                # Se allow_files è True, processa il file
                if allow_files:
                    # Ottieni le informazioni del file
                    fh = FileHandler(entry_path)
                    result, msg_err = fh.exists()                    
                    if not result:
                        logger.warning(f"File non trovato: {fh.nameentry}: {msg_err}")
                        continue

                    fh.get_info()

                    # Crea il nodo XML per il file
                    attributes = {
                        "Name": fh.name,
                        "Size": str(fh.size),
                    }
                    node_file = XMLNode("File", attributes)
                    indent_level += 1

                    try:
                        content = process_content(fh, indent_level + 1, indent, split_content)
                    except Exception as e:
                        msg_err = f"Errore elaborazione processo contenuto: {str(e)}"
                        content = ""
                        logger.error(msg_err)

                    # Crea il nodo content
                    attributes = {
                        "MIME": fh.mime,
                        "Encoding": fh.encoding
                    }
                    if fh.bom:
                        attributes["BOM"] = "True"
                    node_content = XMLNode("Content", attributes)
                    indent_level += 1
                    node_content.set_text(content)
                    node_file.add_child(node_content); indent_level -= 1

                    folder_node.add_child(node_file); indent_level -= 1   
   
    # Struttura base XML    
    node_dad = XMLNode("DataArchitectureDesign", {
        "Author": "Davide"
        })
    indent_initial_level = 0

    node_creation = XMLNode("Creation", {
        "Date": datetime.datetime.now().strftime("%d-%m-%Y"),
        "Hour": datetime.datetime.now().strftime("%H:%M:%S")
        })
    node_dad.add_child(node_creation)
    indent_initial_level += 1

    node_filesystem = XMLNode("FileSystem")
    node_dad.add_child(node_filesystem)
    indent_initial_level += 1

    add_element(
        parent=node_filesystem, 
        current_dir=target_path_folder, 
        indent_level=indent_initial_level, 
        ignore_folders=ignore_folders, 
        ignore_files=ignore_files, 
        include_folders=include_folders,
        split_content=split_content
    )

    # Scrittura file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(node_dad.to_xml(indent=indent))

    return True, f"XML generato: {output_file}"