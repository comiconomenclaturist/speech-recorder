from rest_framework.viewsets import ModelViewSet

# from speech_recorder.xml_renderer import CustomXMLRenderer
from .models import Speaker
from .serializers import SpeakerSerializer


# class SpeakerXMLRenderer(CustomXMLRenderer):
#     root_tag_name = "speakers"
#     item_tag_name = "speakers"


class SpeakersViewset(ModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    # renderer_classes = [SpeakerXMLRenderer]
