import gzip
import bz2
import lzma
import base64
import xml.etree.ElementTree as ET
import os
import argparse
import sys

# Dizionario compressori disponibili
COMPRESSORS = {
    "gzip": gzip.compress,
    "bz2": bz2.compress,
    "lzma": lzma.compress
}

def compress_and_wrap_xml(input_file, compression):
    """Comprimi il file XML e avvolgilo in un nuovo XML con CDATA"""
    if not os.path.isfile(input_file):
        print(f"Errore: Il file '{input_file}' non esiste.")
        sys.exit(1)

    if compression not in COMPRESSORS:
        print(f"Errore: Compressione '{compression}' non supportata. Scegli tra: {', '.join(COMPRESSORS.keys())}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        xml_content = f.read()

    compressed_data = COMPRESSORS[compression](xml_content.encode("utf-8"))
    encoded_data = base64.b64encode(compressed_data).decode("utf-8")

    root = ET.Element("root")
    content = ET.SubElement(root, "content", compression=compression)
    content.text = f"<![CDATA[{encoded_data}]]>"

    base_name, _ = os.path.splitext(input_file)
    output_file = f"{base_name}_{compression}.xml"

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    print(f"File salvato: {output_file}")

def main():
    """Gestisce la CLI"""
    parser = argparse.ArgumentParser(description="Comprimi un file XML e avvolgilo in un nuovo XML con CDATA.")
    parser.add_argument("input_file", help="File XML di input")
    parser.add_argument("--compression", choices=COMPRESSORS.keys(), default="lzma",
                        help="Tipo di compressione (default: lzma)")

    args = parser.parse_args()
    compress_and_wrap_xml(args.input_file, args.compression)

if __name__ == "__main__":
    main()
