from __future__ import print_function
import time
import socket

from common.view import price_to_string


class OandaGetter(object):
    """docstring for OandaGetter"""
    def __init__(self, parser):
        super(OandaGetter, self).__init__()

        self.ready = False
        self.args = None
        self.api = None

        self.add_arguments(parser)        


    def add_arguments(self, parser):
        """
        Add the arguments to an ArgumentParser for getter instance.

        Args:
            parser: The ArgumentParser to add the config option to
        """ 
        parser.add_argument(
            '--no-poll',
            action="store_true",
            default=False,
            help="Used to prevent polling for price updates"
        )

        parser.add_argument(
            '--poll-interval', '-p',
            type=float,
            default=2,
            help="The interval between polls"
        )

        self.ready = True


    def run(self, args, target):
        """
        Get the prices for a list of Instruments for the active Account.
        Repeatedly poll for newer prices if requested.
        """
        try:
            assert self.ready
        except AssertionError as error:
            raise error
        
        self.api = args.config.create_context()

        latest_price_time = None 

        def poll(latest_price_time):
            """
            Fetch and display all prices since than the latest price time

            Args:
                latest_price_time: The time of the newest Price that has been seen

            Returns:
                The updated latest price time
            """

            try:
                response = self.api.pricing.get(
                    args.config.active_account,
                    instruments=",".join(args.instrument),
                    since=latest_price_time,
                    includeUnitsAvailable=False
                )
            except socket.timeout:
                print('Connection timeout, retrying...')

            #
            # Print out all prices newer than the lastest time 
            # seen in a price
            #
            for price in response.get("prices", 200):
                if latest_price_time is None or price.time > latest_price_time:
                    target.push([
                        {
                            "measurement": price.instrument+"_price",
                            "tags": {
                                "host": "blotter",
                            },
                            "time": price.time,
                            "fields": {
                                "bid": price.bids[0].price,
                                "ask": price.asks[0].price,
                                "instrument": price.instrument,
                            }
                        }
                    ])
                    if not args.quite:
                        print(price_to_string(price))

            #
            # Stash and return the current latest price time
            #
            for price in response.get("prices", 200):
                if latest_price_time is None or price.time > latest_price_time:
                    latest_price_time = price.time
        
            return latest_price_time

        #
        # Fetch the current snapshot of prices
        #
        latest_price_time = poll(latest_price_time)

        #
        # Poll for of prices
        #
        while not args.no_poll:
            time.sleep(args.poll_interval)
            latest_price_time = poll(latest_price_time)



