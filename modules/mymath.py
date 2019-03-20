from sympy import *
import numpy as np
import statistics


def zeidels_method(a, b, e):
    n = len(a)
    x = [.0 for i in range(n)]

    converge = False
    while not converge:
        x_new = np.copy(x)
        for i in range(n):
            # сумма произведений k+1, те что справа
            s1 = sum(a[i][j] * x_new[j] for j in range(0, i))
            # сумма произведение k, те что слева
            s2 = sum(a[i][j] * x[j] for j in range(i + 1, n))
            x_new[i] = - (s1 + s2 - b[i]) / a[i][i]
        converge = np.sqrt(sum((x_new[i] - x[i]) ** 2 for i in range(n))) <= e
        x = x_new
    return x


def read_file_txt(file):
    a = []
    for reading_line in file:
        i = 0
        h = 0
        reading_line = reading_line.strip('\n')
        n = len(reading_line)
        b = reading_line[i]
        column = []
        while i < n:
            if b != " ":
                s = reading_line[h:i + 1]
            else:
                column.append(float(s))
                s = ""
                h = i + 1
            i += 1
            if i < n: b = reading_line[i]
        column.append(float(s))
        a.append(column)
    return a


"""Метод наименьших квадратов, на выходе - коэффициенты полинома, аппроксимирующего выборку точек vector"""


def mnk(count, volume, vector):
    ai = []

    vector = vector[len(vector) - volume:len(vector)]
    for i in range(0, count + 1):
        ai.append(symbols(chr(i + 97)))

    S = 0
    for i in range(0, len(vector)):
        p = 0
        for j in range(0, len(ai)):
            p += ai[j] * (vector[i][0] ** (count - j))
        S += (p - vector[i][1]) ** 2

    dai = [0 for k in range(len(ai))]
    for i in range(0, len(ai)):
        dai[i] = diff(expand(S), ai[i])

    A = [0 for l in range(len(ai))]
    for i in range(0, len(ai)):
        A[i] = [0 for n in range(len(ai))]

    B = [0 for n in range(len(ai))]
    for i in range(0, len(ai)):
        B[i] = dai[i]
        for j in range(0, len(ai)):
            A[i][j] = dai[i].coeff(ai[j])
            B[i] = B[i].coeff(ai[j], 0)
        B[i] = -B[i]

    z = zeidels_method(A, B, 0.0001)
    return z


"""Вычисляет значения функции f(x) по коэффициентам coefficients"""


def func(x, coefficients):
    c = len(coefficients)
    fx = 0
    for i in range(0, c):
        fx += coefficients[i] * (x ** (c - i - 1))
    return fx


"""среднее смещение экстремумов выборки, находящейся выше тренда"""


def delta_mean_top(vector_volume, z, extremum_count):
    # vector_volume - точки, отобранные справа в количестве volume
    # z - коэффициенты полинома(линии) тренда
    # extremum_count - количество точек экстремума в выборке для усреднения при построении линий коридора

    delta_top = []
    for i in range(0, len(vector_volume)):
        d = vector_volume[i][1] - func(vector_volume[i][0], z)
        if d > 0:
            delta_top.append(d)
    delta_mean = statistics.mean(sorted(delta_top, reverse=True)[0:extremum_count])
    return delta_mean


"""среднее смещение экстремумов выборки, находящейся ниже тренда"""


def delta_mean_bottom(vector_volume, z, extremum_count):
    # vector_volume - точки, отобранные справа в количестве volume
    # z - коэффициенты полинома(линии) тренда
    # extremum_count - количество точек экстремума в выборке для усреднения при построении линий коридора
    delta_bot = []
    for i in range(0, len(vector_volume)):
        d = vector_volume[i][1] - func(vector_volume[i][0], z)
        if d < 0:
            delta_bot.append(d)
    delta_mean = statistics.mean(sorted(delta_bot)[0:extremum_count])
    return delta_mean
