from __future__ import print_function
import sys

from tabulate import tabulate


def print_title(s):
    """
    Print a string as a title with a strong underline

    Args:
        s: string to print as a title
    """
    print(s)
    print(len(s) * "=")
    print("")


def print_subtitle(s):
    """
    Print a string as a subtitle with an underline

    Args:
        s: string to print as a title
    """
    print(s)
    print(len(s) * "-")
    print("")


def print_entity(entity, title=None, headers=True):
    """
    Print an entity as a title along with the tabular representation
    of the entity.

    Args:
        title: The title to print
        entity: The entity to print
    """

    if title is not None and len(title) > 0:
        print_title(title)

    headers = ["Name", "Value"]
    headers=[]
    tablefmt = "rst"
    body = []

    for field in entity.fields():
        name = field.displayName
        value = field.value
        if field.typeClass.startswith("array"):
            value = "[{}]".format(len(field.value))
        elif field.typeClass.startswith("object"):
            value = "<{}>".format(field.typeName)
        body.append([name, value])

    getattr(sys.stdout, 'buffer', sys.stdout).write(
        tabulate
        (
            body,
            headers,
            tablefmt=tablefmt
        ).encode('utf-8')
    )
    print("")

def price_to_string(price):
    return "{} ({}) bid: {} ask: {}".format(
        price.instrument,
        price.time,
        price.bids[0].price,
        price.asks[0].price
    )

def heartbeat_to_string(heartbeat):
    return "HEARTBEAT ({})".format(
        heartbeat.time
    )