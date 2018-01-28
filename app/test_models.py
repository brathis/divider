"""Contains tests for models module"""
def test_get_suffix():
    """Test that we get the correct suffix for a given exponent"""
    from .models import get_suffix

    # less than milliohms
    assert get_suffix(-20) == '* 10^-20 Ohm'
    assert get_suffix(-4) == '* 10^-4 Ohm'

    # milliohms
    assert get_suffix(-3) == 'mOhm'
    assert get_suffix(-2) == 'mOhm'
    assert get_suffix(-1) == 'mOhm'

    # ohms
    assert get_suffix(0) == 'Ohm'
    assert get_suffix(1) == 'Ohm'
    assert get_suffix(2) == 'Ohm'

    # kiloohms
    assert get_suffix(3) == 'kOhm'
    assert get_suffix(4) == 'kOhm'
    assert get_suffix(5) == 'kOhm'

    # megaohms
    assert get_suffix(6) == 'MOhm'
    assert get_suffix(7) == 'MOhm'
    assert get_suffix(8) == 'MOhm'

    # gigaohms
    assert get_suffix(9) == 'GOhm'
    assert get_suffix(10) == 'GOhm'
    assert get_suffix(11) == 'GOhm'

    # larger than gigaohms
    assert get_suffix(12) == '* 10^12 Ohm'
    assert get_suffix(20) == '* 10^20 Ohm'

def test_get_closest_in_series():
    """Test that we get the actual closest resistors in the series"""
    from .models import get_closest_in_series, SERIES

    assert get_closest_in_series(6.7e-3, SERIES.get('E24')) == (6.8, -3)
    assert get_closest_in_series(4.4e-2, SERIES.get('E24')) == (4.3, -2)
    assert get_closest_in_series(1.2e-1, SERIES.get('E6')) == (1.0, -1)
    assert get_closest_in_series(1.2, SERIES.get('E6')) == (1.0, 0)
    assert get_closest_in_series(1.3e1, SERIES.get('E6')) == (1.5, 1)
    assert get_closest_in_series(1.6e2, SERIES.get('E12')) == (1.5, 2)
    assert get_closest_in_series(1.7e3, SERIES.get('E12')) == (1.8, 3)
    assert get_closest_in_series(1.7e4, SERIES.get('E12')) == (1.8, 4)
    assert get_closest_in_series(0.923, SERIES.get('E12')) == (1.0, 0)

def test_configs_resistor_ratio():
    """Test the essential mechanism of finding the best match
    for a given resistor and resistor ratio
    """
    from .models import Configuration, RatioType, SERIES

    # 1.2 = 1.2 / 1.0
    conf_1 = Configuration(1.2, RatioType.RESISTOR, SERIES.get('E12'), res_2=1.0, exp_2=0)
    assert (conf_1.res_1, conf_1.exp_1) == (1.2, 0)
    conf_2 = Configuration(1.2, RatioType.RESISTOR, SERIES.get('E12'), res_1=1.2, exp_1=0)
    assert (conf_2.res_2, conf_2.exp_2) == (1.0, 0)

    # 1.3 = 1.3 / 1.0 ~ 1.2 / 1.0
    conf_3 = Configuration(1.3, RatioType.RESISTOR, SERIES.get('E12'), res_2=1.0, exp_2=0)
    assert (conf_3.res_1, conf_3.exp_1) == (1.2, 0)
    conf_4 = Configuration(1.3, RatioType.RESISTOR, SERIES.get('E12'), res_1=1.2, exp_1=0)
    assert (conf_4.res_2, conf_4.exp_2) == (1.0, 0)

    # 1.22 = 1.0 / 8.2e-1
    conf_5 = Configuration(1.22, RatioType.RESISTOR, SERIES.get('E12'), res_1=1.0, exp_1=0)
    assert (conf_5.res_2, conf_5.exp_2) == (8.2, -1)
    conf_6 = Configuration(1.22, RatioType.RESISTOR, SERIES.get('E12'), res_2=8.2, exp_2=-1)
    assert (conf_6.res_1, conf_6.exp_1) == (1.0, 0)
