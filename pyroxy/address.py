from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class Anonymity(Enum):
    UNKNOWN = 0  # Unknown Anonymous proxy
    HIA = 1  # High Anonymous proxy
    ANM = 2  # Anonymous proxy server
    NOA = 3  # Non Anonymous proxy


class Protocol(Enum):
    UNKNOWN = 0
    HTTP = 1
    HTTPS = 2
    SOCKS4 = 3
    SOCKS5 = 4


class SpeedType(Enum):
    BPS = 1
    TIME = 2


@dataclass(frozen=True)
class Speed:
    speed_type: SpeedType
    value: Union[int, float]


@dataclass(frozen=True)
class ProxyAddress:
    ip: str
    port: int
    protocol: Protocol
    country: str
    updated: str
    anonymity: Anonymity
    google: bool = False
    speed: Optional[Speed] = None
    uptime: Optional[Speed] = None
    response: Optional[Speed] = None
    latency: Optional[Speed] = None
