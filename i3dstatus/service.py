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
import argparse
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import datetime
import traceback


class GeneratorThread(threading.Thread):
    def __init__(self, generator_path):
        self.generator_path = generator_path
        threading.Thread.__init__(self)

    def run(self):
        subprocess.call(self.generator_path)


class DStatusService(dbus.service.Object):
    def __init__(self, generators, stream=sys.stdout, config={}):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()

        bus_name = dbus.service.BusName('com.dubstepdish.i3dstatus',
                                        bus=bus)
        dbus.service.Object.__init__(self, bus_name,
                                     '/com/dubstepdish/i3dstatus')

        self.blocks = []
        self.generators = generators
        self.config = config if config else {}
        self.stream = stream

        script_dir = os.path.dirname(__file__)

        if 'general' in self.config:
            if 'generators' in self.config['general']:
                # append the generators in the config to the list of generators
                for generator in self.config['general']['generators']:
                    if generator not in self.generators:
                        self.generators.append(generator)

        paths = []
        # arguments are the names of generators to run
        for generator in generators:
            generator_path = ''
            if os.path.isabs(os.path.expanduser(generator)):
                generator_path = os.path.expanduser(generator)
            else:
                generator_path = os.path.join(script_dir, 'generators',
                                              generator)

            if os.path.isfile(generator_path):
                paths.append(generator_path)
            else:
                sys.stderr.write(
                        "Could not find generator: {}".format(generator)
                        )

        self.stream.write('{"version":1}\n[\n[]\n')
        # self.stream..write('{"version":1, "click_events":true}\n[\n[]\n')
        self.stream.flush()

        for generator_path in paths:
            GeneratorThread(generator_path).start()

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

        self.stream.write(',' + json.dumps(self.blocks, ensure_ascii=False) +
                          '\n')
        self.stream.flush()

    @dbus.service.method('com.dubstepdish.i3dstatus',
                         in_signature='s', out_signature='s')
    def get_config(self, block_name):
        if block_name in self.config:
            return json.dumps(self.config[block_name], ensure_ascii=False)
        else:
            return '{}'

    def main(self):
        GLib.MainLoop().run()


def start():
    description = '''\
Another great statusline generator for i3wm.\
    '''

    epilog = '''\
available generators:
  clipboard         - show the contents of the clipboard
  clock             - show the current time
  disk              - show disk usage statistics
  ethernet          - show information about a network device
  focused-window    - show the currently focused window
  mediaplayer       - show artist/title of the currently playing track
  other-statuslines - show the output of another statusline
  scratchpad        - show what windows are in the i3 scratchpad

example usage:
  i3-dstatus focused-window ethernet clock
    '''

    parser = ArgumentParser(prog='i3-dstatus',
                            description=description,
                            epilog=epilog,
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('-c',
                        metavar='CONFIG',
                        dest='config',
                        nargs=1,
                        help='The location of your i3-dstatus config')

    parser.add_argument('generators',
                        metavar='Generators',
                        nargs=argparse.REMAINDER,
                        help='''Pass a list of generators as arguments to
                        appear in the statusline. See below for a list of
                        generators.''')

    args = parser.parse_args()

    # load the config
    config = {}

    try:
        config_path = args.config[0] if args.config else '~/.i3-dstatus.conf'
        with open(os.path.expanduser(config_path)) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        if args.config:
            message = 'Could not find config at {}\n'.format(args.config[0])
            parser.exit(status=1, message=message)
        else:
            pass

    try:
        service = DStatusService(args.generators, config=config)
        service.main()
    except Exception as e:
        with open('/tmp/i3-dstatus-error.log', 'a') as f:
            f.write("ERROR - " + str(datetime.datetime.now()) + "\n")
            f.write(traceback.format_exc())
            f.write('\n')

        sys.exit(1)

if __name__ == '__main__':
    start()
