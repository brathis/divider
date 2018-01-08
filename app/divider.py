#!/usr/bin/env python3
""" Handles user interaction """
import argparse
from models import Run, SERIES


SCHEMATIC = """
          R1           R2
     --[======]-----[======]--
    |            |            |
   V_in        V_out         GND
"""

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--v_in', type=float, required=True)
PARSER.add_argument('--v_out', type=float, required=True)
PARSER.add_argument('--series', type=str)
PARSER.add_argument('--num-results', type=int)
ARGS = PARSER.parse_args()

SELECTED_SERIES = SERIES.get('E12')
if ARGS.series:
    SELECTED_SERIES = SERIES.get(ARGS.series)
    if SELECTED_SERIES is None:
        print('Error: Series \'{}\' doesn\'t exist'.format(ARGS.series))
        exit(1)

NUM_RESULTS = 1
if ARGS.num_results:
    NUM_RESULTS = ARGS.num_results


print(SCHEMATIC)
print(Run(SELECTED_SERIES, ARGS.v_out / ARGS.v_in).get_result(NUM_RESULTS))
