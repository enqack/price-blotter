"""
The Oanda Streamer for blotter

"""
from __future__ import print_function
import socket

from common.view import price_to_string, heartbeat_to_string



class OandaStreamer(object):
    """ docstring for OandaStreamer """
    def __init__(self, parser):
        super(OandaStreamer, self).__init__()

        self.ready = False
        self.args = None
        self.api = None

        self.add_arguments(parser)


    def add_arguments(self, parser):
        """
        Add the arguments to an ArgumentParser that enables the creation of
        a streamer instance.

        Args:
            parser: The ArgumentParser to add the config option to
        """
        parser.add_argument(
            '--snapshot',
            action="store_true",
            default=True,
            help="Request an initial snapshot"
        )

        parser.add_argument(
            '--no-snapshot',
            dest="snapshot",
            action="store_false",
            help="Do not request an initial snapshot"
        )

        parser.add_argument(
            '--show-heartbeats', "-s",
            action='store_true',
            default=False,
            help="display heartbeats"
        )

        self.ready = True


    def run(self, args, target):
        """
        Runs the streamer

        Args:
            args: The supplied arguments
        """
        try:
            assert self.ready
        except AssertionError as error:
            raise error

        self.api = args.config.create_streaming_context()
        # self.api.set_convert_decimal_number_to_native(False)
        # self.api.set_stream_timeout(3)

        print('Subscribing to the pricing stream')
        try:
            response = self.api.pricing.stream(
                args.config.active_account,
                snapshot=args.snapshot,
                instruments=",".join(args.instrument),
            )
        except socket.timeout:
            print('Connection timeout, retrying...')

        # Print out each price as it is received
        for msg_type, msg in response.parts():
            if msg_type == "pricing.Heartbeat" and args.show_heartbeats:
                print(heartbeat_to_string(msg))
            elif msg_type == "pricing.Price":
                print(price_to_string(msg))
                target.push([
                    {
                        "measurement": msg.instrument+"_price",
                        "tags": {
                            "host": "blotter",
                        },
                        "time": msg.time,
                        "fields": {
                            "bid": msg.bids[0].price,
                            "ask": msg.asks[0].price,
                            "instrument": msg.instrument,
                        }
                    }
                ])
