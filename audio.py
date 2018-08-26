# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

import pyaudio
import numpy as np
import wave
import os
#import matplotlib.pyplot as plt
#import struct

os.chdir('C:/Users/Publico/Desktop/Instrumentacion')
# %%
p = pyaudio.PyAudio()

volume = 1     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 1.0   # in seconds, may be float
f = 440.0        # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32).tobytes()

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,channels=1,rate=fs,output=True)

# play. May repeat with different volume values (if done interactively) 
stream.write(samples)

stream.stop_stream()
stream.close()

p.terminate()
# %%
CHUNK = 1024

#if len(sys.argv) < 2:
#    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
#    sys.exit(-1)
#wf = wave.open('output.wav', 'rb')
volume = 0.1     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 2.0   # in seconds, may be float
f = 440.0        # sine frequency, Hz, may be float
samples = volume*(np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

fin = CHUNK

while fin < len(samples):
    data = samples[fin-CHUNK:fin].tobytes()
    stream.write(data)
    fin += CHUNK

stream.stop_stream()
stream.close()

p.terminate()

# %%
   """PyAudio example: Record a few seconds of audio and save to a WAVE file."""


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
