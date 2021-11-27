import logging
from abc import ABC, abstractmethod
from typing import List

from parsel import Selector
from requests import Response

from .address import Anonymity, Protocol, ProxyAddress, Speed, SpeedType

logger = logging.getLogger(__file__)


class FreeProxyParser(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, response: Response) -> List[ProxyAddress]:
        raise NotImplementedError

    @staticmethod
    def setup_protocol(protocol_text: str) -> Protocol:
        protocol_map = {"http": Protocol.HTTP, "https": Protocol.HTTPS}
        return protocol_map.get(protocol_text, Protocol.UNKNOWN)

    @staticmethod
    def setup_anonymity(anonymity_text: str) -> Anonymity:
        anonymous = {
            "anonymous": Anonymity.ANM,
            "transparent": Anonymity.NOA,
            "elite": Anonymity.HIA,
            "elite proxy": Anonymity.HIA,
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
