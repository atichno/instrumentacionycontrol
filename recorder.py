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
    n_escalones(int) = numero de valores discretos que toma la señal
    long_escalon(int) = numero de samples por escalon
    desde(float) = valor inicial de la señal
    hasta(float) = valor final de la señal
    Devuelve array
    """
    samples = np.linspace(0, 1, n_escalones * long_escalon)
    samples *= n_escalones  # solo sirve si linspace va de 0 a 1
    samples = np.floor(samples)
    samples = samples / n_escalones
    samples = desde+(hasta-desde)*samples
    return samples


def senoidal(f_sampleo=44100, frecuencia=10, duracion=1., vpp=1., offset=0.):
    """
    Genera una señal senoidal de frecuencia y duracion definida
    f_sampleo(float) = frecuencia de sampleo de la señal
    frecuencia(float) = frecuencia de la señal
    duracion(float) = duracion de la señal
    vpp(float) = valor pico a pico
    offset(float) = valor dc de la señal
    dtype = data type de la señal
    Devuelve array
    """
    times = np.arange(f_sampleo*duracion)
    return (vpp/2*(np.sin(2*np.pi*times*frecuencia/f_sampleo)) + offset)


def cuadrada(f_sampleo=44100, frecuencia=10, duracion=1., minimo=0.,
             maximo=1.):
    """
    Genera una señal cuadrada de frecuencia y duracion definida, con valores
    maximos y minimos definidos
    f_sampleo(float) = frecuencia de sampleo de la señal
    frecuencia(float) = frecuencia de la señal
    duracion(float) = duracion de la señal
    minimo = valor minimo de la señal
    maximo = valor maximos de la señal
    Devuelve array
    """
    señal = senoidal(f_sampleo=f_sampleo, frecuencia=frecuencia,
                     duracion=duracion)
    return (maximo-minimo)*(np.sign(señal)/2+1/2)+minimo


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

# Cambio sampling rate al valor maximo
# En ubuntu se puede ver con cat /proc/asound/card0/codec#3
fs = 44100       # sampling rate, Hz, must be integer

# Barriendo en amplitud (volumen)
volumen_inicial = .1
volumen_final = 1.
n_volumenes = 4
volumenes = np.geomspace(volumen_inicial, volumen_final, n_volumenes)

# Barriendo en frecuencia
frecuencia_inicial = 200
frecuencia_final = 300
duracion = 1 # segundos de duracion
n_frecuencias = 3
frecuencias = np.geomspace(frecuencia_inicial, frecuencia_final, n_frecuencias)

for freq in frecuencias:
    for vol in volumenes:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)
        senial = senoidal(f_sampleo=fs, frecuencia=freq, duracion=duracion,
                          vpp=vol).astype(np.float32)
        fin = CHUNK
        while fin < len(senial):
            data = senial[fin-CHUNK:fin].tobytes()
            stream.write(data)
            fin += CHUNK
        stream.stop_stream()
        stream.close()
        p.terminate()