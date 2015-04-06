from gi.repository import GLib
import sys
import os
import yaml
import asyncio
from dbus.mainloop.glib import DBusGMainLoop
from .service import BlockManager
from .gbulb import gbulb  # Uggggggggggggggggggggggggggggghhhhhhhhhhhhhhhhhhhh


def start():
    """
    Orchestrates the start of everything, injects dependencies, sets up event
    loops, and all the other things that need to happen
    """
    DBusGMainLoop(set_as_default=True)
    asyncio.set_event_loop_policy(gbulb.GLibEventLoopPolicy())

    try:
        with open("{}/.i3-dstatus.conf".format(os.path.expanduser('~'))) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {}

    manager = BlockManager(config)

    sys.stdout.write('{"version":1}\n[\n[]\n')
    # sys.stdout.write('{"version":1, "click_events":true}\n[\n[]\n')
    sys.stdout.flush()

    main = GLib.MainLoop()
    main.run()

    # Do this when gbulb is better
    #asyncio.get_event_loop().run_forever()
