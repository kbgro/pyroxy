"""Top-level package for pyroxy."""
from .address import Anonymity, Protocol
from .pyroxy import filter_proxy_list, proxy_list

__author__ = """Daniel Ndegwa"""
__email__ = "daniendegwa@gmail.com"
__version__ = "0.1.0"

__all__ = ["proxy_list", "filter_proxy_list", "Protocol", "Anonymity"]
