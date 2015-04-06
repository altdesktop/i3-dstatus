"""
Defines and manages d-bus services and objects.
"""
import dbus
import dbus.service
import weakref
import threading
from aioevents import Event

DBUS_SERVICE = 'com.dubstepdish.i3dstatus'


class BlockManager(dbus.service.Object):
    """
    Manages block objects.
    """
    INTERFACE = 'com.dubstepdish.i3dstatus.Manager'

    blockchanged = Event("Fires when one of the managed blocks changes.")
    blockadded = Event("Fires when a new block is added.")
    blockremoved = Event("Fires when a block is removed.")

    def __init__(self, config):
        bus_name = dbus.service.BusName(DBUS_SERVICE, bus=dbus.SessionBus())
        super().__init__(bus_name, '/com/dubstepdish/i3dstatus')
        self.blocks = []
        self.config = {"general": {}}

        # cache the config
        self.config = config

        # Can't do this statically due to instances
        self.blockchanged.handler(self.block_changed)

    @dbus.service.signal(INTERFACE, signature="o")
    def block_changed(self, block):
        pass

    @dbus.service.method(INTERFACE, in_signature="sa{sv}", out_signature="o")
    def create_block(self, name, defaults=None):
        pass  # TODO

    @dbus.service.method(INTERFACE, in_signature="o")
    def remove_block(self, block):
        pass  # TODO

    @dbus.service.method(INTERFACE, in_signature='s', out_signature='v')
    def get_config(self, genname):
        """
        Get a generator's configuration block
        """
        if genname in self.config:
            return self.config[genname]
        else:
            return {}


