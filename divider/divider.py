""" Contains all the logic """

from enum import Enum

#          R1           R2
#     --[======]-----[======]--
#    |            |            |
#   V_in        V_out         GND

# V_out / V_in = R2 / (R1 + R2)
# resistor_ratio = R1 / R2


class RatioType(Enum):
    """ Allows distinguishing between resistor ratios and voltage ratios """
    VOLTAGE = 0
    RESISTOR = 1


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


def get_suffix(exp):
    """ Returns a human-friendly resistor suffix """
    from math import floor
    suffix = floor(exp / 3)
    ret = ''
    if suffix == -1:
        ret += 'm'
    elif suffix == 0:
        pass
    elif suffix == 1:
        ret += 'k'
    elif suffix == 2:
        ret += 'M'
    elif suffix == 3:
        ret += 'G'
    else:
        ret += '* 10^{} '.format(exp)

    return ret + 'Ohm'


def format_resistance(res, exp):
    """ Returns a human-friendly representation of a given resistance value """
    assert res > 0 and res < 10

    base = res * 10 ** (exp % 3)
    suffix = get_suffix(exp)

    return '{:3.2f} {}'.format(base, suffix)


def closest_sort_helper(item):
    """ Helper for get_closest_in_series """
    return item[2]


def get_closest_in_series(val, series):
    """ Gets the closest realizable value given a resistor series
    Returns a tuple of base and exponent
    """
    from math import floor, log10

    # Calculate exponent
    exp = floor(log10(val))

    # Calculate list of relative errors
    # Also consider exponents above and below
    errors = list()
    for exp in range(exp - 1, exp + 2):
        errors.extend(
            (res_series, exp, abs(val - res_series * 10 ** exp) / val)
            for res_series in series[1])

    # Sort by relative error
    errors.sort(key=closest_sort_helper)
    return errors[0][0], errors[0][1]


class Configuration:
    """ A Configuration consists of two resistors, an exponent and a voltage ratio """

    def find_match(self):
        """ Finds the matching second resistor for the given desired ratio """
        if hasattr(self, 'val_1'):
            # Calculate ideal value for res_2
            if self.ratio_type is RatioType.VOLTAGE:
                ideal_2 = self.val_1 * self.desired_ratio / \
                    (1 - self.desired_ratio)
            else:
                ideal_2 = self.val_1 / self.desired_ratio

            # Get closest available value for res_2
            self.res_2, self.exp_2 = get_closest_in_series(
                ideal_2, self.series)
            self.val_2 = self.res_2 * 10 ** self.exp_2
        else:
            # Calculate ideal value for res_1
            if self.ratio_type is RatioType.VOLTAGE:
                ideal_1 = self.val_2 * \
                    (1 - self.desired_ratio) / self.desired_ratio
            else:
                ideal_1 = self.val_2 * self.desired_ratio

            # Calculate closest available value for res_1
            self.res_1, self.exp_1 = get_closest_in_series(
                ideal_1, self.series)
            self.val_1 = self.res_1 * 10 ** self.exp_1

    def __init__(self, desired_ratio, ratio_type, series,
                 res_1=None, exp_1=None, res_2=None, exp_2=None):
        """ Given one resistor value and a desired ratio, calculates the other
        as well as the resulting ratio and errors
        """

        assert (res_1 is None and exp_1 is None and res_2 is not None and exp_2 is not None) or (
            res_1 is not None and exp_1 is not None and res_2 is None and exp_2 is None)

        self.desired_ratio = desired_ratio
        self.ratio_type = ratio_type
        self.series = series

        if res_1 is not None:
            self.res_1 = res_1
            self.exp_1 = exp_1
            self.val_1 = res_1 * 10 ** self.exp_1
        else:
            self.res_2 = res_2
            self.exp_2 = exp_2
            self.val_2 = res_2 * 10 ** self.exp_2

        self.find_match()

        if self.ratio_type is RatioType.VOLTAGE:
            self.ratio = self.val_2 / (self.val_1 + self.val_2)
        else:
            self.ratio = self.val_1 / self.val_2

        self.error_abs = self.desired_ratio - self.ratio
        self.error_rel = self.error_abs / self.desired_ratio

    def __str__(self):
        return 'R1 = {}, R2 = {}, e_rel = {:3.2f}%, ratio = {:6.5f}\n'.format(
            format_resistance(self.res_1, self.exp_1),
            format_resistance(self.res_2, self.exp_2),
            self.error_rel * 100,
            self.ratio,)

    def __eq__(self, other):
        return self.val_1 == other.val_1 and self.val_2 == other.val_2

    def __hash__(self):
        return hash((self.val_1, self.val_2))


def sort_relative(item):
    """ Helper to sort by relative error """
    return abs(item.error_rel)


class Result:
    """ Represents the result of a Run """

    def __init__(self, series, desired_ratio, ratio_type, configurations):
        self.series = series
        self.desired_ratio = desired_ratio
        self.ratio_type = ratio_type
        self.configurations = configurations

    def __str__(self):
        format_string = ''
        if self.ratio_type is RatioType.VOLTAGE:
            format_string = '{} best results for ratio V_out / V_in = {:6.5f} using series {}:\n'
        else:
            format_string = '{} best results for ratio R1 / R2 = {:6.5f} using series {}:\n'

        string = format_string.format(
            len(self.configurations),
            self.desired_ratio,
            self.series)
        for configuration in self.configurations:
            string += str(configuration)
        return string


class Run:
    """ A Run iterates through a given series and returns a Result """

    configurations = set()

    def create_configurations(self):
        """ Creates a list of all possible configurations for the given series """
        # Iterate over R1 and R2
        for res_series in self.series[1]:
            self.configurations.add(Configuration(
                self.desired_ratio, self.ratio_type, self.series, res_1=res_series, exp_1=0))
            self.configurations.add(Configuration(
                self.desired_ratio, self.ratio_type, self.series, res_2=res_series, exp_2=0))

    def __init__(self, series, desired_ratio, ratio_type=RatioType.VOLTAGE):
        self.series = series
        self.desired_ratio = desired_ratio
        self.ratio_type = ratio_type

        self.create_configurations()

    def get_result(self, num_results):
        """ Gets the <num_results> closest Configurations """
        configurations_list = list(self.configurations)
        configurations_list.sort(key=sort_relative)
        return Result(self.series[0], self.desired_ratio,
                      self.ratio_type, configurations_list[:num_results])
