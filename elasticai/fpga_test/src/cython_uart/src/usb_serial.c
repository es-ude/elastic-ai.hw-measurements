//
// Created by silas on 9/9/24.
//

#include "usb_serial.h"

#include <stdlib.h>

struct usb_serial serial;

void init_serial(usb_serial *serial,char com_name[], int baud_rate, int buffer_bytesize)
{
    /* Open serial device: O_RWDR(Read and Write), O_NOCTTY(Port never gets control of Process), O_NDELAY(Use non-blocking I/O)  */
    serial->fd = open(com_name, O_RDWR | O_NOCTTY | O_NDELAY);
    if (serial->fd == -1)
    {
        perror("Failed to open serial port");
    }
    if (!isatty(serial->fd))
    {
        perror("Serial port is not a tty");
    }

    /* Set up serial ports*/
    serial->options.c_cflag = B115200 | CS8 | CLOCAL | CREAD;
    serial->options.c_iflag = IGNPAR;
    serial->options.c_oflag = 0;
    serial->options.c_lflag = 0;

    /* Apply the settings */
    tcflush(serial->fd, TCIFLUSH);
    tcsetattr(serial->fd, TCSANOW, &serial->options);
}

void close_serial(usb_serial *serial)
{
    close(serial->fd);
}

void write_serial(usb_serial *serial)
{
    serial->len = write(serial->fd, serial->data, serial->len);
    tcdrain(serial->fd);
};

void load_data(usb_serial *serial, char *byte_buffer, int len)
{
    memset(serial->data, 0, 255);
    for (int i = 0; i < len; i++)
    {
        serial->data[i] = byte_buffer[i];
    }
}

void write_wofb(usb_serial *serial, char *byte_buffer, int len)
{
    load_data(serial, byte_buffer, len);
    serial->len = len;
    write_serial(serial);
};

void write_wfb(usb_serial *serial, char *byte_buffer, int len, char *out_buffer)
{
    load_data(serial, byte_buffer, len);
    serial->len = len;
    write_serial(serial);

    serial->len = write(serial->fd, out_buffer, len);
};

void read_serial(usb_serial *serial, char *out_buffer, int nbytes)
{
    serial->len = read(serial->fd, out_buffer, nbytes);
};