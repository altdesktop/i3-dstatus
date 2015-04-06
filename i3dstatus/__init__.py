from gi.repository import GLib
import sys
import os
import yaml
import asyncio
from dbus.mainloop.glib import DBusGMainLoop
from .service import BlockManager
from .barproto import BarManager, InputParser
from .gbulb import gbulb  # Uggggggggggggggggggggggggggggghhhhhhhhhhhhhhhhhhhh


def start():
    """
    Orchestrates the start of everything, injects dependencies, sets up event
    loops, and all the other things that need to happen
    """
    # Remap some stuff so we don't corrupt pipes
    i3bar_blocks, sys.stdout = sys.stdout, sys.stderr
    i3bar_input, sys.stdin = sys.stdin, None

    DBusGMainLoop(set_as_default=True)
    #asyncio.set_event_loop_policy(gbulb.GLibEventLoopPolicy())

    try:
        with open("{}/.i3-dstatus.conf".format(os.path.expanduser('~'))) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {}

    manager = BlockManager(config)

    blockman = BarManager(i3bar_blocks, manager, config)
    parser = InputParser(i3bar_input, manager, config)

    # FIXME: Feed blockman, parser coroutines to event loop


    main = GLib.MainLoop()
    main.run()
    # Do this instead when gbulb is better
    #asyncio.get_event_loop().run_forever()
