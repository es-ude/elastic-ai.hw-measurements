import serial
from serial.tools import list_ports


def scan_available_serial_ports() -> list:
    """Returning the COM Port name of the addressable devices
    :return: List with COM port name
    """
    available_coms = list_ports.comports()
    list_right_com = [port.device for port in available_coms]
    if len(list_right_com) == 0:
        errmsg = '\n'.join([f"{port.usb_description()} {port.device} {port.usb_info()}" for port in available_coms])
        raise ConnectionError(f"No COM Port with right USB found:\n{errmsg}")
    return list_right_com


class HandlerUSB:
    """Class for handling serial ports in Python"""
    __BYTES_HEAD: int = 1
    __BYTES_DATA: int = 2

    def __init__(self, com_name: str, baud: int, buffer_bytesize: int) -> None:
        """Init. of the device with name and baudrate of the device
        :param com_name:        String with name of the COM port
        :param baud:            Integer with Baud rate of the device
        :param buffer_bytesize: Integer with buffer size
        :return: None
        """
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
            inter_byte_timeout=0.1
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
        transmit_byte = head.to_bytes(self.__BYTES_HEAD, byteorder='big')
        transmit_byte += data.to_bytes(self.__BYTES_DATA, byteorder='big')
        self.device.write(transmit_byte)
        out = self.device.read(len(transmit_byte))
        return out

    def read(self, no_bytes: int):
        """Read content from device"""
        return self.device.read(no_bytes)
