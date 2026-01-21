//
// Created by silas on 9/9/24.
//

#ifndef USB_SERIAL_H
#define USB_SERIAL_H

#include <stdio.h>
#include <string.h>
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>

typedef struct usb_serial
{
    int fd, len;
    char data[255];
    struct termios options;
} usb_serial;

void init_serial(usb_serial *serial,char com_name[], int baud_rate, int buffer_bytesize);

void close_serial(usb_serial *serial);

void write_serial(usb_serial *serial);

void load_data(usb_serial *serial, char *byte_buffer, int len);

void write_wofb(usb_serial *serial, char *byte_buffer, int len);

void write_wfb(usb_serial *serial, char *byte_buffer, int len, char *out_buffer);

void write_wfb_lf(usb_serial *serial, char *byte_buffer, int len, char *out_buffer);

void write_wfb_hex(usb_serial *serial, int head, char *byte_buffer, int len, char *out_buffer);

void read_serial(usb_serial *serial, char *out_buffer, int nbytes);

#endif //USB_SERIAL_H
