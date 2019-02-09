/*
 * constants.h - constants from dexread
 *
 *  Created on: Feb 22, 2011
 *  Author: John Kloosterman
 */

#ifndef CONSTANTS_H_
#define CONSTANTS_H_

#define TRUE            1       /* boolean TRUE value */
#define FALSE           0       /* boolean FALSE value */
#define BUFFERSIZE      240      /* size of character input buffer */
#define FIXED           0       /* fixed tune */
#define boolean         int     /* make a boolean data type */
#define ESC             27      /* ESCAPE character */
#define OK              1       /* successful function execution */
#define ERROR           0       /* unsuccessful function execution */
#define SPACE           0x20    /* hex representation for a space */
#define LF              0x0A    /* Line Feed */
#define CR              0x0D    /* carriage return*/
#define BS              0x08    // back space
#define EOB             0x07    // end of block (bell)

#endif /* CONSTANTS_H_ */
