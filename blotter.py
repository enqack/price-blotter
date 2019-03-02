#!/usr/bin/env python3
"""
An Oanda blotter

author: Steve Verhelle


"""
import argparse

import common.config
import common.args
from common.view import price_to_string, heartbeat_to_string

from getter.oanda import OandaGetter
from streamer.oanda import OandaStreamer
from target.influxdb import InfluxDBTarget


class Blotter(object):
    def __init__(self, parser):
        self.parser = parser

    def run(self):
        # set endpoints and get their arguments
        source = OandaGetter(self.parser)
        target = InfluxDBTarget(self.parser)

        # parse main and enpoint arguments
        args = self.parser.parse_args()

        # connect to target database
        target.connect()

        # run source collection
        source.run(args, target)


def main():
    """
    Blotter price ingester
    """
    # init argument parser
    parser = argparse.ArgumentParser()

    # add main arguments    
    common.config.add_argument(parser)
    
    parser.add_argument(
        '--instrument', '-i',
        type=common.args.instrument,
        required=True,
        action='append',
        help='Instrument to get prices for'
    )

    parser.add_argument(
        '--quite', '-q',
        action='store_true',
        default=False,
        help='Used to prevent polling for price updates'
    )

    blotter = Blotter(parser)
    blotter.run()



if __name__ == "__main__":
    main()
