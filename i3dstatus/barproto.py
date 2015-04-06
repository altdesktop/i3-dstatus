"""
Deals with the interface to i3bar.
"""
import asyncio
import ijson
import signal
import json

# TODO http://i3wm.org/docs/i3bar-protocol.html

STOP_SIGNAL = signal.SIGUSR1
CONT_SIGNAL = signal.SIGUSR2

# Make sure to register stop_signal and cont_signal as to not lock-up the whole
# process (which could fuck with d-bus) but instead just stop output to i3bar.

# Make sure to register for click events and handle them.


def BarManager(stream, blocks, config):
    # Set signal handlers
    stream.write(json.dumps({
        "version": 1,
        "stop_signal": STOP_SIGNAL,
        "cont_signal": CONT_SIGNAL,
        "click_events": True
    }))
    stream.write('\n[')
    stream.flush()
