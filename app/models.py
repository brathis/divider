""" Contains all the logic """

from enum import Enum

#          R1           R2
#     --[======]-----[======]--
#    |            |            |
#   V_in        V_out         GND

# V_out / V_in = R2 / (R1 + R2)


SERIES = {
    'E6': ('E6', (1.0, 1.5, 2.2, 3.3, 4.7, 6.8)),
    'E12': ('E12', (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)),
    'E24': ('E24', (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
                    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1)),
    'E48': ('E48', (1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54,
                    1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49,
                    2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
                    4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49,
                    6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53)),
}


class Configuration:
    """ A Configuration consists of two resistors and a voltage ratio """
    def __init__(self, res_1, res_2, desired_ratio):
        self.res_1 = res_1
        self.res_2 = res_2
        self.desired_ratio = desired_ratio

        self.ratio = res_2 / (res_1 + res_2)
        self.error_abs = self.desired_ratio - self.ratio
        self.error_rel = self.error_abs / self.desired_ratio

    def __str__(self):
        return 'R1 = {}, R2 = {}, e_rel = {:3.2f}%, ratio = {:6.5f}\n'.format(
            self.res_1,
            self.res_2,
            self.error_rel * 100,
            self.ratio,)


def sort_absolute(item):
    """ Helper to sort by absolute error """
    return abs(item.error_abs)


def sort_relative(item):
    """ Helper to sort by relative error """
    return abs(item.error_rel)


class Result:
    """ Represents the result of a Run """

    def __init__(self, series, desired_ratio, configurations):
        self.series = series
        self.desired_ratio = desired_ratio
        self.configurations = configurations

    def __str__(self):
        string = '{} best results for ratio V_out / V_in = {:6.5f} using series {}:\n'.format(
            len(self.configurations),
            self.desired_ratio,
            self.series)
        for configuration in self.configurations:
            string += str(configuration)
        return string


class Run:
    """ A Run iterates through a given series and returns a Result """

    class SortType(Enum):
        """ Enum to express, after which criterion to sort """
        ABSOLUTE = 0
        RELATIVE = 1

    configurations = []

    def create_configurations(self):
        """ Creates a list of all possible configurations for the given series """
        for value_1 in self.series[1]:
            for value_2 in self.series[1]:
                self.configurations.append(Configuration(value_1, value_2, self.desired_ratio))

    def __init__(self, series, desired_ratio):
        self.series = series
        self.desired_ratio = desired_ratio

        self.create_configurations()

    def get_result(self, num_results, sort_type=SortType.RELATIVE):
        """ Gets the <num_results> closest Configurations """
        if sort_type == self.SortType.ABSOLUTE:
            self.configurations.sort(key=sort_absolute)
        else:
            self.configurations.sort(key=sort_relative)

        return Result(self.series[0], self.desired_ratio, self.configurations[:num_results])
