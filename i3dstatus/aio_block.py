from __future__ import annotations

import json
from dbus_next import Variant
from dbus_next.aio import MessageBus
from dbus_next.introspection import Node

import os
from .service import StatusService

here = os.path.abspath(os.path.dirname(__file__))

with open(f'{here}/data/notifications.xml', 'r') as f:
    introspection = Node.parse(f.read())


class Block:
    def __init__(self, name):
        self.name = name
        self.notifications = None

    async def connect(self) -> Block:
        bus = await MessageBus().connect()
        obj = bus.get_proxy_object('org.freedesktop.Notifications',
                                   '/org/freedesktop/Notifications', introspection)
        self.notifications = obj.get_interface('org.freedesktop.Notifications')
        obj = bus.get_proxy_object('com.dubstepdish.i3dstatus', '/com/dubstepdish/i3dstatus',
                                   Node(interfaces=[StatusService().introspect()]))
        self.i3dstatus = obj.get_interface('com.dubstepdish.i3dstatus')
        config_json = await self.i3dstatus.call_get_config(self.name)
        self.config = json.loads(config_json)
        return self

    @staticmethod
    def expand_template(text, context):
        if not context:
            return text

        for key in sorted(context.keys(), key=lambda k: len(k), reverse=True):
            text = text.replace('%' + key, str(context[key]))

        return text

    async def clear(self, instance=None):
        block = {
            'name': Variant('s', self.name),
            'full_text': Variant('s', ''),
        }
        if instance:
            block['instance'] = instance

        await self.i3dstatus.call_show_block(block)

    async def show(self, full_text, instance=None, markup=None, context=None):
        block = {
            'name': Variant('s', self.name),
            'full_text': Variant('s', Block.expand_template(full_text, context)),
        }

        if markup is True:
            markup = "pango"
        if markup:
            block['markup'] = Variant('s', markup)
        if instance:
            block['instance'] = Variant('s', instance)

        await self.i3dstatus.call_show_block(block)

    async def notify(self, message):
        if self.notifications:
            # https://developer.gnome.org/notification-spec/
            message = 'i3-dstatus [{generator}]: {msg}'.format(generator=self.name, msg=message)
            await self.notifications.call_notify('i3dstatus', 0, '', '', message, [], {}, -1)

    async def error(self, message):
        # TODO error log
        await self.notify(message)
