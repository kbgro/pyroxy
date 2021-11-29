import logging
import os
from pathlib import Path


class Config:
    GEO_NODE_URL = "https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc&speed=fast"  # noqa
    FREE_PROXY_NET_URL = "https://free-proxy-list.net/"
    FREE_PROXY_CZ_URL = "http://free-proxy.cz/en/proxylist/country/all/socks/ping/all/1"

    CACHE_DIR = Path(__file__).resolve(True).parent.parent / ".pyroxy_cache"
    LOG_DIR = Path(__file__).resolve(True).parent.parent / "logs"

    LOG_FILE = LOG_DIR / "pyroxy.log"

    HEADERS = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",  # noqa
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa
        "Accept-Language": "en-US,en;q=0.9",
    }


def setup():
    setup_cache_directory()
    setup_logger()


def setup_logger():
    format_str = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"

    logging.basicConfig(
        level=logging.DEBUG,
        format=format_str,
        datefmt="%m-%d %H:%M",
        filename=Config.LOG_FILE,
        filemode="a+",
    )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(format_str)
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)


def setup_cache_directory():
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    os.makedirs(Config.LOG_DIR, exist_ok=True)
