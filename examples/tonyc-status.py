#!/usr/bin/env python3

###
# This is my personal statusline generator.
# Deps:
# i3ipc-glib (https://github.com/acrisci/i3ipc-glib)
# Playerctl (https://github.com/acrisci/playerctl)
###

import dbus, time, sys
from gi.repository import i3ipc, Playerctl, GLib
from threading import Timer

bus = dbus.SessionBus()
player = Playerctl.Player(player_name='spotify')
i3 = i3ipc.Connection()

def show_block(block):
    service = bus.get_object('com.dubstepdish.i3dstatus', '/com/dubstepdish/i3dstatus')
    service_method = service.get_dbus_method('show_block', 'com.dubstepdish.i3dstatus')
    service_method(block)

def on_window_title(i3, e):
    block = { "name": "3:i3title", "full_text": e.container.props.name }
    show_block(block)

def on_metadata(player, e):
    block = { "name": "2:mediaplayer" }

    if 'xesam:artist' in e.keys() and 'xesam:title' in e.keys():
        block['full_text'] = '{} - {}'.format(e['xesam:artist'][0], e['xesam:title'])

    show_block(block)

def on_player_exit(player):
    # clear the block on exit
    show_block({"name": "2:mediaplayer"})

def on_tick():
    block = { "name": "1:clock", "full_text": time.strftime('%H:%M:%S') }
    show_block(block)
    Timer(1.0, on_tick).start()

player.on('metadata', on_metadata)
player.on('exit', on_player_exit)
i3.on('window::focus', on_window_title)
i3.on('window::title', on_window_title)
i3.on('ipc-shutdown', sys.exit)
Timer(1.0, on_tick).start()

main = GLib.MainLoop()
main.run()
