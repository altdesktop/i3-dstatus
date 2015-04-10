from gi.repository import GLib
import os
from dbus.mainloop.glib import DBusGMainLoop
import yaml
import sys
from .service import DStatusService
from .procman import run_from_config

def start():
    DBusGMainLoop(set_as_default=True)

    try:
        with open("{}/.i3-dstatus.conf".format(os.path.expanduser('~'))) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = {}

    manager = DStatusService(config)
    run_from_config(config)

    sys.stdout.write('{"version":1}\n[\n[]\n')
    # sys.stdout.write('{"version":1, "click_events":true}\n[\n[]\n')
    sys.stdout.flush()

    main = GLib.MainLoop()
    main.run()
