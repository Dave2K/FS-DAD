class XMLNode:
    """Classe per rappresentare un nodo XML."""
    
    def __init__(self, tag, attributes=None):
        """
        Inizializza un nodo XML.
        :param tag: Nome del tag
        :param attributes: Dizionario degli attributi
        """
        self.tag = tag
        self.attributes = attributes if attributes else {}
        self.children = []
        self.text = ""

    def add_child(self, child):
        """Aggiunge un nodo figlio."""
        self.children.append(child)

    def set_text(self, text):
        """Imposta il testo del nodo."""
        self.text = text

    def to_xml(self, indent_level=0, indent="    "):
        """Converte il nodo in stringa XML."""
        indent_str = indent * indent_level
        attrs = " ".join([f'{k}="{v}"' for k, v in self.attributes.items()])

        if not self.children and not self.text:
            return f"{indent_str}<{self.tag}{' ' + attrs if attrs else ''}/>"

        opening_tag = f"{indent_str}<{self.tag}{' ' + attrs if attrs else ''}>"
        closing_tag = f"{indent_str}</{self.tag}>"

        xml_content = [opening_tag]
        if self.text:
            xml_content.append(f"{indent * (indent_level + 1)}{self.text}")
        for child in self.children:
            xml_content.append(child.to_xml(indent_level + 1, indent))
        xml_content.append(closing_tag)

        return "\n".join(xml_content)