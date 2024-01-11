from rest_framework_xml.renderers import XMLRenderer
from xml.sax.saxutils import XMLGenerator
from django.utils.encoding import force_str
from speech_recording.xml_renderer import CustomXMLRenderer
from io import StringIO


class SpeakerXMLRenderer(CustomXMLRenderer):
    root_tag_name = "speakers"
    item_tag_name = "speakers"


class ScriptXMLRenderer(XMLRenderer):
    root_tag_name = "script"
    item_tag_name = "mediaitem"

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

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement(self.item_tag_name, {"languageISO639code": "en"})
                self._to_xml(xml, item)
                xml.endElement(self.item_tag_name)

        elif isinstance(data, dict):
            pk = data.get("id", 0)
            xml.startElement(self.root_tag_name, {"id": f"script_{pk}"})
            xml.startElement("recordingscript", {})
            xml.startElement(
                "section",
                {
                    "name": f"script_{data.get('id', 0)}",
                    "promptphase": "recording",
                    "speakerdisplay": "true",
                },
            )
            for index, (key, value) in enumerate(data.items()):
                if key != "id":
                    xml.startElement(
                        key, {"finalsilence": "4000", "itemcode": str(index).zfill(4)}
                    )
                    xml.startElement("recprompt", {})
                    self._to_xml(xml, value)
                    xml.endElement("recprompt")
                    xml.endElement(key)
            xml.endElement("section")
            xml.endElement("recordingscript")
            xml.endElement(self.root_tag_name)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(force_str(data))
