i3-dstatus
==========

The ultimate DIY statusline generator for `i3wm <http://i3wm.org>`__.

About
-----

i3-dstatus is a statusline generator for i3 that you can use to display
system information you may be interested in. i3 comes with ``i3status``
which has many limitations. It has no plugin interface. It has no
support for events and relies on polling for all its information, which
makes it surprisingly heavy on resources. It has a weird config file
format that makes it difficult to configure.

Other projects have come along to make up for these weaknesses and many
of them do a great job. i3-dstatus is for users who want a more flexible
statusline that can be achieved from editing options in a configuration
file but without having to learn a complicated plugin api to create
custom statusline entries.

This is accomplished by allowing users to update the statusline through
interprocess communication using
`DBUS <http://www.freedesktop.org/wiki/Software/dbus/>`__. i3-dstatus
exposes a DBUS service that you can use to update the statusline simply
in pretty much any programming language and from any process (maybe even
in a cron!).

-  No configuration file is required
-  Update the statusline from multiple processes
-  Update the statusline from any language (even from the command line!)
-  No complicated plugin api to learn

Installing
----------

i3-dstatus is on `PyPI <https://pypi.python.org/pypi/i3-dstatus>`__.

::

    pip install i3-dstatus

Usage
-----

Use i3-dstatus as your status command in your bar block like so:

::

    bar {
        status_command i3-dstatus clock
    }

Pass the path of statusline generator scripts you want to run as
arguments to i3-dstatus. Passing a relative path will start the script
from the generators included with i3-dstatus from the generator path.
Using an absolute path or a ~/ home relative path will call the
appropriate path. The blocks will appear on i3bar in the order the
generators were given on the command line.

Configuration
~~~~~~~~~~~~~

Generator scripts will look for ``~/.i3-dstatus.conf`` for configuration
options. See ``i3-dstatus.conf`` in the repo for an example. The
configuration file should be a single YAML object. (More documentation
to come).

Updating the Statusline
-----------------------

The dbus service exposes the method ``show_block`` to update the
statusline. This method takes a dict of variants. Pass an object that
conforms to the `i3bar input
protocol <http://i3wm.org/docs/i3bar-protocol.html>`__ to show a block.

You can clear a block by omitting the "full\_text" member or setting it
to the empty string.

You can update the statusline from a python script. Just use a script
like this:

.. code:: python

    from dbus_next.aio import MessageBus
    from dbus_next import Variant

    bus = await MessageBus().connect()
    introspection = await bus.introspect('com.dubstepdish.i3dstatus', '/com/dubstepdish/i3dstatus')
    obj = bus.get_proxy_object('com.dubstepdish.i3dstatus', '/com/dubstepdish/i3dstatus')
    i3dstatus = obj.get_interface('com.dubstepdish.i3dstatus')
    await i3dstatus.call_show_block({
        'name': Variant('s', 'test'),
        'full_text': Variant('s', 'hello world')
    })

You can update the statusline from any language with dbus bindings
(which is pretty much all of them). You can even update the statusline
from the command line!

::

    dbus-send --session \
        --dest=com.dubstepdish.i3dstatus \
        --type=method_call \
        /com/dubstepdish/i3dstatus \
        com.dubstepdish.i3dstatus.show_block \
        dict:string:string:name,test,full_text,'hello world'

Contributing
------------

Please report bugs, request feature, write documentation, and add
generators to the ``i3dstatus/generators`` directory. i3-dstatus is a community
project so feedback is welcome!

License
-------

This work is available under a FreeBSD License (see LICENSE).

Copyright © 2014, Tony Crisci

All rights reserved.
