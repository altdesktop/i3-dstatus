"""
Deals with the interface to i3bar.
"""

# TODO http://i3wm.org/docs/i3bar-protocol.html

# Make sure to register stop_signal and cont_signal as to not lock-up the whole
# process (which could fuck with d-bus) but instead just stop output to i3bar.

# Make sure to register for click events and handle them.