class Block(dbus.service.Object):
    """
    A single block in i3bar.

    Doc strings blatently ripped from http://i3wm.org/docs/i3bar-protocol.html
    """
    INTERFACE = 'com.dubstepdish.i3dstatus.Block'
    _WELL_KNOWN_PROPS = set(
        'full_text', 'short_text', 'color', 'min_width', 'align', 'name',
        'instance', 'urgent', 'separator', 'separator_block_width', 'markup',
        # Not in the spec; used for our purposes
        'order',
        )

    changed = Event("Raised when a property is set")
    # FIXME: Have a D-bus signal of the same name

    def __init__(self, manager):
        self._manager = weakref.ref(manager)  # Don't create reference cycles

        # Slight misnomer. Only locks out changed events. Doesn't actually prevent other changes.
        self._change_lock = threading.Lock()  # XXX: Use asyncio.Lock? Only if .update() is a coroutine

        self._props = {}

        self.changed.handler(self._call_manager_changed)

    def _call_manager_changed(self):
        """
        Propogates block changes to the parent manager's blockchanged event
        """
        man = self._manager
        if man is not None:
            man.blockchanged(self)


    @dbus.service.method(INTERFACE, in_signature='a{sv}')
    def update(self, values):
        """
        Performs a bulk update of properties. Issues only one changed event for
        the entire update.
        """
        # XXX: Rewrite as aio coroutine?
        with self._change_lock:
            for prop, value in values.items():
                if prop in self._WELL_KNOWN_PROPS:
                    setattr(self, prop, value)
                else:
                    self._props[prop] = value
        self.changed()

    def _changed(self):
        """
        Raise a changed event, unless it's been locked out by update()
        """
        have_lock = self._change_lock.acquire(blocking=False)
        if have_lock:
            self._change_lock.release()
            self.changed()

    @dbus.service.method(INTERFACE, in_signature='s', out_signature='v')
    def get_prop(self, name):
        """
        Gets a user-defined property.
        """
        return self._props.get(name)

    @dbus.service.method(INTERFACE, in_signature='sv')
    def set_prop(self, name, value):
        """
        Sets a user-defined property.
        """
        self._props[name] = value

    # I wish I could do this with metaprogramming, but I can't think of a
    # solution that's not tedious and worth the time.

    full_text = property(
        """The full_text will be displayed by i3bar on the status line. This is
        the only required key."""
        )
    _full_text = ""

    @dbus.service.method(INTERFACE, out_signature='s')
    @full_text.getter
    def get_full_text(self):
        return self._full_text

    @dbus.service.method(INTERFACE, in_signature='s')
    @full_text.setter
    def set_full_text(self, value):
        self._full_text = str(value)
        self._changed()

    short_text = property(
        """Where appropriate, the short_text (string) entry should also be
        provided. It will be used in case the status line needs to be shortened
        because it uses more space than your screen provides. For example, when
        displaying an IPv6 address, the prefix is usually (!) more relevant
        than the suffix, because the latter stays constant when using autoconf,
        while the prefix changes. When displaying the date, the time is more
        important than the date (it is more likely that you know which day it
            is than what time it is)."""
        )
    _short_text = ""

    @dbus.service.method(INTERFACE, out_signature='s')
    @short_text.getter
    def get_short_text(self):
        return self._short_text

    @dbus.service.method(INTERFACE, in_signature='s')
    @short_text.setter
    def set_short_text(self, value):
        self._short_text = str(value)
        self._changed()

    color = property(
        """To make the current state of the information easy to spot, colors 
        can be used. For example, the wireless block could be displayed in red
        (using the color (string) entry) if the card is not associated with any
        network and in green or yellow (depending on the signal strength) when
        it is associated. Colors are specified in hex (like in HTML), starting
        with a leading hash sign. For example, #ff0000 means red."""
        )
    _color = ""

    @dbus.service.method(INTERFACE, out_signature='s')
    @color.getter
    def get_color(self):
        return self._color

    @dbus.service.method(INTERFACE, in_signature='s')
    @color.setter
    def set_color(self, value):
        self._color = str(value)
        self._changed()

    min_width = property(
        """The minimum width (in pixels) of the block. If the content of the
        full_text key take less space than the specified min_width, the block
        will be padded to the left and/or the right side, according to the
        align key. This is useful when you want to prevent the whole status
        line to shift when value take more or less space between each
        iteration. The value can also be a string. In this case, the width of
        the text given by min_width determines the minimum width of the block.
        This is useful when you want to set a sensible minimum width regardless
        of which font you are using, and at what particular size."""
        )
    _min_width = 0

    @dbus.service.method(INTERFACE, out_signature='v')
    @min_width.getter
    def get_min_width(self):
        return self._min_width

    @dbus.service.method(INTERFACE, in_signature='v')
    @min_width.setter
    def set_min_width(self, value):
        if not isinstance(value, (int, str)):
            raise ValueError("Must be an int or str")
        self._min_width = value
        self._changed()

    align = property(
        """Align text on the center, right or left (default) of the block, when
        the minimum width of the latter, specified by the min_width key, is not
        reached."""
        )
    _align = "left"

    @dbus.service.method(INTERFACE, out_signature='s')
    @align.getter
    def get_align(self):
        return self._align

    @dbus.service.method(INTERFACE, in_signature='s')
    @align.setter
    def set_align(self, value):
        if value not in ('left', 'center', 'right'):
            raise ValueError("Must be one of 'left', 'center', or 'right'")
        self._align = value
        self._changed()

    name = property(
        """Every block should have a unique name (string) entry so that it can
        be easily identified in scripts which process the output. i3bar
        completely ignores the name and instance fields."""
        )
    _name = ""

    @dbus.service.method(INTERFACE, out_signature='s')
    @name.getter
    def get_name(self):
        return self._name

    @dbus.service.method(INTERFACE, in_signature='s')
    @name.setter
    def set_name(self, value):
        self._name = str(value)
        self._changed()

    instance = property(
        """Make sure to also specify an instance (string) entry where
        appropriate. For example, the user can have multiple disk space blocks
        for multiple mount points. i3bar completely ignores the name and
        instance fields."""
        )
    _instance = ""

    @dbus.service.method(INTERFACE, out_signature='s')
    @instance.getter
    def get_instance(self):
        return self._instance

    @dbus.service.method(INTERFACE, in_signature='s')
    @instance.setter
    def set_instance(self, value):
        self._instance = str(value)
        self._changed()

    urgent = property(
        """A boolean which specifies whether the current value is urgent.
        Examples are battery charge values below 1 percent or no more available
        disk space (for non-root users). The presentation of urgency is up to
        i3bar."""
        )
    _urgent = False

    @dbus.service.method(INTERFACE, out_signature='b')
    @urgent.getter
    def get_urgent(self):
        return self._urgent

    @dbus.service.method(INTERFACE, in_signature='b')
    @urgent.setter
    def set_urgent(self, value):
        self._urgent = bool(value)
        self._changed()

    separator = property(
        """A boolean which specifies whether a separator line should be drawn
        after this block. The default is true, meaning the separator line will
        be drawn. Note that if you disable the separator line, there will still
        be a gap after the block, unless you also use separator_block_width."""
        )
    _separator = True

    @dbus.service.method(INTERFACE, out_signature='b')
    @separator.getter
    def get_separator(self):
        return self._separator

    @dbus.service.method(INTERFACE, in_signature='b')
    @separator.setter
    def set_separator(self, value):
        self._separator = bool(value)
        self._changed()

    separator_block_width = property(
        """The amount of pixels to leave blank after the block. In the middle
        of this gap, a separator line will be drawn unless separator is
        disabled. Normally, you want to set this to an odd value (the default
        is 9 pixels), since the separator line is drawn in the middle."""
        )
    _separator_block_width = 9

    @dbus.service.method(INTERFACE, out_signature='u')
    @separator_block_width.getter
    def get_separator_block_width(self):
        return self._separator_block_width

    @dbus.service.method(INTERFACE, in_signature='u')
    @separator_block_width.setter
    def set_separator_block_width(self, value):
        self._separator_block_width = int(value)
        self._changed()

    markup = property(
        """A string that indicates how the text of the block should be parsed.
        Set to "pango" to use Pango markup. Set to "none" to not use any markup
        (default)."""
        )
    _markup = "none"

    @dbus.service.method(INTERFACE, out_signature='s')
    @markup.getter
    def get_markup(self):
        return self._markup

    @dbus.service.method(INTERFACE, in_signature='s')
    @markup.setter
    def set_markup(self, value):
        if value not in ('pango', 'none'):
            raise ValueError("Must be one of 'pango' or 'none'")
        self._markup = value
        self._changed()

    order = property(
        """An integer to give the order of blocks. Lower numbers appear 
        "sooner". Blocks of the same order may appear in any order."""
        )
    _order = "none"

    @dbus.service.method(INTERFACE, out_signature='s')
    @order.getter
    def get_order(self):
        return self._order

    @dbus.service.method(INTERFACE, in_signature='s')
    @order.setter
    def set_order(self, value):
        self._order = value
        self._changed()
