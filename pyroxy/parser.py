import base64
import logging
from abc import ABC, abstractmethod
from os import listdir
from pathlib import Path
from typing import List, Union

from parsel import Selector
from requests import Response

from .address import Anonymity, Protocol, ProxyAddress, Speed, SpeedType

logger = logging.getLogger("parser")


class FreeProxyParser(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, response: Response) -> List[ProxyAddress]:
        raise NotImplementedError

    @staticmethod
    def setup_protocol(protocol_text: str) -> Protocol:
        protocol_map = {
            "HTTP": Protocol.HTTP,
            "HTTPS": Protocol.HTTPS,
            "SOCKS4": Protocol.SOCKS4,
            "SOCKS5": Protocol.SOCKS5,
        }
        return protocol_map.get(protocol_text.upper(), Protocol.UNKNOWN)

    @staticmethod
    def setup_anonymity(anonymity_text: str) -> Anonymity:
        anonymous = {
            # No Anonymity
            "transparent": Anonymity.NOA,
            "level3": Anonymity.NOA,
            # Anonymous
            "anonymous": Anonymity.ANM,
            "level2": Anonymity.ANM,
            # High Anonymity
            "elite": Anonymity.HIA,
            "elite proxy": Anonymity.HIA,
            "High anonymity": Anonymity.HIA,
            "level1": Anonymity.HIA,
        }
        return anonymous.get(anonymity_text, Anonymity.UNKNOWN)


class FreeProxyNetParser(FreeProxyParser):
    @classmethod
    def parse(cls, response: Response) -> List[ProxyAddress]:
        if response.status_code != 200:
            logger.info(f"Response: [{response.status_code}] : {response.url}")
            return []

        selector = Selector(response.text)
        p_rows = selector.css(".fpl-list > table tr")

        proxy_list = []
        for tr in p_rows:
            tds = tr.css("td")
            if not tds:
                continue
            ip = tds[0].css("::text").get()
            port = tds[1].css("::text").get()
            google = (tds[5].css("::text").get() or "") in "yes"
            country = tds[3].css("::text").get()
            anonymity = cls.setup_anonymity(tds[4].css("::text").get())
            https = tds[6].css("::text").get()
            updated = tds[7].css("::text").get()

            protocols = "https" if https == "yes" else "http"
            protocol = cls.setup_protocol(protocols)

            pad = ProxyAddress(ip, port, protocol, country, updated, google=google, anonymity=anonymity)
            proxy_list.append(pad)

        return proxy_list


class GeoNodeProxyParser(FreeProxyParser):
    @classmethod
    def parse(cls, response: Response) -> List[ProxyAddress]:
        if response.status_code != 200:
            logger.info(f"Response: [{response.status_code}] : {response.url}")
            return []

        data = response.json().get("data")

        proxy_list = []
        for proxy in data:
            ip = proxy.get("ip")
            port = proxy.get("port")
            anonymity = cls.setup_anonymity(proxy.get("anonymityLevel"))
            country = proxy.get("country")
            google = proxy.get("google")
            updated = proxy.get("updated_at")

            protocols = proxy.get("protocols")
            protocol = protocols[0] if protocols else ""
            protocol = cls.setup_protocol(protocol)

            speed = Speed(SpeedType.TIME, proxy.get("speed", -1))
            response_time = Speed(SpeedType.TIME, proxy.get("responseTime", -1))

            pad = ProxyAddress(
                ip,
                port,
                protocol,
                country,
                updated,
                google=google,
                anonymity=anonymity,
                speed=speed,
                response=response_time,
            )
            proxy_list.append(pad)

        return proxy_list


class FreeProxyCZ(FreeProxyParser):
    @classmethod
    def parse(cls, response: Union[Response, str]) -> List[ProxyAddress]:
        selector = Selector(response.text) if isinstance(response, Response) else Selector(response)
        ip_rows = selector.css("table#proxy_list tbody > tr")
        column_length = len(list(map(lambda s: s.get(), selector.css("table#proxy_list th ::text"))))
        proxies: List[ProxyAddress] = []
        for row in ip_rows:
            tds = row.css("td")
            if len(tds) != column_length:
                continue

            ip = cls._parse_ip(tds[0])
            port = int(tds[1].css("::text").get())
            protocol = tds[2].css("::text").get()
            country = tds[3].css("a::text").get()
            _ = tds[4].css("::text").get()  # region
            _ = tds[5].css("::text").get()  # city
            anonymity = tds[6].css("::text").get()
            speed = tds[7].css("small::text").get()
            _ = tds[8].css("small::text").get()  # uptime
            response_time = tds[9].css("small::text").get()
            last_checked = tds[10].css("small::text").get()

            pad = ProxyAddress(
                ip,
                port,
                cls.setup_protocol(protocol),
                country,
                last_checked,
                anonymity=cls.setup_anonymity(anonymity),
                speed=speed,
                response=response_time,
            )
            proxies.append(pad)
        return proxies

    @staticmethod
    def _parse_ip(ip_selector: Selector) -> str:
        ip_string = ip_selector.css("script").re_first(r".*\(\"(.+)\"")
        clean_ip_string = ip_string.split('")')[0]
        return base64.urlsafe_b64decode(clean_ip_string).decode()

    @staticmethod
    def from_cache(cache_dir: Path) -> List[ProxyAddress]:
        proxies = set()
        for file in listdir(cache_dir):
            with open(cache_dir / file) as f:
                text = f.read()
                proxies.update(FreeProxyCZ.parse(text))

        return list(proxies)
