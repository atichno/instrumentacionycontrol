# -*- coding: utf-8 -*-
import struct
import pyaudio
import wave
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import time


def escalon(n_escalones, long_escalon, desde, hasta):
    """
    Genera una señal escalonada entre dos valores
    """
    samples = np.linspace(0, 1, n_escalones * long_escalon)
    samples = samples * n_escalones # solo sirve si linspace va de 0 a 1
    samples = np.floor(samples)
    samples = samples / n_escalones
    samples = desde + (hasta - desde) * samples    
    return samples


def senoidal(f_sampleo=44100, frecuencia=10, duracion=1., vpp=1.):
    """
    Genera una señal senoidal de frecuencia y duracion definida
    """
    return 2*vpp*(np.sin(2*np.pi*np.arange(f_sampleo*duracion)*frecuencia/f_sampleo))


def cuadrada(f_sampleo=44100, frecuencia=10, duracion=1., minimo=0., maximo=1.):
    señal = senoidal(f_sampleo=f_sampleo, frecuencia=frecuencia,
                     duracion=duracion)
    return (np.sign(señal)+minimo+1)/(2*(maximo-minimo))

# %%
code_path = '/home/juan/Documentos/Instrumentacion/instrumentacion'
files_path = '/home/juan/Documentos/Instrumentacion'

os.path.isfile(files_path)

struct.pack('f', 3.141592654)
struct.unpack('f', b'\xdb\x0fI@')
struct.pack('4f', 1.0, 2.0, 3.0, 4.0)

# %%

pa = pyaudio.PyAudio()
datos = [];
def callback(in_data, frame_count, time_info, status):
    datos.append(in_data)
    return in_data, pyaudio.paContinue
    
## Tomamos dia y hora actual para dar nombre al archivo wav
#mes_dia = strftime("%m%d-%H_%M_%S")
# Agregamos un contador para facilitar referir a los archivos
num_wavs = len(glob.glob(os.path.join(os.getcwd(), '*.wav')))
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
CHUNK = 1024

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
