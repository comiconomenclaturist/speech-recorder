from rest_framework_xml.renderers import XMLRenderer
from xml.sax.saxutils import XMLGenerator, quoteattr
from io import StringIO


class CustomXMLGenerator(XMLGenerator):
    def startDocument(self, attrs):
        self._write(f'<?xml version="1.0" encoding="{self._encoding}"')

        for name, value in attrs.items():
            self._write(f" {name}={quoteattr(value)}")

        self._write("?>\n")


class CustomXMLRenderer(XMLRenderer):
    xml_attrs = {}
    root_tag = ("root", {})

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """

        stream = StringIO()

        xml = CustomXMLGenerator(stream, self.charset)
        xml.startDocument(self.xml_attrs)
        xml.startElement(*self.root_tag)

        self._to_xml(xml, data)

        xml.endElement(self.root_tag[0])
        xml.endDocument()
        return stream.getvalue()
