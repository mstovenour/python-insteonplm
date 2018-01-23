import logging
import binascii
from insteonplm.constants import *

class MessageFlags(object):
    def __init__(self, flags=0x00):
        self.log = logging.getLogger(__name__)
        #self._flags = self._normalize(flags)
        self._messageType = None
        self._extended = None
        self._hopsLeft = None
        self._hopsMax = None

        if flags is not None:
            self._set_properties(flags)
        
    def __repr__(self):
        return self.to_hex()

    def __str__(self):
        return self.to_hex()

    def __eq__(self, other):
        if hasattr(other, 'messageType'):
            messageTypeIsEqual = False
            if self.messageType == None or other.messageType == None:
                messageTypeIsEqual = True
            else:
                messageTypeIsEqual = (self.messageType == other.messageType)
            extendedIsEqual = False
            if self.extended == None or other.extended == None:
                extendedIsEqual = True
            else:
                extendedIsEqual = (self.extended == other.extended)
            return messageTypeIsEqual and extendedIsEqual
        else:
            return False

    def __ne__(self, other):
        if self._flags == None or other == None:
            return False
        return self._flags == other

    @classmethod
    def get_properties(cls):
        property_names=[p for p in dir(cls) if isinstance(getattr(cls,p),property)]
        return property_names

    @property
    def isBroadcast(self):
        return (self._messageType & MESSAGE_TYPE_BROADCAST_MESSAGE) == MESSAGE_TYPE_BROADCAST_MESSAGE

    @property
    def isDirect(self):
        direct = (self._messageType  == 0x00)
        if self.isDirectACK or self.isDirectNAK:
            direct = True
        return direct

    @property
    def isDirectACK(self):
        return (self._messageType == MESSAGE_TYPE_DIRECT_MESSAGE_ACK)

    @property
    def isDirectNAK(self):
        return (self._messageType == MESSAGE_TYPE_DIRECT_MESSAGE_NAK)

    @property
    def isAllLinkBroadcast(self):
        return (self._messageType == MESSAGE_TYPE_ALL_LINK_BROADCAST)

    @property
    def isAllLinkCleanup(self):
        return (self._messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP)

    @property
    def isAllLinkCleanupACK(self):
        return (self._messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK)

    @property
    def isAllLinkCleanupNAK(self):
        return (self._messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK)

    @property
    def isExtended(self):
        return self._extended == 1

    @property
    def hopsLeft(self):
        return self._hopsLeft

    @property
    def maxHops(self):
        return self._hopsMax

    @maxHops.setter
    def maxHops(self, val):
        self._maxhops = val

    @property
    def messageType(self):
        return self._messageType

    @property
    def extended(self):
        return self._extended

    @classmethod
    def create(cls, messageType, extended, hopsleft=None, maxhops=None):
        """Create message flags.
        messageType: integter 0 to 7:
                        MESSAGE_TYPE_DIRECT_MESSAGE = 0
                        MESSAGE_TYPE_DIRECT_MESSAGE_ACK = 1
                        MESSAGE_TYPE_ALL_LINK_CLEANUP = 2
                        MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK = 3
                        MESSAGE_TYPE_BROADCAST_MESSAGE = 4
                        MESSAGE_TYPE_DIRECT_MESSAGE_NAK = 5 
                        MESSAGE_TYPE_ALL_LINK_BROADCAST = 6 
                        MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK = 7   
        extended: 1 for extended, 0 for standard or None
        hopsleft: int  0 - 3
        maxhops:  int  0 - 3
        """
        flags = MessageFlags(None)
        flags._messageType = messageType
        flags._extended = 1 if extended else 0
        flags._hopsLeft = hopsleft
        flags._hopsMax = maxhops
        return flags

    def to_byte(self):
        flagByte = 0x00
        messageType = 0 if self._messageType is None else (self._messageType << 5)
        extendedBit = 0 if self._extended is None else self._extended << 4
        hopsMax = 0 if self._hopsMax is None else self._hopsMax
        hopsLeft = 0 if self._hopsLeft is None else (self._hopsLeft << 2)
        flagByte = flagByte | messageType | extendedBit | hopsLeft | hopsMax
        return bytes([flagByte])

    def to_hex(self):
        return binascii.hexlify(self.to_byte()).decode()

    def _normalize(self, flags):
        """Take any format of flags and turn it into a hex string."""
        if isinstance(flags, MessageFlags):
            return flags.to_byte()
        if isinstance(flags, bytearray):
            return binascii.hexlify(flags)
        if isinstance(flags, int):
            return flags
        if isinstance(flags, bytes):
            return binascii.hexlify(flags)
        if isinstance(flags, str):
            flags = flags[0:2]
            return binascii.unhexlify(flags.lower())
        if flags is None:
            return None
        else:
            self.log.warning('MessageFlags class init with unknown type %s: %r',
                             type(flags), flags)
            return None

    def _set_properties(self, flags):
        flagByte = self._normalize(flags)

        self._messageType = (flagByte & 0xe0) >> 5
        self._extended = (flagByte & MESSAGE_FLAG_EXTENDED_0X10) >> 4
        self._hopsLeft = (flagByte & 0x0c) >> 2
        self._hopsMax = flagByte & 0x03
