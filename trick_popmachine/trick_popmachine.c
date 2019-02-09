/* trick_popmachine.c - Trick pop machine into thinking there is a cable connected.
 *  Send SIGUSR1 to tell it to nicely shut down.
 * 
 * Author: John Kloosterman
 * Date: Feb. 28, 2011
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <termios.h>
#include <assert.h>
#include <strings.h>
#include <signal.h>
#include <unistd.h>

#define TRUE 1
#define FALSE 0

/* Continuously send breaks to DEVICE.
   This tricks the pop machine into thinking there is no cable connected. */

int fd;
struct termios set, prev;

void usr1_handler (int arg)
{
	fprintf(stderr, "trick_popmachine: SIGUSR1 recieved: stopping.\n");

	tcsetattr(fd, TCSANOW, &prev);
	if (close(fd) == -1)
		perror("close()");
	exit(EXIT_SUCCESS);
}

int main (int argc, char **argv)
{
	pid_t child;

	if (argc < 2) {
		puts("trick_popmachine - fool pop machine into thinking cable is not connected.");
		puts("Syntax: trick_popmachine <device>");
		puts("Send SIGUSR1 to shut down nicely, in order to read data from machine.");
    		exit(EXIT_FAILURE);
	}

	/* We don't want to block the terminal, so this lets us exit and
		do the real work in the background. */
	child = fork();

	if (child == -1) {
		perror("fork()");
		exit(EXIT_FAILURE);
	}
	if (child != 0) {
		fprintf(stderr, "trick_popmachine: Spawned background process.\n");
		exit(EXIT_SUCCESS);
	}
	/* If we got here, child == 0, so we are the child. */

	/* Set up serial port.
	   See dex_communicate/dex.c for notes. */
	fd = open(argv[1], O_RDWR | O_NOCTTY);
	if (fd == -1) {
		perror(argv[1]);
		exit(EXIT_FAILURE);
	}

	tcgetattr(fd, &prev);
	bzero(&set, sizeof(set));

	set.c_cflag = CS8 | CMSPAR | CLOCAL | CREAD;
	cfsetspeed(&set, B9600);
	set.c_iflag = set.c_oflag = 0;
	set.c_cc[VTIME] = 0;
	set.c_cc[VMIN] = 0;

	tcsetattr(fd, TCSANOW, &set);

	/* Make a nice way to tell us to shut down.
 	   This way the port gets closed properly. */
	signal(SIGUSR1, &usr1_handler);

	/* Send breaks to pop machine. */
	for (;;) {
		tcsendbreak(fd, 0);
	}

	/* This never gets executed, but this is what would go here if it did. */
	tcsetattr(fd, TCSANOW, &prev);
	if (close(fd) == -1)
		perror("close()");

	return 0;
}

