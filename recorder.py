# -*- coding: utf-8 -*-
'''recorder.py
Provides WAV recording functionality via two approaches:

Blocking mode (record for a set duration):
>>> rec = Recorder(channels=2)
>>> with rec.open('blocking.wav', 'wb') as recfile:
...     recfile.record(duration=5.0)

Non-blocking mode (start and stop recording):
>>> rec = Recorder(channels=2)
>>> with rec.open('nonblocking.wav', 'wb') as recfile2:
...     recfile2.start_recording()
...     time.sleep(5.0)
...     recfile2.stop_recording()
'''

import pyaudio
import wave
import numpy as np
import wave
from time import strftime
import glob
import os
import matplotlib.pyplot as plt
import time

class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile
    
     # genero escalones
def escalon(n_escalones,long_escalon,desde,hasta):
    samples = np.linspace(0,1,n_escalones * long_escalon)
    samples = samples * n_escalones # solo sirve si linspace va de 0 a 1
    samples = np.floor(samples)
    samples = samples / n_escalones
    samples = desde + (hasta - desde) * samples    
    return samples
    
# %%
pa = pyaudio.PyAudio()
datos = [];
def callback(in_data, frame_count, time_info, status):
    datos.append(in_data)
    return in_data, pyaudio.paContinue
    
os.chdir("C:\\Users\\Publico\\Desktop\\Instrumentacion\\instrumentacionycontrol\\Prueba recorder\\")
## Tomamos dia y hora actual para dar nombre al archivo wav
#mes_dia = strftime("%m%d-%H_%M_%S")
# Agregamos un contador para facilitar referir a los archivos
num_wavs = len(glob.glob(os.path.join(os.getcwd(), '*.wav')))
rec = Recorder(channels=2)
# Use a stream with a callback in non-blocking mode
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=44100,
                 input=True,
                 frames_per_buffer=1024,
                 stream_callback=callback)
stream.start_stream()
time.sleep(1)
stream.stop_stream()
pa.terminate()
# %%
with rec.open('medicion-{}.wav'.format(num_wavs+1), 'wb') as recfile2:
#    s = recfile2.start_recording()
    #time.sleep(10.0)
    CHUNK = 1024
    
    #if len(sys.argv) < 2:
    #    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    #    sys.exit(-1)
    #wf = wave.open('output.wav', 'rb')
    volume = 0.51    # range [0.0, 1.0]
    fs = 44100       # sampling rate, Hz, must be integer
    duration = 1.0 # in seconds, may be float
    f = 2000      # sine frequency, Hz, may be float
 #   samples = volume*(np.cos(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
    
    # Barriendo en frecuencia
    frecuencia_inicial = 10 ;
    frecuencia_final = 20000 ;
    salto = 1000;
    frecuencias = np.arange(frecuencia_inicial,frecuencia_final,salto)
    n_periodos = 5 # cantidad de periodos

    for freq in frecuencias:
        p = pyaudio.PyAudio()
    
        stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)
#        duration = n_periodos/freq
        duration = 0.5
        senial = volume * (np.sin(2*np.pi*np.arange(fs*duration)*freq/fs)).astype(np.float32)
        
        fin = CHUNK
        
        while fin < len(senial):
            data = senial[fin-CHUNK:fin].tobytes()
            stream.write(data)
            fin += CHUNK
        stream.stop_stream()
        stream.close()
    
        p.terminate()    
        #samples = volume*(np.cos(2*np.pi*np.arange(fs*duration))).astype(np.float32)

    
    
    recfile2.stop_recording()
    
# %% Graficar
with wave.open('nonblocking.wav','r') as spf:
    #Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.frombuffer(signal, 'Int16')
    fs = spf.getframerate()
    tiempo = np.linspace(0, len(signal)/fs, num=len(signal))
    plt.figure(1)
    plt.title('Signal Wave...')
    plt.plot(tiempo, signal)
    plt.show()
