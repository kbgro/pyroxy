"""Main module."""
from typing import List, Optional

import requests

from .address import Anonymity, Protocol, ProxyAddress
from .parser import FreeProxyNetParser, GeoNodeProxyParser
from .settings import Config

ProxiesType = List[ProxyAddress]


def proxy_list() -> ProxiesType:
    proxies = []

    fn_proxy_list = FreeProxyNetParser.parse(requests.get(Config.FREE_PROXY_NET_URL, headers=Config.HEADERS))
    geo_proxy_list = GeoNodeProxyParser.parse(requests.get(Config.GEO_NODE_URL, headers=Config.HEADERS))

    proxies.extend(fn_proxy_list)
    proxies.extend(geo_proxy_list)

    return proxies


def filter_proxy_list(google: Optional[bool], protocols: List[Protocol], anonymity: List[Anonymity]) -> ProxiesType:
    proxies = proxy_list()

    filtered_proxies = ProxyFilters.google(proxies, google)
    filtered_proxies = ProxyFilters.protocol(filtered_proxies, protocols)
    filtered_proxies = ProxyFilters.anonymity(filtered_proxies, anonymity)

    return filtered_proxies


def proxy_list_file(filename: str, proxies: ProxiesType) -> None:
    with open(filename, "w") as f:
        proxies_text = "\n".join(set(map(lambda p: f"{p.ip}:{p.port}", proxies)))
        f.write(proxies_text)


class ProxyFilters:
    @staticmethod
    def google(proxies, use_google: Optional[bool]) -> ProxiesType:
        if use_google is not None:
            proxies = list(filter(lambda p: p.google == use_google, proxies))
        return proxies

    @staticmethod
    def anonymity(proxies: ProxiesType, anonymity_list: List[Anonymity]) -> ProxiesType:
        if anonymity_list:
            proxies = list(filter(lambda p: p.anonymity in anonymity_list, proxies))
        return proxies

    @staticmethod
    def protocol(proxies: ProxiesType, protocols: List[Protocol]) -> ProxiesType:
        if protocols:
            proxies = list(filter(lambda p: p.protocol in protocols, proxies))
        return proxies
