cdef extern from "termios.h":
    struct termios:
        pass

cdef extern from "src/src_usb_serial.h":
    ctypedef struct usb_serial:
        int fd
        int len
        char data[255]
        termios options

    void init_serial(usb_serial *serial, char com_name[], int baud_rate, int buffer_bytesize)
    void close_serial(usb_serial *serial)
    void write_serial(usb_serial *serial)
    void load_data(usb_serial *serial, char *byte_buffer, int len)
    void write_wofb(usb_serial *serial, char *byte_buffer, int len)
    void write_wfb(usb_serial *serial, char *byte_buffer, int len, char *out_buffer)
    void read_serial(usb_serial *serial, char *out_buffer, int nbytes)
