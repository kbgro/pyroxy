"""Console script for pyroxy."""
import logging
import sys

import click

from . import pyroxy
from .address import Anonymity, Protocol
from .settings import setup

setup()

logger = logging.getLogger("cli")


@click.group()
def proxies():
    pass


@proxies.command()
@click.argument("filename")
@click.option("--site", type=click.Choice(["geonode", "freeproxy"], case_sensitive=False))
@click.option("--cached/--no-cached", default=False)
def proxylist(filename, site, cached):
    """Write proxy list to a file."""
    if cached:
        proxies_ = pyroxy.cached_proxies()
        logger.info(f"CACHED: {len(proxies_)}")
    else:
        proxies_ = pyroxy.proxy_list(site)
    proxy_list = pyroxy.filter_proxy_list(proxies_, [Protocol.HTTPS, Protocol.SOCKS4, Protocol.SOCKS5], [Anonymity.HIA])
    pyroxy.proxy_list_file(filename, proxy_list)


if __name__ == "__main__":
    sys.exit(proxies())  # pragma: no cover
