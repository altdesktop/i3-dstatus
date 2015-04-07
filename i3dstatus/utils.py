"""
Utility functions for generators.
"""
import dbus
from .service import DBUS_SERVICE, PATH_PREFIX, BlockManager, Block
__all__ = 'make_block',


class make_block:
    """
    Boilerplates the creation and cleanup of a block.

    >>> with make_block('spam', {}) as bgen:
    ...     block = bgen()
    ...     pass  # More code

    (We use the callable so that if the lookup fails, the finally triggers)
    """

    def __init__(self, bid, defaults=None):
        self.bid = bid
        self.defaults = defaults or {}
        self.service = dbus.Interface(
            dbus.SessionBus().get_object(DBUS_SERVICE, PATH_PREFIX),
            BlockManager.INTERFACE
        )

    def __enter__(self, service):
        self.blockpath = bpath = self.service.create_block(self.bid, self.defaults)
        return lambda: dbus.Interface(
            dbus.SessionBus().get_object(DBUS_SERVICE, bpath),
            Block.INTERFACE
        )

    def __exit__(self, *_):
        self.service.remove_block(self.blockpath)
