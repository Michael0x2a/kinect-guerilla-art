from pykinect import nui
from pykinect.audio import KinectAudioSource
from winspeech import recognition

with nui.Runtime(nui.RuntimeOptions.UsesAudio) as kinect, KinectAudioSource() as source: 
    rec = recognition.SpeechRecognitionEngine()
    audio_file = source.start()
    rec.set_input_to_audio_file(audio_file)
    rec.load_grammar('Grammar.xml')
    print 'Recognizing...', rec.recognize_sync()
