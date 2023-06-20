import json
import math
import time
import wave

from django.core.handlers.wsgi import WSGIRequest
from rest_framework.views import APIView
from rest_framework.response import Response

from audio_sender.rabbitmq import QueueHelper


class AudioSenderView(APIView):

    def post(self, request: WSGIRequest) -> Response:
        """Simple POST api to start the flow"""

        audio_file_obj = request.FILES.get('audio_file')

        if not audio_file_obj:
            return Response({'status': 'ERROR', 'detail': 'No audio file found!'}, status=400)
        if not audio_file_obj.name.endswith('.wav'):
            return Response({'status': 'ERROR', 'detail': 'only .wav extension is supported'}, status=400)

        with wave.open(audio_file_obj, 'rb') as audio_file:

            frame_rate = audio_file.getframerate()
            if frame_rate > 16000:
                return Response(
                    {'status': 'ERROR', 'detail': f'audio file frame rate is {frame_rate} should be less than 16 kHz'},
                    status=400)

            # Calculate the total number of frames in 20ms
            part_frames = math.ceil(frame_rate * 0.02)

            # start reading frames from the start in parts
            audio_part_number = 0
            api_response_messages = list()
            while True:
                audio_part_number += 1
                audio_part = audio_file.readframes(part_frames)

                if not audio_part:
                    break

                QueueHelper.send_to_audio_queue(data=audio_part)

                # After sending 500 audio parts, wait for message from microservice B if it contains speech or not
                if audio_part_number % 500 == 0:

                    # we need to wait for a few seconds to get response from microservice-B
                    time.sleep(5)

                    message_str = QueueHelper.get_message_from_queue(queue_name='contains-speech-ack')
                    message_dict = json.loads(message_str)

                    if message_dict['contains_speech']:
                        _msg = f'SPEECH detected in audio part starting from {audio_part_number - 500} to {audio_part_number}'
                        print(_msg)
                        api_response_messages.append(_msg)
                    else:
                        _msg = f'No SPEECH detected in 500 parts, stopping processing!'
                        print(_msg)
                        api_response_messages.append(_msg)
                        break

        return Response({'status': 'SUCCESS', 'detail': f'{str(api_response_messages)}'}, status=200)

