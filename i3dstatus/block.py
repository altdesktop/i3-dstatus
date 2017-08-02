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


    @staticmethod
    def expand_template(text, context):
        if not context:
            return text

        for key in sorted(context.keys(), key=lambda k: len(k), reverse=True):
            text = text.replace('%' + key, str(context[key]))

        return text


    def show(self, full_text, instance=None, markup=None, context=None):
        block = {
            'name': self.name,
            'full_text': Block.expand_template(full_text, context),
        }

        if markup is True:
            markup = "pango"
        if markup:
            block['markup'] = markup
        if instance:
            block['instance'] = instance

        self.interface.show_block(block)
