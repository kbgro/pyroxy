"""Main module."""
import logging
from typing import List, Optional

import requests

from .address import Anonymity, Protocol, ProxyAddress
from .parser import FreeProxyCZ, FreeProxyNetParser, GeoNodeProxyParser
from .settings import Config

logger = logging.getLogger("pyroxy")

ProxiesType = List[ProxyAddress]


def proxy_list(site: Optional[str]) -> ProxiesType:
    proxies = []

    fn_proxy_list = FreeProxyNetParser.parse(requests.get(Config.FREE_PROXY_NET_URL, headers=Config.HEADERS))
    geo_proxy_list = GeoNodeProxyParser.parse(requests.get(Config.GEO_NODE_URL, headers=Config.HEADERS))

    logger.info(f"FREE NET: {len(fn_proxy_list)}")
    logger.info(f"GEONODE : {len(geo_proxy_list)}")

    if not site:
        proxies.extend(fn_proxy_list)
        proxies.extend(geo_proxy_list)
        logger.info(f"Returning all sites proxies : {len(proxies)}")
    elif site and site.lower() == "freeproxy":
        proxies.extend(fn_proxy_list)
    elif site and site.lower() == "geonode":
        proxies.extend(geo_proxy_list)

    return proxies


def filter_proxy_list(
    proxies: ProxiesType, protocols: List[Protocol], anonymity: List[Anonymity], google: Optional[bool] = None
) -> ProxiesType:
    filtered_proxies = ProxyFilters.google(proxies, google)
    logger.info(f"Google    filtered: {len(filtered_proxies)}")

    filtered_proxies = ProxyFilters.protocol(filtered_proxies, protocols)
    logger.info(f"Protocol  filtered: {len(filtered_proxies)}")

    filtered_proxies = ProxyFilters.anonymity(filtered_proxies, anonymity)
    logger.info(f"Anonymity filtered: {len(filtered_proxies)}")

    return filtered_proxies


def proxy_list_file(filename: str, proxies: ProxiesType) -> None:
    with open(filename, "w") as f:
        proxies_text = "\n".join(set(map(lambda p: f"{p.ip}:{p.port}", proxies)))
        f.write(proxies_text)


def cached_proxies() -> ProxiesType:
    return FreeProxyCZ.from_cache(Config.CACHE_DIR)


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
