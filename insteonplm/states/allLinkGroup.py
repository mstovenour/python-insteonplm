"""Dimmable light states."""
import logging

from insteonplm.constants import (
    COMMAND_LIGHT_ON_0X11_NONE,
    COMMAND_LIGHT_ON_FAST_0X12_NONE,
    COMMAND_LIGHT_OFF_0X13_0X00,
    COMMAND_LIGHT_OFF_FAST_0X14_0X00,
    COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00,
    COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00,
    COMMAND_LIGHT_START_MANUAL_CHANGEDOWN_0X17_0X00,
    COMMAND_LIGHT_START_MANUAL_CHANGEUP_0X17_0X01,
    COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
    COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00,
    COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
    MESSAGE_TYPE_ALL_LINK_CLEANUP)
from insteonplm.messages.standardSend import StandardSend
from insteonplm.messages.standardReceive import StandardReceive
from insteonplm.messages.messageFlags import MessageFlags
from insteonplm.states import State

_LOGGER = logging.getLogger(__name__)


class AllLinkGroup(State):
    """Device state representing an IM ALL-Link Group.

    Available methods are:
    on()
    off()
    brighten()
    dim()
    """

    def __init__(self, address, statename, group, send_message_method,
                 message_callbacks, defaultvalue, ALL_Link_cleanup_method):
        """Init the State Class."""
        super().__init__(address, statename, group, send_message_method,
                         message_callbacks, defaultvalue)

        self._updatemethod = None
        self._ALL_Link_cleanup_method = ALL_Link_cleanup_method
        self._register_messages()

    # pylint: disable=too-many-locals
    def _register_messages(self):
        _LOGGER.debug('Registering callbacks for allLinkGroup PLM: %s '
                      'Group: 0x%x', self._address.human, self._group)
        template_on_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_0X11_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_on_fast_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_ON_FAST_0X12_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_off_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_0X13_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_off_fast_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_OFF_FAST_0X14_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_brighten_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_dim_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_start_down_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_START_MANUAL_CHANGEDOWN_0X17_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_start_up_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_START_MANUAL_CHANGEUP_0X17_0X01,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_manual_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_STOP_MANUAL_CHANGE_0X18_0X00,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)
        template_instant_cleanup = StandardReceive.template(
            commandtuple=COMMAND_LIGHT_INSTANT_CHANGE_0X21_NONE,
            address=self._address,
            flags=MessageFlags.template(MESSAGE_TYPE_ALL_LINK_CLEANUP, None),
            cmd2=self._group)

        self._message_callbacks.add(template_on_cleanup,
                                    self._on_message_received)
        self._message_callbacks.add(template_on_fast_cleanup,
                                    self._on_message_received)
        self._message_callbacks.add(template_off_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_off_fast_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_brighten_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_dim_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_start_down_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_start_up_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_manual_cleanup,
                                    self._manual_change_received)
        self._message_callbacks.add(template_instant_cleanup,
                                    self._manual_change_received)

    def on(self):
        """Braodcast All-Link Recall for this state's group."""
        self._ALL_Link_cleanup_method(self.group, COMMAND_LIGHT_ON_0X11_NONE)
        self._update_subscribers(0xff)

    def off(self):
        """Braodcast All-Link off for this state's group."""
        self._ALL_Link_cleanup_method(self.group, COMMAND_LIGHT_OFF_0X13_0X00)
        self._update_subscribers(0x00)

    def brighten(self):
        """Braodcast All-Link Brighten for this state's group."""
        self._ALL_Link_cleanup_method(
            self.group,
            COMMAND_LIGHT_BRIGHTEN_ONE_STEP_0X15_0X00)

    def dim(self):
        """Braodcast All-Link Dim for this state's group."""
        self._ALL_Link_cleanup_method(self.group,
                                      COMMAND_LIGHT_DIM_ONE_STEP_0X16_0X00)

    def handle_ALL_Link_cleanup(self, msg, recall_level):
        """Update the state's subscribers with the new level or fixed level."""
        level = 255
        if msg.cmd1 == COMMAND_LIGHT_ON_0X11_NONE.get('cmd1', None):
            level = recall_level
        elif msg.cmd1 == COMMAND_LIGHT_ON_FAST_0X12_NONE.get('cmd1', None):
            level = 255
        elif msg.cmd1 == COMMAND_LIGHT_OFF_0X13_0X00.get('cmd1', None):
            level = 0
        elif msg.cmd1 == COMMAND_LIGHT_OFF_FAST_0X14_0X00.get('cmd1', None):
            level = 0
        else:
            _LOGGER.error('AlL-Link_cleanup device %s:0x%02x command '
                          'unknown 0x%02x', msg.address.human, self.group,
                          msg.cmd1)

        _LOGGER.debug('AlL-Link_cleanup device %s:0x%02x updating '
                      'subscribers with level 0x%x from command 0x%02x',
                      self.address.human, self.group, level, msg.cmd1)

        self._update_subscribers(level)

    # pylint: disable=unused-argument
    def _on_message_received(self, msg):
        _LOGGER.debug('AlL-Link_cleanup received device %s:0x%x updating '
                      'subscribers with level 0x%x from command 0x%x',
                      self.address.human, self.group, 0xff, msg.cmd1)
        self._update_subscribers(0xff)

    # pylint: disable=unused-argument
    def _off_message_received(self, msg):
        _LOGGER.debug('AlL-Link_cleanup received device %s:0x%x updating '
                      'subscribers with level 0x%x from command 0x%x',
                      self.address.human, self.group, 0x00, msg.cmd1)
        self._update_subscribers(0x00)

    # pylint: disable=unused-argument
    def _manual_change_received(self, msg):
        self._send_status_request()

    def _send_status_request(self):
        """Send a status request message to the device."""
        status_command = StandardSend(self._address,
                                      COMMAND_LIGHT_STATUS_REQUEST_0X19_0X00)
        self._send_method(status_command,
                          self._status_message_received)

    def _status_message_received(self, msg):
        self._update_subscribers(msg.cmd2)
