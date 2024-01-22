from rest_framework_xml.renderers import XMLRenderer
from xml.sax.saxutils import XMLGenerator
from django.utils.encoding import force_str
from speech_recording.xml_renderer import CustomXMLRenderer
from io import StringIO


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
