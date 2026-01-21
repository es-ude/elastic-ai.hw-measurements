import sys
import serial
from glob import glob


def scan_available_serial_ports() -> list:
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class HandlerUSB:
    __BYTES_HEAD: int = 1
    __BYTES_DATA: int = 2

    """Class for handling serial ports in Python"""
    def __init__(self, com_name: str, baud: int, buffer_bytesize: int):
        """Init. of the device with name and baudrate of the device"""
        self.SerialName = com_name
        self.SerialBaud = baud
        self.SerialParity = 0

        self.packet_size = buffer_bytesize
        self.device = serial.Serial()
        self.device_init = False
        self.__setup_usb()

    @property
    def com_port_active(self):
        """Boolean for checking if serial communication is open and used"""
        return self.device.is_open

    def redefine_bytesize(self, bytes_head: int, bytes_data: int) -> None:
        """Redefine bytes for transmitting head information and data"""
        self.__BYTES_HEAD = bytes_head
        self.__BYTES_DATA = bytes_data

    def __setup_usb(self):
        """Setup USB device"""
        # Setting the parity
        parity = str()
        if self.SerialParity == 0:
            parity = serial.PARITY_NONE
        if self.SerialParity == 1:
            parity = serial.PARITY_EVEN
        if self.SerialParity == 2:
            parity = serial.PARITY_ODD

        # Setting the serial port
        self.device = serial.Serial(
            port=self.SerialName,
            baudrate=self.SerialBaud,
            parity=parity,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            inter_byte_timeout=0.5
        )
        self.device_init = True

    def open(self):
        """Starting a connection to device"""
        if self.device.is_open:
            self.device.close()
        self.device.open()

    def close(self):
        """Closing a connection to device"""
        self.device.close()

    def write_wofb(self, data: bytes) -> None:
        """Write content to device without feedback"""
        self.device.write(data)

    def write_wfb(self, data: bytes):
        """Write all information to device (specific bytes)"""
        self.device.write(data)
        dev_out = self.device.read(len(data))
        return dev_out

    def write_wfb_lf(self, data: bytes):
        """Write all information to device (unlimited bytes until LF)"""
        self.device.write(data)
        dev_out = self.device.read_until()
        return dev_out

    def write_wfb_hex(self, head: int, data: int) -> bytes:
        """Write content to FPGA/MCU for specific custom-made task"""
        transmit_byte = head.to_bytes(self.__BYTES_HEAD, 'little')
        transmit_byte += data.to_bytes(self.__BYTES_DATA, 'big')
        self.device.write(transmit_byte)
        out = self.device.read(len(transmit_byte))
        return out

    def read(self, no_bytes: int):
        """Read content from device"""
        return self.device.read(no_bytes)
