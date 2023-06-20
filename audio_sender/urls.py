
from django.urls import path
from audio_sender.views import AudioSenderView

urlpatterns = [
    path('api/v1/upload-audio-file', AudioSenderView.as_view(), name='audio-upload-v1')
]
