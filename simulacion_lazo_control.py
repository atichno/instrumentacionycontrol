import numpy as np
import matplotlib.pyplot as plt

## seteo señales de alimentacion de los LEDs
amplitud_1 = 1
frecuencia_1 = 3
fase_1 = np.pi * np.random.rand()
n_puntos = 10000
tmax = 6
t = np.linspace(0,tmax,n_puntos)
alimentacion_1 = amplitud_1 * np.sin(2 * np.pi * frecuencia_1 * t + fase_1)

amplitud_2 = 0.5
frecuencia_2 = 3
fase_2 = np.pi * np.random.rand()
fase_2 = fase_1
alimentacion_2 = amplitud_2 * np.sin(2 * np.pi * frecuencia_2 * t + fase_2)

## busco la señal detectada de luz en el fotodiodo (los LEDs se prenden solamente en la mitad de los ciclos)
senial_1 = keep(alimentacion_1, value = 0, kp = 'larger') # value es un valor crítico a partir del cual el LED deja de emitir luz
senial_2 = keep(alimentacion_2, value = 0, kp = 'larger')
senial_total = np.array(senial_1) + np.array(senial_2) # la señal detectada es la suma de la que se detectaría para cada LED por separado (fuentes no coherentes)

#plt.plot(t, senial_1)
#plt.plot(t, senial_2)
#plt.plot(t, senial_total)

value = 0 # valor critico

t_value = [] # va a contener los tiempos en los que ambos LEDs estan apagados
ind = [] # va a contener los indices del vector tiempo para los cuales ambos LEDs estan apagados

for i, v in enumerate(senial_total):
    if v == value:
        t_value.append(t[i])
        ind.append(i)

ind_fall = [] # va a contener los indices del vector tiempo para los cuales ambos LEDs pasan a estar apagados
ind_rise = [] # va a contener los indices del vector tiempo para el cual al menos un LED pasa a estar prendido (donde antes tenía ambos apagados)
ind_all = [] # va a contener los indices del vector tiempo para el cual se prenden o apagan los LEDs (pasaje de al menos uno prendido a ambos apagados, y de ambos apagados a al menos uno prendido)

for i in ind:
    if i + 1 not in ind:
        ind_rise.append(i)
        ind_all.append(i)
    if i - 1 not in ind:
        ind_fall.append(i)
        ind_all.append(i)

#plt.scatter(t_value, t_value, s = 1)
plt.scatter(ind_rise, ind_rise)
plt.scatter(ind_fall, ind_fall)
