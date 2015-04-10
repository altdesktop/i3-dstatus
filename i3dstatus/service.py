"""
Defines and manages d-bus services and objects.
"""
import json
import dbus
import dbus.service
import sys

DBUS_SERVICE = 'com.dubstepdish.i3dstatus'


class DStatusService(dbus.service.Object):
    """
    Manages block objects.
    """
    INTERFACE = 'com.dubstepdish.i3dstatus.Manager'

    def __init__(self, config):
        bus_name = dbus.service.BusName(DBUS_SERVICE, bus=dbus.SessionBus())
        super().__init__(bus_name, '/com/dubstepdish/i3dstatus')
        self.blocks = []
        self.config = {"general": {}}

        # cache the config
        self.config = config

    @dbus.service.method(INTERFACE, in_signature='a{sv}')
    def show_block(self, block):
        # apply config options to the block
        block_config = {}
        if block['name'] in self.config:
            if 'instance' in block and \
                    block['instance'] in self.config[block['name']]:
                # this block is configured by instance
                block_config = self.config[block['name']][block['instance']]
            else:
                block_config = self.config[block['name']]

        for i3bar_key in ['color', 'min_width', 'min-width' 'align',
                          'separator', 'separator_block_width',
                          'separator-block-width']:
            if i3bar_key.replace('-', '_') in block:
                # if given in the block, it overrides the config
                continue
            if 'general' in self.config and \
                    i3bar_key in self.config['general']:
                # if given in the general config, this is the default for all
                # blocks
                k = i3bar_key.replace('-', '_')
                block[k] = self.config['general'][i3bar_key]
            if i3bar_key in block_config:
                # if given in the block config, this overrides the general
                # config
                k = i3bar_key.replace('-', '_')
                block[k] = block_config[i3bar_key]

        # try to find the block given by the name and replace it
        block_found = False
        for i, b in enumerate(self.blocks):
            if b['name'] == block['name']:
                block_found = True
                self.blocks[i] = block

        if not block_found:
            self.blocks.append(block)

        # filter out blocks with no 'full_text' member
        self.blocks = [b for b in self.blocks if 'full_text' in b and
                       b['full_text']]

        sys.stdout.write(',' + json.dumps(self.blocks, ensure_ascii=False) +
                         '\n')
        sys.stdout.flush()

    @dbus.service.method(INTERFACE, in_signature='s', out_signature='s')
    def get_config(self, block_name):
        if block_name in self.config:
            return json.dumps(self.config[block_name], ensure_ascii=False)
        else:
            return '{}'
