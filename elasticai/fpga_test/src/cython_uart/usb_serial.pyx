cimport usb_serial as usb

# Create a Python-accessible wrapper class around usb_serial
cdef class PyUsbSerial:
    cdef usb.usb_serial serial  # Define a usb_serial struct internally

    def init_serial(self, com_name, int baud_rate, int buffer_bytesize):
        # Initialize the serial port on object creation
        init_serial(&self.serial, com_name, baud_rate, buffer_bytesize)

    def close_serial(self):
        # Close the serial port when the object is destroyed
        close_serial(&self.serial)

    def write_serial(self):
        # Write data to the serial port
        write_serial(&self.serial)

    def load_data(self, byte_buffer, length):
        # Not needed in Python
        pass

    def write_wofb(self, byte_buffer):
        # Write without feedback
        cdef int length = len(byte_buffer)
        write_wofb(&self.serial, byte_buffer, length)

    def write_wfb(self, byte_buffer):
        # Write with feedback
        cdef int length = len(byte_buffer)
        cdef char[255] out_buffer
        write_wfb(&self.serial, byte_buffer, length, out_buffer)
        return out_buffer

    def read_serial(self, int nbytes):
        # Read from the serial port
        cdef char[255] out_buffer
        read_serial(&self.serial, out_buffer, nbytes)
        return out_buffer[:nbytes]  # Return the read data as a Python string
