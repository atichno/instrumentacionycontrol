# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 17:15:33 2018

@author: Publico
"""

# -*- coding: utf-8 -*-
import pyaudio
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import time
from scipy.signal import chirp
import pandas as pd

def senoidal(f_sampleo=44100, frecuencia=100, num_puntos=1024, vpp=1.,
             offset=0.):
    """
    Genera una señal senoidal de frecuencia y numero de puntos definida
    
    Parameters
    ----------
    f_sampleo(float) = frecuencia de sampleo de la señal
    frecuencia(float) = frecuencia de la señal
    duracion(float) = duracion de la señal
    vpp(float) = valor pico a pico
    offset(float) = valor dc de la señal
    dtype = data type de la señal
    Returns
    -------
    Devuelve array
    """
    times = np.arange(num_puntos)
    return (vpp/2*(np.sin(2*np.pi*times*frecuencia/f_sampleo))
            + offset).astype(np.float32)


def take(arr, partlen):
    larr = len(arr)
    while True:
        cursor = 0
        while cursor < larr-partlen:
            tmp = arr[cursor:cursor+partlen]
            yield tmp
            cursor = min(cursor+partlen, larr+1)


def create_callback(gen):
    def callback_output(out_data, frame_count, time_info, status):
        out_data = next(gen)
        return out_data, pyaudio.paContinue
    return callback_output


def time_per_freq(freq_arr, per_per_freq):
    cursor = 0
    while cursor < len(freq_arr):
        yield per_per_freq/freq_arr[cursor]
        cursor += 1


# %% Barrido en frecuencia/caracterizacion par emisor-receptor
fs = 192000
CHUNK = 1024

#volumen_inicial = .1
#volumen_final = 3.
#volumenes = np.linspace(volumen_inicial, volumen_final, n_volumenes)
freq = 1000
vol = 2

df = pd.DataFrame(columns=['Tiempo (s)', 'Voltaje total (num)', 
                           'Voltaje caida sobre R 0Ohm (num)'])
t_medicion = 2
pa = pyaudio.PyAudio()

tmp = senoidal(f_sampleo=fs, frecuencia=freq, num_puntos=CHUNK*100,
               vpp=vol, offset=0.)
stream_out = pa.open(format=pyaudio.paFloat32,
                     channels=1,
                     rate=fs,
                     output=True,
                     frames_per_buffer=CHUNK,
                     stream_callback=create_callback(take(tmp, CHUNK)))
stream_out.start_stream()
num_datos = int(t_medicion*fs)
datos_canal1 = np.zeros(num_datos)
datos_canal2 = np.zeros(num_datos)
tiempo = np.arange(0, t_medicion, 1/fs)
stream_in = pa.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=fs,
                    input=True,
                    frames_per_buffer=CHUNK)
stream_in.start_stream()
fin = CHUNK
while fin < int(t_medicion*fs):
    new_data = np.fromstring(stream_in.read(CHUNK), 'Float32')
    datos_canal1[fin-CHUNK:fin] = new_data[::2]
    datos_canal2[fin-CHUNK:fin] = new_data[1::2]
    fin += CHUNK
stream_in.stop_stream()
stream_out.stop_stream()
pa.terminate()
resistencia = 1000

v_total = datos_canal1[-num_datos//10:]
v_resistencia = datos_canal2[-num_datos//10:]

corriente = v_resistencia/resistencia
v_diodo = v_total - v_resistencia
tiempo = np.linspace(0, t_medicion, len(v_diodo))

fig, ax = plt.subplots(3, sharex=True)
ax[0].plot(tiempo, v_total, label='V total')
ax[1].plot(tiempo, v_diodo, label='Voltaje diodo')
ax[2].plot(tiempo, corriente, 'r', label='Corriente')

fig = plt.figure()
plt.plot(v_diodo, corriente, label='Curva I-V')

df['Tiempo (s)'] = tiempo
df['Corriente (num)'] = corriente
df['Voltaje diodo (num))'] = v_diodo
df.to_csv('IV_diodo_n.dat')
