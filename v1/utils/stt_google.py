from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io

def stt_recognize(local_file_path, leng_code="es-CL", sample_rate=16000):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1.SpeechClient()

    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": leng_code,
        "sample_rate_hertz": sample_rate,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    for result in response.results:
        alternative = result.alternatives[0]
        
    return alternative
