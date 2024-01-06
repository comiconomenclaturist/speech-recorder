from rest_framework_xml.renderers import XMLRenderer
from xml.sax.saxutils import XMLGenerator
from io import StringIO


class CustomXMLGenerator(XMLGenerator):
    def startDocument(self):
        self._write(
            f'<?xml version="1.0" encoding="{self._encoding}" standalone="yes"?>\n'
        )


class CustomXMLRenderer(XMLRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """

        app_name = renderer_context["request"].resolver_match.namespace

        if app_name:
            self.root_tag_name = self.item_tag_name = app_name

        if data is None:
            return ""

        stream = StringIO()

        xml = CustomXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, {})

        self._to_xml(xml, data)

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        return stream.getvalue()
