from __future__ import annotations

import json
import os
import copy
from dbus_next import Variant
from dbus_next.aio import MessageBus
from dbus_next.introspection import Node

from .service import StatusService

interfaces = {}


def get_interface_definition(iface: str):
    global interfaces
    if iface in interfaces:
        return interfaces[iface]

    iface_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'interfaces',
                              '{}.xml'.format(iface))
    with open(iface_path, 'r') as f:
        interfaces[iface] = f.read()

    return interfaces[iface]


class Block:
    def __init__(self, name, bus=None):
        self.name = name
        self.notifications = None
        self.notifications_xml = get_interface_definition('org.freedesktop.Notifications')
        self.bus = bus
        self.last_block = {}

    async def connect(self) -> Block:
        if self.bus is None:
            self.bus = await MessageBus().connect()
        obj = self.bus.get_proxy_object('org.freedesktop.Notifications',
                                        '/org/freedesktop/Notifications', self.notifications_xml)
        self.notifications = obj.get_interface('org.freedesktop.Notifications')
        obj = self.bus.get_proxy_object('com.dubstepdish.i3dstatus', '/com/dubstepdish/i3dstatus',
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

        if block != self.last_block:
            await self.i3dstatus.call_show_block(block)
            self.last_block = copy.deepcopy(block)

    async def notify(self, message):
        if self.notifications:
            # https://developer.gnome.org/notification-spec/
            message = 'i3-dstatus [{generator}]: {msg}'.format(generator=self.name, msg=message)
            await self.notifications.call_notify('i3dstatus', 0, '', '', message, [], {}, -1)

    async def error(self, message):
        # TODO error log
        await self.notify(message)
