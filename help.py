"""
Modulo per visualizzare le informazioni di aiuto del programma.
Include esempi pratici per ogni opzione.
"""

def display_help(name_main):
    """
    Mostra le informazioni di aiuto per l'uso del programma.
    :param name_main: Nome del file principale
    """
    help_text = f"""
    Utilizzo:
      python {name_main} [OPZIONI]

    Opzioni:
      --config <file>    Specifica un file di configurazione (default: config.json)
      --target <dir>     Specifica la directory da analizzare
      --output <file>    Specifica il file XML di output
      --include <pat>    Processa solo le cartelle che corrispondono al pattern
      --help             Mostra questo messaggio di aiuto

    Esempi:
      1. Analizza una cartella specifica:
         python {name_main} --target "c:\\sources\\FS-DAD"

      2. Genera un file XML con un nome specifico:
         python {name_main} --target "c:\\sources\\FS-DAD" --output "output.xml"

      3. Usa un file di configurazione personalizzato:
         python {name_main} --config "custom_config.json"

      4. Includi solo cartelle che corrispondono a un pattern:
         python {name_main} --include "src/*,tests/*"

      5. Escludi cartelle specifiche:
         Modifica il file config.json e aggiungi le cartelle da escludere
         sotto la chiave "exclude_folders".

    Configurazione:
      Modifica il file config.json per specificare:
        - target_path_folder: Directory da analizzare
        - output_file: File XML di output
        - exclude_dirs: Directory da escludere
        - exclude_files: File da escludere
        - include_folders: Pattern per includere cartelle

      Nota: I parametri CLI sovrascrivono quelli nel file di configurazione.
    """
    print(help_text)