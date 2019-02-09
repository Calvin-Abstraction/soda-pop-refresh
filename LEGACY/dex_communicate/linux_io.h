/*
 * linux_io.h - functions to communicate with the serial port under linux.
 *
 * Created on: Feb 22, 2011
 * Authors: John Kloosterman and Quentin Baker
 */

#ifndef LINUX_IO_H_
#define LINUX_IO_H_

void flush_serial();
int serial_send(char x);
int wait4_for_serial(unsigned char *ch);
char wait_for_serial(int time);

void init_serial(char *device);
void close_serial();

void delay (int msec);

#endif /* LINUX_IO_H_ */
