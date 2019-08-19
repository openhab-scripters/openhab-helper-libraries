******
Lights
******

Eos sends commands to *Lights* based on a *Scene*. In order for Eos to control
an item it needs to be of a certain item type (see light types below) and have
a metadata namespace called ``eos`` with a value of ``True``. The easiest way
to enable items to be Eos Lights is using the :doc:`Editor`.

Types
=====

    Eos classifies different item types into different types of lights in order
    to determine what scene types and states are valid.

*Switch*
--------

        As its name suggests, ``Switch`` items are treated as *Switch* type
        lights. They can be used with *Fixed* and *Threshold* type scenes and
        only accept ``"ON"`` or ``"OFF"`` as a value for any state settings.

*Dimmer*
--------

        A ``Dimmer`` or ``Number`` item will be treated as *Dimmer* type light.
        They can be used with *Fixed*, *Threshold*, or *Scaled* type scenes and
        only accept numbers for state settings.

*Color*
-------

        A ``Color`` item will be treated as a *Color* type light. They can be
        used with *Fixed*, *Threshold*, and *Scaled* type scenes as well.
        Acceptable states are a single number or a list of 3 numbers
        representing the HSB values. If the state setting is a single number,
        it will be taken to mean the Brightness in the HSB value and the
        current Hue and Saturation will be used when sending the command. If
        the setting is a list of 3 numbers, they will be used as the Hue,
        Saturation, and Brightness when sending a command. When using HSB
        states with *Scaled* type scenes it is possible to have the Hue wrap
        around, but you must specify the range in a linear manner. It is also
        possible to specify Saturation and Brightness settings beyond the range
        of 0-100, these will be constrained to within the 0-100 range before
        sending the command.

        As an example, this is the scene configuration I use for a simulated
        sun-lamp in our bedroom. With ``level_source`` set to 100 the command
        sent is ``20,65,50``, and at 0 the command is ``349,100,0`` (Hue is
        0-359).

        .. code-block::

            "sunlamp": {
                "level_high": 100,
                "level_low": 0,
                "state_high": [20, 65, 50],
                "state_low": [-10, 115, 0]
            }
