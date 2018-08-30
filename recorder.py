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
    samples *= n_escalones  # solo sirve si linspace va de 0 a 1
    samples = np.floor(samples)
    samples = samples / n_escalones
    samples = desde+(hasta-desde)*samples
    return samples


def senoidal(f_sampleo=44100, frecuencia=10, duracion=1., vpp=1.,
             dtype=np.float32):
    """
    Genera una señal senoidal de frecuencia y duracion definida
    """
    times = np.arange(f_sampleo*duracion)
    return 2*vpp*(np.sin(2*np.pi*times*frecuencia/f_sampleo)).astype(dtype)


def cuadrada(f_sampleo=44100, frecuencia=10, duracion=1., minimo=0.,
             maximo=1.):
    señal = senoidal(f_sampleo=f_sampleo, frecuencia=frecuencia,
                     duracion=duracion)
    return (np.sign(señal)+minimo+1)/(2*(maximo-minimo))


def callback_input(in_data, frame_count, time_info, status):
    datos.append(in_data)
    return in_data, pyaudio.paContinue


# %%
code_path = '/home/juan/Documentos/Instrumentacion/instrumentacion'
files_path = '/home/juan/Documentos/Instrumentacion/files'

if ~os.path.isdir(code_path):
    os.makedirs(files_path)

# %%
struct.pack('f', 3.141592654)
struct.unpack('f', b'\xdb\x0fI@')
struct.pack('4f', 1.0, 2.0, 3.0, 4.0)

# %%

pa = pyaudio.PyAudio()
datos = []
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
                 stream_callback=callback_input)
stream.start_stream()
time.sleep(1)
stream.stop_stream()
pa.terminate()

# %%
CHUNK = 1024

volume = 1.    # range [0.0, 1.0]
# Cambio sampling rate al valor maximo
# En ubuntu se puede ver con cat /proc/asound/card0/codec#3
fs = 192000       # sampling rate, Hz, must be integer

# Barriendo en frecuencia
frecuencia_inicial = 10
frecuencia_final = 20000
periodos_por_frec = 10
n_frecuencias = 10
frecuencias = np.geomspace(frecuencia_inicial, frecuencia_final, n_frecuencias)
n_periodos = 10     # cantidad de periodos
for freq in frecuencias:
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)
    duration = periodos_por_frec/freq
    senial = senoidal(f_sampleo=fs, frecuencia=freq, duracion=duration,
                      vpp=volume, dtype=np.float32)
    fin = CHUNK
    while fin < len(senial):
        data = senial[fin-CHUNK:fin].tobytes()
        stream.write(data)
        fin += CHUNK
    stream.stop_stream()
    stream.close()
    p.terminate()
