import matplotlib.pyplot as plt
import modules.mymath as my_math

"""
Модуль, отвечающий за визуализацию текущей ситуации в виде графика при помощи matplotlib.pyplot.
Также использует 
"""

COLOR_OF_POINT = {0: 'red', 1: 'green', 2: 'orange', 3: 'blue', 4: 'black'}


class Plot:
    def __init__(self, vector):
        # создаём ссылку на вектор выборки
        self.vector = vector
        # визуальное оформление графика
        plt.rc('grid', linestyle="--", color='black')
        plt.grid()
        plt.title('ESU bot')
        plt.xlabel('x')
        plt.ylabel('y')

    """
    Рисует линию на графике по выборке, используя коэффициенты функции.
    Используется для отрисовки линий коридора поддержки.
    """

    @staticmethod
    def _draw_line(coefficients, vector_of_volume):
        x_minimum = min(vector_of_volume)[0] + len(vector_of_volume)
        x_maximum = max(vector_of_volume)[0] + len(vector_of_volume)
        dx = (x_maximum - x_minimum) / 100
        x_list = []

        x_iterator = x_minimum
        while x_iterator <= x_maximum:
            x_list.append(x_iterator)
            x_iterator += dx

        y_list = [my_math.func(x, coefficients) for x in x_list]
        plt.plot(x_list, y_list, color='green')

    """Отрисовывает коридор поддержки, используя закрытый метод"""

    def draw_corridor(self, trend_coefficients, support_top_coefficients,
                      support_bot_coefficients, warning_top_coefficients, get_warning_bot_coefficients, course_volume):
        self._draw_line(trend_coefficients, course_volume)
        self._draw_line(support_top_coefficients, course_volume)
        self._draw_line(support_bot_coefficients, course_volume)
        self._draw_line(warning_top_coefficients, course_volume)
        self._draw_line(get_warning_bot_coefficients, course_volume)

    """Отрисовывает линии между точками на имеющейся выборке"""

    def _draw_lines_between_points(self):
        if len(self.vector) > 1:
            plt.plot([self.vector[k][0] for k in range(len(self.vector)-2, len(self.vector))], [self.vector[k][1] for k in range(len(self.vector)-2, len(self.vector))], color='blue')

    """Отрисовывает точку, в соответствии с цветом. (0 - красный, 1 - зелёный, 2 - жёлтный, 3 - синий)"""

    def draw_point(self, point_coord, color):
        # print('Рисуемая точка:', point_coord)
        plt.scatter(point_coord[0], point_coord[1], color=COLOR_OF_POINT[color])
        self._draw_lines_between_points()

    @staticmethod
    def pause(time):
        plt.pause(time)
