# -*- coding: utf-8 -*-
import pyaudio
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import time
from scipy.signal import chirp


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


def cuadrada(f_sampleo=44100, frecuencia=100, num_puntos=1024, minimo=0.,
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
                     num_puntos=num_puntos)
    return (maximo-minimo)*(np.sign(señal)/2+1/2)+minimo


def callback_input(in_data, frame_count, time_info, status):
    datos.append(in_data)
    return in_data, pyaudio.paContinue


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
#%%

def time_per_freq(freq_arr, per_per_freq):
    cursor = 0
    while cursor < len(freq_arr):
        yield per_per_freq/freq_arr[cursor]
        cursor += 1


# %% Output con callback
pa = pyaudio.PyAudio()
CHUNK = 1024
tmp = senoidal(f_sampleo=44100, frecuencia=1000, num_puntos=1024*100,
               vpp=.1, offset=0.)
fs = 44100       # sampling rate, Hz, must be integer

# Use a stream with a callback in non-blocking mode
stream_out = pa.open(format=pyaudio.paFloat32,
                     channels=1,
                     rate=fs,
                     output=True,
                     frames_per_buffer=CHUNK,
                     stream_callback=create_callback(take(tmp, CHUNK)))
stream_out.start_stream()
time.sleep(10)
stream_out.stop_stream()
pa.terminate()
# %% Input con tiempo definido
pa = pyaudio.PyAudio()
CHUNK = 1024
t_medicion = 2.
fs = 44100       # sampling rate, Hz, must be integer
channels = 1
datos = np.zeros((channels, int(t_medicion*fs)))

tiempo = np.arange(0, t_medicion, 1/fs)
stream_in = pa.open(format=pyaudio.paFloat32,
                    channels=channels,
                    rate=fs,
                    input=True,
                    frames_per_buffer=CHUNK)
stream_in.start_stream()

fin = CHUNK
while fin < int(t_medicion*fs):
    new_data = stream_in.read(CHUNK)
    for nchan in range(channels):
        datos[nchan][fin-CHUNK:fin] = np.fromstring(new_data[nchan::channels],
                                                    'Float32')
    fin += CHUNK
time.sleep(1)
stream_in.stop_stream()
pa.terminate()
for nchan in range(channels):
    plt.plot(tiempo, datos[nchan])

#path = 'C:\\Users\\Publico\\Desktop\\Instrumentacion\\instrumentacionycontrol\\'
#fname = 'aa'
#if not os.path.exists('{}{}.dat'.format(path, fname)):
#    np.savetxt('{}{}.dat'.format(path, fname), np.transpose([tiempo, datos]))
#else:
#    print('El archivo ya existe!')

# %% Input-output simultaneo

fs = 96000       # sampling rate, Hz, must beinteger
CHUNK = 1024

volumen_inicial = .1
volumen_final = 1.
n_volumenes = 2
volumenes = np.geomspace(volumen_inicial, volumen_final, n_volumenes)

# Barriendo en frecuencia
frecuencia_inicial = 1000
frecuencia_final = 5000
duracion = 1 # segundos de duracion
n_frecuencias = 2
frecuencias = np.geomspace(frecuencia_inicial, frecuencia_final, n_frecuencias)

datos_serie = []
frecuencias_serie = []
volumenes_serie = []

for freq in frecuencias:
    for vol in volumenes:
        pa = pyaudio.PyAudio()
        tmp = senoidal(f_sampleo=fs, frecuencia=freq, num_puntos=CHUNK*100,
                       vpp=vol, offset=0.)
        #w = chirp(np.arange(0, t_medicion, 1/fs), f0=1, f1=25000, t1=t_medicion,
        #          method='linear')
        
        # Use a stream with a callback in non-blocking mode
        stream_out = pa.open(format=pyaudio.paFloat32,
                             channels=1,
                             rate=fs,
                             output=True,
                             frames_per_buffer=CHUNK,
                             stream_callback=create_callback(take(tmp, CHUNK)))
        stream_out.start_stream()
        
        t_medicion = 1.
        channels = 1
        datos = np.zeros((channels, int(t_medicion*fs)))
        tiempo = np.arange(0, t_medicion, 1/fs)
        stream_in = pa.open(format=pyaudio.paFloat32,
                            channels=channels,
                            rate=fs,
                            input=True,
                            frames_per_buffer=CHUNK)
        stream_in.start_stream()
        
        fin = CHUNK
        while fin < int(t_medicion*fs):
            new_data = stream_in.read(CHUNK)
            for nchan in range(channels):
                datos[nchan][fin-CHUNK:fin] = np.fromstring(new_data[nchan::channels],
                                                            'Float32')
            fin += CHUNK
        stream_in.stop_stream()
        pa.terminate()
        datos_serie.append(datos) # guarda la señal medida en cada iteracion
        frecuencias_serie.append(freq) # guarda informacion del valor de la frecuencia en cada iteracion
        volumenes_serie.append(vol) # guarda informacion del valor de la amplitud en cada iteracion
        
datos_plot = datos_serie[1] # con esto se selecciona una de las señales (de una iteración en particular) para graficarla
fig, ax = plt.subplots(2, 1)
ax[0].plot(tiempo, datos_plot[0])
n_puntos = len(datos_plot[0])
fourier = np.abs(np.fft.fft(datos_plot[0]))
fourier_freqs = np.linspace(0, fs, len(datos_plot[0]))
ax[1].plot(fourier_freqs[:n_puntos//2], fourier[:n_puntos//2])

# %% Barrido en frecuencia/caracterizacin par emisor-receptor
pa = pyaudio.PyAudio()
fs = 192000
CHUNK = 1024

volumen_inicial = .5
volumen_final = 3.
n_volumenes = 4
volumenes = np.geomspace(volumen_inicial, volumen_final, n_volumenes)

# Barriendo en frecuencia
frecuencia_inicial = 200
frecuencia_final = 3000
n_frecuencias = 10
frecuencias = np.geomspace(frecuencia_inicial, frecuencia_final, n_frecuencias)


for freq in frecuencias:
    for vol in volumenes:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=fs,
                        output=True)
        senial = senoidal(f_sampleo=fs, frecuencia=freq, num_puntos=CHUNK*100,
                          vpp=vol).astype(np.float32)
        fin = CHUNK
        while fin < int(t_medicion*fs):
            new_data = stream_in.read(CHUNK)
            datos[fin-CHUNK:fin] = np.fromstring(new_data, 'Float32')
            fin += CHUNK
        stream_in.stop_stream()
        stream_out.stop_stream()
        to_analize = datos[-num_datos//10:]
        vin = (max(tmp)-min(tmp))
        vout = (max(to_analize)-min(to_analize))
        fouin = max(np.abs(np.fft.fft(tmp)))
        fouout = max(np.abs(np.fft.fft(to_analize)))
        vout_vin[n_freq, n_vol] = vout/vin
        fouout_fouin[n_freq, n_vol] = fouout/fouin
pa.terminate()
for n_vol, _ in enumerate(volumenes):
    plt.plot(frecuencias, vout_vin[:, n_vol], 'rx')
plt.plot(frecuencias, np.mean(vout_vin, axis=1), lw=2)
