Audio
Create transcription
POST
https://api.groq.com/openai/v1/audio/transcriptions

Transcribes audio into the input language.
Request Body

model
string
Required
ID of the model to use. whisper-large-v3 and whisper-large-v3-turbo are currently available.
file
string
Optional
The audio file object (not file name) to transcribe, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm. Either a file or a URL must be provided. Note that the file field is not supported in Batch API requests.
language
string
Optional
The language of the input audio. Supplying the input language in ISO-639-1 format will improve accuracy and latency.
prompt
string
Optional
An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language.
response_format
string
Optional
Defaults to json
Allowed values: json, text, verbose_json
The format of the transcript output, in one of these options: json, text, or verbose_json.
temperature
number
Optional
Defaults to 0
The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit.
timestamp_granularities[]
array
Optional
Defaults to segment
The timestamp granularities to populate for this transcription. response_format must be set verbose_json to use timestamp granularities. Either or both of these options are supported: word, or segment. Note: There is no additional latency for segment timestamps, but generating word timestamps incurs additional latency.
url
string
Optional
The audio URL to translate/transcribe (supports Base64URL). Either a file or a URL must be provided. For Batch API requests, the URL field is required since the file field is not supported.
Response Object

text
string
The transcribed text.

curl

curl https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@./sample_audio.m4a" \
  -F model="whisper-large-v3"
Example Response

{
  "text": "Your transcribed text appears here...",
  "x_groq": {
    "id": "req_unique_id"
  }
}
Create translation
POST
https://api.groq.com/openai/v1/audio/translations

Translates audio into English.
Request Body

model
string
Required
ID of the model to use. whisper-large-v3 and whisper-large-v3-turbo are currently available.
file
string
Optional
The audio file object (not file name) translate, in one of these formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.
prompt
string
Optional
An optional text to guide the model's style or continue a previous audio segment. The prompt should be in English.
response_format
string
Optional
Defaults to json
Allowed values: json, text, verbose_json
The format of the transcript output, in one of these options: json, text, or verbose_json.
temperature
number
Optional
Defaults to 0
The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit.
url
string
Optional
The audio URL to translate/transcribe (supports Base64URL). Either file or url must be provided. When using the Batch API only url is supported.
Response Object

text
string

curl

curl https://api.groq.com/openai/v1/audio/translations \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F file="@./sample_audio.m4a" \
  -F model="whisper-large-v3"
Example Response

{
  "text": "Your translated text appears here...",
  "x_groq": {
    "id": "req_unique_id"
  }
}
Create speech
POST
https://api.groq.com/openai/v1/audio/speech

Generates audio from the input text.
Request Body

input
string
Required
The text to generate audio for.
model
string
Required
One of the available TTS models.
voice
string
Required
The voice to use when generating the audio. List of voices can be found here.
response_format
string
Optional
Defaults to mp3
Allowed values: flac, mp3, mulaw, ogg, wav
The format of the generated audio. Supported formats are flac, mp3, mulaw, ogg, wav.
sample_rate
integer
Optional
Defaults to 48000
Allowed values: 8000, 16000, 22050, 24000, 32000, 44100, 48000
The sample rate for generated audio
speed
number
Optional
Defaults to 1
Range: 0.5 - 5
The speed of the generated audio.
Returns

Returns an audio file in wav format.


