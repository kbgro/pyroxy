"""Console script for pyroxy."""
import sys

import click

from pyroxy.address import Anonymity, Protocol

from . import pyroxy


@click.group()
def proxies():
    pass


@proxies.command()
@click.argument("filename")
def proxylist(filename):
    """Write proxy list to a file."""
    proxy_list = pyroxy.filter_proxy_list(None, [Protocol.HTTPS, Protocol.SOCKS4], [Anonymity.HIA])
    pyroxy.proxy_list_file(filename, proxy_list)


if __name__ == "__main__":
    sys.exit(proxies())  # pragma: no cover
