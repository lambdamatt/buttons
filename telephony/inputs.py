"""
Classes to simplify mapping GPIO pins and values to JoystickXL inputs and states.

This module provides a set of classes to aid in configuring GPIO pins and convert
their raw states to values that are usable by JoystickXL.
"""

# These typing imports help during development in vscode but fail in CircuitPython
try:
    from typing import Union
except ImportError:
    pass

# These are all CircuitPython built-ins
try:
    from analogio import AnalogIn  # type: ignore
    from digitalio import DigitalInOut, Direction, Pull  # type: ignore
    from microcontroller import Pin  # type: ignore
except ImportError:
    print("*** WARNING: CircuitPython built-in modules could not be imported. ***")


class VirtualInput:
    """Provide an object with a .value property to represent a remote input."""

    def __init__(self, value: Union[bool, int]) -> None:
        """
        Provide an object with a ``.value`` property to represent a remote input.

        :param value: Sets the initial ``.value`` property (Should be ``True`` for
            active-low buttons, ``32768`` for idle/centered axes).
        :type value: bool or int
        """
        self.value = value




class Button:
    """Data source storage and value processing for a button input."""

    @property
    def value(self) -> bool:
        """
        Get the current, fully processed value of this button input.

        .. warning::

            Accessing this property also updates the ``.was_pressed`` and
            ``.was_released`` logic, which means accessing ``.value`` directly anywhere
            other than in a call to ``Joystick.update_button()`` can make those
            properties unreliable.  If you need to read the current state of a button
            anywhere else in your input processing loop, you should be using
            ``.is_pressed`` or ``.is_released`` rather than ``.value``.

        :return: ``True`` if pressed, ``False`` if released or bypassed.
        :rtype: bool
        """
        self._last_state = self._state
        self._state = self._source.value != self._active_low

        return self._state and not self.bypass

    @property
    def is_pressed(self) -> bool:
        """
        Determine if this button is currently in the ``pressed`` state.

        :return: ``True`` if button is pressed, otherwise ``False``
        :rtype: bool
        """
        return self._source.value != self._active_low

    @property
    def is_released(self) -> bool:
        """
        Determine if this button is currently in the ``released`` state.

        :return: ``True`` if button is released, otherwise ``False``.
        :rtype: bool
        """
        return self._source.value == self._active_low

    @property
    def was_pressed(self) -> bool:
        """
        Determine if this button was just pressed.

        Specifically, if the button state changed from ``released`` to ``pressed``
        between the last two reads of ``Button.value``.

        .. warning::

            This property only works reliably when ``Button.value`` is accessed *once
            per iteration of your input processing loop*.  If your code uses the
            built-in ``Joystick.add_input()`` method and associated input lists along
            with a single call to ``Joystick.update()``, you should be fine.

        :return: ``True`` if the button was just pressed, ``False`` otherwise.
        :rtype: bool
        """
        return self._state is True and self._last_state is False

    @property
    def was_released(self) -> bool:
        """
        Determine if this button was just released.

        Specifically, if the button state changed from ``pressed`` to ``released``
        between the last two reads of ``Button.value``.

        .. warning::

            This property only works reliably when ``Button.value`` is accessed *once
            per iteration of your input processing loop*.  If your code uses the
            built-in ``Joystick.add_input()`` method and associated input lists along
            with a single call to ``Joystick.update()``, you should be fine.

        :return: ``True`` if the button was just released, ``False`` otherwise.
        :rtype: bool
        """
        return self._state is False and self._last_state is True

    @property
    def source_value(self) -> bool:
        """
        Get the raw source input value.

        *(For VirtualInput sources, this property can also be set.)*

        :return: ``True`` or ``False``
        :rtype: bool
        """
        return self._source.value is True

    @source_value.setter
    def source_value(self, value: bool) -> None:
        """Set the raw source value for a VirtualInput button source."""
        if not isinstance(self._source, VirtualInput):
            raise TypeError("Only VirtualInput source values can be set manually.")
        self._source.value = value

    @property
    def active_low(self) -> bool:
        """
        Get the input configuration state of the button.

        :return: ``True`` if the button is active low, ``False`` otherwise.
        :rtype: bool
        """
        return self._active_low

    def __init__(
        self,
        source=None,
        active_low: bool = True,
        bypass: bool = False,
    ) -> None:
        """
        Provide data source storage and value processing for a button input.

        :param source: CircuitPython pin identifier (i.e. ``board.D2``), or any object
            with a boolean ``.value`` attribute.  (Defaults to ``None``, which will
            create a ``VirtualInput`` source instead.)
        :type source: Any, optional
        :param active_low: Set to ``True`` if the input pin is active low
            (reads ``False`` when the button is pressed), otherwise set to ``False``.
            (defaults to ``True``)
        :type active_low: bool, optional
        :param bypass: Set to ``True`` to make the button always appear ``released``
            in USB HID reports back to the host device.  (Defaults to ``False``)
        :type bypass: bool, optional
        """
        self._source = Button._initialize_source(source, active_low)
        self._active_low = active_low
        self._state = False
        self._last_state = False

        self.bypass = bypass
        """Set to ``True`` to make the button always appear ``released``."""

    @staticmethod
    def _initialize_source(source, active_low: bool):
        """
        Configure a source as an on-board pin, off-board input or VirtualInput.

        :param source: CircuitPython pin identifier (i.e. ``board.D2``), any object
            with a boolean ``.value`` attribute or a ``VirtualInput`` object.
        :type source: Any
        :param active_low: Set to ``True`` if the input pin is active low (reads
            ``False`` when the button is pressed), otherwise set to ``False``.
        :type active_low: bool
        :return: A fully configured digital source pin or virtual input.
        :rtype: Any
        """
        if source is None:
            return VirtualInput(value=active_low)
        elif isinstance(source, Pin):
            source_gpio = DigitalInOut(source)
            source_gpio.direction = Direction.INPUT
            if active_low:
                source_gpio.pull = Pull.UP
            else:
                source_gpio.pull = Pull.DOWN
            return source_gpio
        elif hasattr(source, "value") and isinstance(source.value, bool):
            return source
        else:
            raise TypeError("Incompatible button source specified.")



    """Data source storage and value conversion for hat switch inputs."""

    U = 0
    """Alias for the ``UP`` switch position."""

    UR = 1
    """Alias for the ``UP + RIGHT`` switch position."""

    R = 2
    """Alias for the ``RIGHT`` switch position."""

    DR = 3
    """Alias for the ``DOWN + RIGHT`` switch position."""

    D = 4
    """Alias for the ``DOWN`` switch position."""

    DL = 5
    """Alias for the ``DOWN + LEFT`` switch position."""

    L = 6
    """Alias for the ``LEFT`` switch position."""

    UL = 7
    """Alias for the ``UP + LEFT`` switch position."""

    IDLE = 8
    """Alias for the ``IDLE`` switch position."""

    @property
    def value(self) -> int:
        """
        Get the current, fully processed value of this hat switch.

        :return: Current position value (always ``IDLE`` if bypassed), as follows:

                * ``0`` = UP
                * ``1`` = UP + RIGHT
                * ``2`` = RIGHT
                * ``3`` = DOWN + RIGHT
                * ``4`` = DOWN
                * ``5`` = DOWN + LEFT
                * ``6`` = LEFT
                * ``7`` = UP + LEFT
                * ``8`` = IDLE

        :rtype: int
        """
        new_value = self._update()

        if self.bypass:
            return Hat.IDLE
        else:
            return new_value

    @property
    def packed_source_values(self) -> int:
        """
        Get the current packed value of all four button input source values.

        :return: Packed button input source values in one byte (``0000RLDU``).
        :rtype: int
        """
        pv = self.up.source_value
        pv |= self.down.source_value << 1
        pv |= self.left.source_value << 2
        pv |= self.right.source_value << 3
        return pv

    @property
    def active_low(self) -> bool:
        """
        Get the input configuration state of the hat switch buttons.

        :return: ``True`` if the buttons are active low, ``False`` otherwise.
        :rtype: bool
        """
        return self._active_low

    def __init__(
        self,
        up=None,
        down=None,
        left=None,
        right=None,
        active_low: bool = True,
        bypass: bool = False,
    ) -> None:
        """
        Provide data source storage and value processing for a hat switch input.

        :param up: CircuitPython pin identifier (i.e. ``board.D2``) or any object with
            a boolean ``.value`` attribute.  (Defaults to ``None``, which will create
            a ``VirtualInput`` source instead.)
        :type up: Any, optional
        :param down: CircuitPython pin identifier (i.e. ``board.D2``) or any object with
            a boolean ``.value`` attribute.  (Defaults to ``None``, which will create
            a ``VirtualInput`` source instead.)
        :type down: Any, optional
        :param left: CircuitPython pin identifier (i.e. ``board.D2``) or any object with
            a boolean ``.value`` attribute.  (Defaults to ``None``, which will create
            a ``VirtualInput`` source instead.)
        :type left: Any, optional
        :param right: CircuitPython pin identifier (i.e. ``board.D2``) or any object
            with a boolean ``.value`` attribute.  (Defaults to ``None``, which will
            create a ``VirtualInput`` source instead.)
        :type right: Any, optional
        :param active_low: Set to ``True`` if the input pins are active low
            (read ``False`` when buttons are pressed), otherwise set to ``False``.
            (defaults to ``True``)
        :type active_low: bool, optional
        :param bypass: Set to ``True`` to make the hat switch always appear ``idle``
            in USB HID reports back to the host device.  (Defaults to ``False``)
        :type bypass: bool, optional
        """
        self.up = Button(up, active_low)
        """Button object associated with the ``up`` input."""

        self.down = Button(down, active_low)
        """Button object associated with the ``down`` input."""

        self.left = Button(left, active_low)
        """Button object associated with the ``left`` input."""

        self.right = Button(right, active_low)
        """Button object associated with the ``right`` input."""

        self._active_low = active_low
        self._value = Hat.IDLE

        self.bypass = bypass
        """Set to ``True`` to make the hat switch always appear ``idle``."""

        self._update()

    def unpack_source_values(self, source_values: int) -> None:
        """
        Unpack all four source values from a single packed integer.

        :param source_values: Packed button source values in one byte (``0000RLDU``).
        :type source_values: int

        .. note::

            This operation is only valid for hat switches composed of
            ``VirtualInput`` objects.
        """
        self.up.source_value = (source_values & 0x01) == 0x01
        self.down.source_value = ((source_values >> 1) & 0x01) == 0x01
        self.left.source_value = ((source_values >> 2) & 0x01) == 0x01
        self.right.source_value = ((source_values >> 3) & 0x01) == 0x01

    def _update(self) -> int:
        """Update the angular position value based on discrete input states."""
        U = self.up.value
        D = self.down.value
        L = self.left.value
        R = self.right.value

        if U and R:
            self._value = Hat.UR
        elif U and L:
            self._value = Hat.UL
        elif U:
            self._value = Hat.U
        elif D and R:
            self._value = Hat.DR
        elif D and L:
            self._value = Hat.DL
        elif D:
            self._value = Hat.D
        elif L:
            self._value = Hat.L
        elif R:
            self._value = Hat.R
        else:
            self._value = Hat.IDLE
        return self._value
