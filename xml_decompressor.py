import gzip
import bz2
import lzma
import base64
import xml.etree.ElementTree as ET
import os
import argparse
import sys

# Dizionario decompressori disponibili
DECOMPRESSORS = {
    "gzip": gzip.decompress,
    "bz2": bz2.decompress,
    "lzma": lzma.decompress
}

def detect_compression_type(filename):
    """Determina il tipo di compressione in base al suffisso del nome file"""
    for comp in DECOMPRESSORS.keys():
        if filename.endswith(f"_{comp}.xml"):
            return comp
    return None

def decompress_and_extract_xml(input_file):
    """Estrai e decomprimi il contenuto di un file XML con CDATA"""
    if not os.path.isfile(input_file):
        print(f"Errore: Il file '{input_file}' non esiste.")
        sys.exit(1)

    compression = detect_compression_type(input_file)
    
    if compression is None:
        print(f"Errore: Impossibile determinare il tipo di compressione da '{input_file}'.")
        sys.exit(1)

    tree = ET.parse(input_file)
    root = tree.getroot()
    content_element = root.find("content")

    if content_element is None or not content_element.text:
        print(f"Errore: Il file '{input_file}' non contiene dati compressi validi.")
        sys.exit(1)

    encoded_data = content_element.text.strip()
    if not encoded_data.startswith("<![CDATA[") or not encoded_data.endswith("]]>"):
        print("Errore: Il contenuto non è in formato CDATA.")
        sys.exit(1)

    encoded_data = encoded_data[9:-3]  # Rimuove `<![CDATA[` e `]]>`
    
    try:
        compressed_data = base64.b64decode(encoded_data)
        xml_content = DECOMPRESSORS[compression](compressed_data).decode("utf-8")
    except Exception as e:
        print(f"Errore nella decompressione: {e}")
        sys.exit(1)

    output_file = input_file.replace(f"_{compression}.xml", "_utf-8.xml")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"File decompresso: {output_file}")

def main():
    """Gestisce la CLI"""
    parser = argparse.ArgumentParser(description="Estrai e decomprimi un file XML con CDATA.")
    parser.add_argument("input_file", help="File XML compresso da decomprimere")

    args = parser.parse_args()
    decompress_and_extract_xml(args.input_file)

if __name__ == "__main__":
    main()
