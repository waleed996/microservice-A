# microservice-A (Audio Sender)
Send audio file to microservice-B in parts using rabbitmq queue.

## Explanation
The start is triggered by a simple POST api call, sending the audio file in 'form-data' from postman.
Below is the curl request you can use, update the 'assignment_audio.wav' path according to your system.

```
curl --location 'http://127.0.0.1:8001/audio-sender/api/v1/upload-audio-file' --form 'audio_file=@"/path/to/assignment_audio.wav"'
```

After the file object is created, in the api some basic checks regarding format, extension and frame rate are done.
Number of frames in 20ms are calculated using the frame rate. Using the 'wave' module the number of frames are
retrieved and each 20ms part is sent to the 'audio-parts' rabbitmq queue in bytes. After sending 500 20ms byte messages
the service goes to sleep for 5 seconds. The idea here is that microservice-B needs a few seconds to process the
500 messages and send an acknowledgement using the 'contains-speech-ack' queue. I understand that logically in a real
world case this is not the right thing to do but just to make it simple because of time and effort constraints, i have
done it like this for now.

# How to Run
I have included a docker compose file with this service. Please clone both services in the same folder and 
from microservice-A project directory run
```
docker-componse up
```
this will create the containers for both services and rabbitmq. Microservice-A will run on port 8001 and microservice-B
on port 8002.
