/*
 * linux_io.c - functions to communicate with the serial port under linux.
 *
 * Created on: Feb 22, 2011
 * Author: John Kloosterman
 */

#include "linux_io.h"
#include "constants.h"

// coax usleep out of the header, enable CMSPAR
#define _BSD_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>

/*
 * Several functions from dexread use this to define an error.
 */
// #define ESC             27      /* ESCAPE character */

/* Baud rate is 9600. */
#define BAUDRATE B9600

int fd;			// the filedescriptor for DEVICE
struct termios oldtio;	// the settings of DEVICE before we run.

void delay (int msec) {
	if (usleep(msec * 1000))
		perror("delay():");
}

void flush_serial() {
    tcflush(fd, TCIFLUSH);
}

/* Send a byte on the serial port. */
int serial_send(char x) {
	delay(8);

	if (write(fd, &x, 1) == -1)
		perror("serial_send(): write(): ");

	return 0;
}

/* Read from serial port without waiting. */
int wait4_for_serial(unsigned char *ch) {
	ssize_t count;

	count = read(fd, ch, 1);
	if (count == 0) {
		*ch = ESC;
		return 0;
	}
	else if (count == -1) {
		perror("wait4_for_serial(): read(): ");
		*ch = ESC;
		return 0;
	}
	else {
		return 1;
	}
}

/* Keep listening for a response from the serial port. */
char wait_for_serial(int time) {
	ssize_t count;
	int i = 0;
	char ret = 0;

	do {
		i++;
		count = read(fd, &ret, 1);
		delay(5);
	} while ((count == 0) && i < (time * 2));

	if (count == 0)
		return ESC;
	else if (count == -1) {
		perror("wait_for_serial(): read(): ");
		return ESC;
	}

	return ret;
}

/* Initialize the serial port with the required settings. */
void init_serial(char *device)
{
	struct termios newtio;

	fd = open(device, O_RDWR | O_NOCTTY);

	if (fd < 0) {
		perror(device);
		exit(EXIT_FAILURE);
	}

	/* Save serial port settings to restore afterwards. */
	tcgetattr(fd, &oldtio);

	/* Clear new attributes structure. */
	bzero(&newtio, sizeof(newtio));

	/*
	 * BAUDRATE - set above
	 * CMSPAR - 8 data bits, 1 stop bit, space parity
	 * CLOCAL - no modem control
	 * CREAD - enable receiving characters
	 */
	newtio.c_cflag = CS8 | CMSPAR | CLOCAL | CREAD;
	cfsetspeed(&newtio, BAUDRATE);

	/*
	 * IGNPAR - ignore bits with parity errors
	 */
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = 0;

	/* Set non-canonical mode (i.e. we are doing char-by-char, not line-by-line), no echo */
	newtio.c_lflag = 0;

	/* Recieve 1 character at a time, don't time between chars. */
	newtio.c_cc[VTIME] = 0;
	newtio.c_cc[VMIN] = 0;

	/* activate settings. */
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd, TCSANOW, &newtio);

	/* Wait. */
	delay(100);
}

/* Close serial port. */
void close_serial() {
	// Restore old settings.
    	tcsetattr(fd, TCSANOW, &oldtio);

	if (close(fd) == -1)
		perror("close_serial(): close(): ");
}
