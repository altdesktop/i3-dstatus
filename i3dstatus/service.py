#!/usr/bin/env python3

from gi.repository import GLib
import json
import dbus
import dbus.service
import sys
import os
import threading
import subprocess
from dbus.mainloop.glib import DBusGMainLoop
import yaml


class GeneratorThread(threading.Thread):
    def __init__(self, generator_path):
        self.generator_path = generator_path
        threading.Thread.__init__(self)

    def run(self):
        subprocess.call(self.generator_path)


class DStatusService(dbus.service.Object):
    def __init__(self, generators):
        bus_name = dbus.service.BusName('com.dubstepdish.i3dstatus',
                                        bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name,
                                     '/com/dubstepdish/i3dstatus')
        self.blocks = []
        self.generators = generators
        self.config = {}

        script_dir = os.path.dirname(__file__)

        paths = []
        # arguments are the names of generators to run
        for generator in generators:
            generator_path = ''
            if generator[0] == '~' and os.path.isabs(os.path.expanduser(generator[0])):
                generator_path = os.path.expanduser(generator)
            elif generator[0] == '/':
                generator_path = generator
            else:
                generator_path = os.path.join(script_dir, 'generators', generator)

            if os.path.isfile(generator_path):
                paths.append(generator_path)
            else:
                sys.stderr.write(
                        "ERROR: could not find generator: {}".format(generator)
                        )

        for generator_path in paths:
            GeneratorThread(generator_path).start()

        # cache the config
        try:
            f = open("{}/.i3-dstatus.conf".format(os.path.expanduser('~')))
            self.config = yaml.safe_load(f)
            f.close()
        except FileNotFoundError:
            pass

        if 'general' in self.config:
            if 'order' in self.config['general']:
                # `order` in the config overrides generator order given on the
                # command line
                self.generators = self.config['general']['order']

    @dbus.service.method('com.dubstepdish.i3dstatus', in_signature='a{sv}')
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

        # sort by the order the generators were given
        def sort_blocks(b):
            if b['name'] in self.generators:
                return self.generators.index(b['name']) + 1
            else:
                return 0

        self.blocks.sort(key=sort_blocks)

        sys.stdout.write(',' + json.dumps(self.blocks, ensure_ascii=False) +
                         '\n')
        sys.stdout.flush()

    @dbus.service.method('com.dubstepdish.i3dstatus',
                         in_signature='s', out_signature='s')
    def get_config(self, block_name):
        if block_name in self.config:
            return json.dumps(self.config[block_name], ensure_ascii=False)
        else:
            return '{}'


def start():
    DBusGMainLoop(set_as_default=True)
    DStatusService(sys.argv[1:])

    sys.stdout.write('{"version":1}\n[\n[]\n')
    # sys.stdout.write('{"version":1, "click_events":true}\n[\n[]\n')
    sys.stdout.flush()

    main = GLib.MainLoop()
    main.run()

if __name__ == '__main__':
    start()
