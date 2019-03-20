import modules.mymath as my_math
import math

"""
Класс, отвечаюший за анализ текущей ситуаций и хранящий данные о текущей ситуации.
В полях хранит как выборку котировок, так и коэффициенты линий коридора поддержки, включая warning-зоны.
Использует математический модуль собственной разработки.
"""

type_of_trend_type = {-1: 'downward', 0: 'NaN', 1: 'rising'}

class Analysis:
    course_values = []
    trend_coefficients = []
    support_top_coefficients = []
    support_bottom_coefficients = []
    warning_zone_bottom_coefficients = []
    warning_zone_top_coefficients = []
    warning_zone_size = 0
    number_of_extremes = 0
    pitch_of_trend = 0
    type_of_trend = type_of_trend_type[0]
    trend_type_was_changed = False
    trend_was_built = False

    def __init__(self, course_values, warning_zone_size, number_of_extremes):
        self.course_values = course_values
        self.warning_zone_size = warning_zone_size
        self.number_of_extremes = number_of_extremes

    '''Вычисляет коэффициенты линии тренда степени degree по последним точкам из выборки в количестве sample'''

    def calculate_trend_line(self, degree, sample):
        self.trend_coefficients = list(my_math.mnk(count=degree, volume=sample, vector=self.course_values))

        # определяем тип тренда
        self.pitch_of_trend = math.atan(self.trend_coefficients[0])
        if self.pitch_of_trend >= 0:
            type_of_trend_new = type_of_trend_type[1]  # rising
        else:
            type_of_trend_new = type_of_trend_type[-1]  # downward

        # если тренд перестроен не первый раз
        if self.trend_was_built:
            if self.type_of_trend != type_of_trend_new:
                self.trend_type_was_changed = True
            else:
                self.trend_type_was_changed = False
        else:
            self.trend_was_built = True
        self.type_of_trend = type_of_trend_new

    '''Вычисляет коэффициенты линий поддержки и линий warning-зон по последним точкам из выборки в количестве sample'''

    def calculate_support_corridor(self, sample):
        sample_vector = self.course_values[len(self.course_values) - sample:len(self.course_values)]

        # вычисляем коэффициенты верхнего уровня коридора поддержки
        delta_top = my_math.delta_mean_top(sample_vector, self.trend_coefficients, self.number_of_extremes)
        self.support_top_coefficients = list(self.trend_coefficients)
        self.support_top_coefficients[len(self.support_top_coefficients) - 1] += delta_top
        # вычисляем коэффициенты верхней границы warning-зоны
        self.warning_zone_top_coefficients = list(self.support_top_coefficients)
        self.warning_zone_top_coefficients[len(self.support_top_coefficients) - 1] += (delta_top * self.warning_zone_size)

        # вычисляем коэффициенты нижнего уровня коридора поддержки
        delta_bottom = my_math.delta_mean_bottom(sample_vector, self.trend_coefficients, self.number_of_extremes)
        self.support_bottom_coefficients = list(self.trend_coefficients)
        self.support_bottom_coefficients[len(self.support_bottom_coefficients) - 1] += delta_bottom

        # вычисляем коэффициенты нижней границы warning-зоны
        self.warning_zone_bottom_coefficients = list(self.support_bottom_coefficients)
        self.warning_zone_bottom_coefficients[len(self.support_bottom_coefficients) - 1] += (delta_bottom * self.warning_zone_size)

    '''Изменяет высоту warning-зоны'''

    def change_warning_zone(self, new_warning_zone_height):
        self.warning_zone_size = new_warning_zone_height

    def get_trend_coefficients(self):
        return self.trend_coefficients

    def get_support_top_coefficients(self):
        return self.support_top_coefficients

    def get_warning_top_coefficients(self):
        return self.warning_zone_top_coefficients

    def get_support_bot_coefficients(self):
        return self.support_bottom_coefficients

    def get_warning_bot_coefficients(self):
        return self.warning_zone_bottom_coefficients

    def get_trend_was_built(self):
        return self.trend_was_built

    def get_trend_was_changed(self):
        return self.trend_type_was_changed

    def get_type_of_trend(self):
        return self.type_of_trend

    """Возвращает статус заданной точки по её значению
    point[0] - координата x
    point[1] - координата y
    """

    def is_point_in_corridor_status(self, point):
        status = 0
        if self.trend_was_built:
            if my_math.func(point[0], self.support_bottom_coefficients) <= point[1] <= my_math.func(point[0], self.support_top_coefficients):
                status = 1
            elif my_math.func(point[0], self.warning_zone_bottom_coefficients) <= point[1] <= my_math.func(point[0], self.warning_zone_top_coefficients):
                status = 2
            elif point[1] <= my_math.func(point[0], self.warning_zone_bottom_coefficients):
                status = 3
        else:
            status = 4
        return status
