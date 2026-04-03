"""Chat channels module with plugin architecture."""

from pgflow.channels.base import BaseChannel
from pgflow.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
