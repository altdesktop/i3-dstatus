import json
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

class Block:

    def __init__(self, name):
        self.name = name
        self.bus = dbus.SessionBus()
        self.interface = dbus.Interface(self.bus.get_object(
            'com.dubstepdish.i3dstatus',
            '/com/dubstepdish/i3dstatus'),
            'com.dubstepdish.i3dstatus')
        self.config = json.loads(self.interface.get_config(self.name))


    def show(self, full_text, instance=None, markup=None):
        block = {
            'name': self.name,
            'full_text': full_text,
        }

        if markup is True:
            markup = "pango"
        if markup:
            block['markup'] = markup
        if instance:
            block['instance'] = instance

        self.interface.show_block(block)
