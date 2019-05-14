import json
import dbus
import dbus.mainloop.glib


class Block:
    def __init__(self, name):
        self.name = name
        self.bus = dbus.SessionBus()
        self.interface = dbus.Interface(
            self.bus.get_object('com.dubstepdish.i3dstatus', '/com/dubstepdish/i3dstatus'),
            'com.dubstepdish.i3dstatus')
        self.config = json.loads(self.interface.get_config(self.name))

        self.notifications = None

        try:
            self.notifications = dbus.Interface(
                self.bus.get_object('org.freedesktop.Notifications',
                                    '/org/freedesktop/Notifications'),
                'org.freedesktop.Notifications')
        except dbus.DBusException:
            # notifications are unavailable
            pass

    @staticmethod
    def expand_template(text, context):
        if not context:
            return text

        for key in sorted(context.keys(), key=lambda k: len(k), reverse=True):
            text = text.replace('%' + key, str(context[key]))

        return text

    def clear(self, instance=None):
        block = {
            'name': self.name,
            'full_text': '',
        }
        if instance:
            block['instance'] = instance

        self.interface.show_block(block)

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

    def notify(self, message):
        if self.notifications:
            # https://developer.gnome.org/notification-spec/
            message = 'i3-dstatus [{generator}]: {msg}'.format(generator=self.name, msg=message)
            self.notifications.Notify('i3dstatus', 0, '', '', message, [], [], -1)

    def error(self, message):
        # TODO error log
        self.notify(message)
