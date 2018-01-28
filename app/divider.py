""" Handles user interaction """
import argparse
from .models import Run, SERIES, RatioType

SCHEMATIC = """
        R1           R2
    --[======]-----[======]--
    |            |            |
V_in        V_out         GND
"""

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--v_in', type=float)
PARSER.add_argument('--v_out', type=float)
PARSER.add_argument('--res-ratio', type=float)
PARSER.add_argument('--series', type=str)
PARSER.add_argument('--num-results', type=int)
ARGS = PARSER.parse_args()

RUN = None

# Parse series
SELECTED_SERIES = SERIES.get('E12')
if ARGS.series:
    SELECTED_SERIES = SERIES.get(ARGS.series)
    if SELECTED_SERIES is None:
        print('Error: Series \'{}\' doesn\'t exist'.format(ARGS.series))
        exit(1)

# Parse number of results
NUM_RESULTS = 1
if ARGS.num_results:
    NUM_RESULTS = ARGS.num_results

# Either a voltage ratio or a resistor ratio must be given
if ARGS.v_in and ARGS.v_out:
    VOLTAGE_RATIO = ARGS.v_out / ARGS.v_in

    # Sanity check voltage ratio
    if VOLTAGE_RATIO > 1:
        print('Error: v_out can\'t be larger than v_in')
        exit(1)
    if VOLTAGE_RATIO < 0:
        print('Error: Voltage ratio can not be negative')
        exit(1)

    print(SCHEMATIC)

    RUN = Run(SELECTED_SERIES, VOLTAGE_RATIO, RatioType.VOLTAGE)
elif ARGS.res_ratio:
    # Sanity check resistor ratio
    if ARGS.res_ratio < 0:
        print('Error: Resistor ratio can not be negative')
        exit(1)

    RUN = Run(SELECTED_SERIES, ARGS.res_ratio, RatioType.RESISTOR)
else:
    print('Error: Either specify v_in and v_out, or res-ratio')
    exit(1)

print(RUN.get_result(NUM_RESULTS))
exit(0)
