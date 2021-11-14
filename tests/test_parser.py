from pprint import pprint

import requests

from pyroxy.parser import FreeProxyNetParser, GeoNodeProxyParser
from pyroxy.settings import Config


def test_parse_free_net():
    response = requests.get(Config.FREE_PROXY_NET_URL, headers=Config.HEADERS)
    proxy_list = FreeProxyNetParser.parse(response)
    print()
    pprint(proxy_list)


def test_parse_geonode():
    response = requests.get(Config.GEO_NODE_URL, headers=Config.HEADERS)
    proxy_list = GeoNodeProxyParser.parse(response)
    print()
    pprint(proxy_list)
