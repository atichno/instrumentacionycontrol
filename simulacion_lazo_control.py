import numpy as np
import matplotlib.pyplot as plt

amplitud_1 = 1
frecuencia_1 = 3
fase_1 = np.pi * np.random.rand()
n_puntos = 1000
tmax = 2
t = np.linspace(0,tmax,n_puntos)
alimentacion_1 = amplitud_1 * np.sin(2 * np.pi * frecuencia_1 * t + fase_1)

amplitud_2 = 0.5
frecuencia_2 = 2.9
fase_2 = np.pi * np.random.rand()
alimentacion_2 = amplitud_2 * np.sin(2 * np.pi * frecuencia_2 * t + fase_2)

senial_1 = keep(alimentacion_1, value = 0, kp = 'larger')
senial_2 = keep(alimentacion_2, value = 0, kp = 'larger')
senial_total = np.array(senial_1) + np.array(senial_2)

plt.plot(t, senial_1)
plt.plot(t, senial_2)
plt.plot(t, senial_total)
