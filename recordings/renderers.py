from rest_framework_xml.renderers import XMLRenderer
from xml.sax.saxutils import XMLGenerator, quoteattr
from django.utils.encoding import force_str
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

    def _to_xml(self, xml, data, attrs={}):
        if isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, dict) and "attrs" in item.keys():
                    attrs = item.pop("attrs", {})
                xml.startElement(self.item_tag_name, attrs)
                self._to_xml(xml, item)
                xml.endElement(self.item_tag_name)

        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and "attrs" in value.keys():
                    attrs = value.pop("attrs", {})
                    value = value.get(key) or value
                xml.startElement(key, attrs)
                self._to_xml(xml, value)
                xml.endElement(key)
                attrs = {}

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_str(data))

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


class ProjectXMLRenderer(CustomXMLRenderer):
    xml_attrs = {"standalone": "no"}
    root_tag = ("ProjectConfiguration", {"version": "4.0.0"})


class SpeakerXMLRenderer(CustomXMLRenderer):
    xml_attrs = {"standalone": "yes"}
    root_tag = ("speakers", {})
    item_tag_name = "speakers"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """

        if data is None:
            return ""

        stream = StringIO()

        xml = XMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement("speakers", {})
        xml.startElement("speakers", {})

        self._to_xml(xml, data)

        xml.endElement("speakers")
        xml.endElement("speakers")
        xml.endDocument()
        return stream.getvalue()


class ScriptXMLRenderer(CustomXMLRenderer):
    root_tag_name = "script"
    item_tag_name = "recording"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """

        if data is None:
            return ""

        stream = StringIO()

        xml = XMLGenerator(stream, self.charset)
        xml.startDocument()
        xml._write('<!DOCTYPE script SYSTEM "SpeechRecPrompts_4.dtd">')

        self._to_xml(xml, data)

        xml.endDocument()
        return stream.getvalue()
