/*
 * dex.c - implements protocol to get audit data from the pop machine.
 *
 * Created: Feb. 22, 2011
 * Mostly taken from dex_audit.cpp in specifications/Dexread Version 1.1.zip
 * Author: John Kloosterman
 *
 * The author of dex_audit.cpp has more information about the magic going on,
 *  if interested.
 */

/* Define to be more verbose about the communications going on. */
#define DEBUG 1

/* Number of communication attempts to try before giving up. */
#define MAX_TRIES 10

#ifdef DEBUG
#define debug(x) fprintf(stderr, x);
#else
#define debug(x) ;
#endif

#include "linux_io.h"
#include "dexcommands.h"
#include "constants.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* Constants */
#define 	BUFFER_SIZE 			5500 			// data buffer size
#define 	FIELD_BUFFER			120
#define 	MAX_FIELD       		249			// max field buffer
#define 	SUCCESS			  	0	  		// function will return 0 if successful
#define 	FAIL				-1   			// Function will return -1 if unsuccessful
#define 	MILLI_SECONDS	 		15

#define  CHANGER_IS_SLAVE  "1234567890RR01L01"  /* COM_ID R REV_LEVEL */
#define  CHANGER_IS_MASTER "001234567890R01L01" /*RESP_CODE COM_ID REV_LEVEL */
#define  SLAVE  0
#define  MASTER 1

/* Global variables. */
int Port;
char *field[500];
char third_handshake_data[250];
int lastfield;
int outofmem;
int dont_ENQ_twice;
unsigned int BCC, BCC_0, BCC_1, BCC_14, DATA_0, X2, X15, X16;

int wait_for_response (unsigned char *ch) {
  while (wait4_for_serial(ch) == 0) {}       // Wait for a response
  return(SUCCESS);
}

void alternate_answer(int j)
{
  delay(MILLI_SECONDS);
  serial_send(DLE);
  delay(MILLI_SECONDS);
  serial_send(0x30+(j));
}

/* CRC check */
void crc_16(char data)
{
  int j;

  for (j=0;j<8;j++)
    {
      DATA_0 = (data >> j) & 0x0001;
      BCC_0 = (BCC & 0x0001);
      BCC_1 = (BCC >> 1) & 0x0001;
      BCC_14 = (BCC >> 14) & 0x0001;
      X16 = (BCC_0 ^ DATA_0) & 0x0001; 	// bit15 of BCC after shift
      X15  = (BCC_1 ^ X16) & 0x0001;		// bit0 of BCC after shift
      X2  = (BCC_14 ^ X16) & 0x0001;		// bit13 of BCC after shift
      BCC = BCC >> 1;
      BCC = BCC & 0x5FFE;
      BCC = BCC | (X15);
      BCC = BCC | (X2 << 13);
      BCC = BCC | (X16 << 15);
    }
}

int master_handshake(char data_string[])
{
  int i;
  char done = FALSE;
  unsigned char response1,response2;
  unsigned char response = NUL;
  BCC = NUL;

  if (dont_ENQ_twice == 1)   // True on Master Mode
    {
      flush_serial();                         //clear return buffer
      serial_send(ENQ);
      response = wait_for_serial(100);
    }

  i = 0;
  while (!done)
    {
      if (dont_ENQ_twice == 1)    // True in Master mode
	{
	  while (response != DLE)
	    {
	      flush_serial();		//clear return buffer
	      serial_send(ENQ);
	      response = wait_for_serial(100);
	    }


	  if (wait_for_response(&response)== FAIL)
	    return(FAIL);
	  if (response != 0x30)
	    return(FAIL);
	}

      dont_ENQ_twice = 0;
      delay(MILLI_SECONDS);
      flush_serial();			//clear return buffer
      serial_send(DLE);
      delay(MILLI_SECONDS);
      serial_send(SOH);
      delay(MILLI_SECONDS);

      for (i=0;i<strlen(data_string);i++)
	{
	  crc_16(data_string[i]);
	  serial_send(data_string[i]);
	  delay(MILLI_SECONDS);
	}
      serial_send(DLE);
      delay(MILLI_SECONDS);
      serial_send(ETX);
      delay(MILLI_SECONDS);
      crc_16(ETX);
      serial_send(BCC&0x00FF);
      delay(MILLI_SECONDS);
      serial_send((BCC&0xFF00)>>8);
      delay(MILLI_SECONDS);
      delay(5*MILLI_SECONDS);
      if (wait_for_response(&response1)==FAIL)
	return(FAIL);
      if (wait_for_response(&response2)==FAIL)
	return(FAIL);
      if ((response1 == DLE) && ((response2 == 0x31) || (response2 ==0x30)))
	{
	  serial_send(EOT);
	  return(SUCCESS);
	}
      done = TRUE;
      if (response1 == NAK)
	done = FALSE;
      else	return(FAIL);
    }
  return(SUCCESS);
}

int slave_handshake()
{
  unsigned char response;
  BCC = NUL;

  for (;;)
    {
      if (wait_for_response(&response)==FAIL)  /* Waiting for ENQ */
	break;
      delay(MILLI_SECONDS);
      if (response == ENQ)
	alternate_answer(0);
      else if (response == ETX)
	{
	  crc_16(response);
	  if (wait_for_response(&response)==FAIL)
	    return(FAIL);
	  crc_16(response);
	  if (wait_for_response(&response)==FAIL)
	    return(FAIL);
	  crc_16(response);
	  delay(MILLI_SECONDS);
	  if (BCC == NUL)
	    alternate_answer(1);
	  else
	    {
	      BCC = NUL;
	      serial_send(NAK);
	    }
	}
      else if (response == EOT)
	return(SUCCESS);
      else if ((response != DLE) && (response != SOH) && (response != STX))
	crc_16(response);

    } /* end of forever loop */
  return(FAIL);
}

int third_handshake(int error)
{
  unsigned char response,response1,response2;
  int           j, i, block_number, save_i, k, fieldlen, savefield;

  savefield=0;
  lastfield=0;
  save_i=0;
  k=0;
  i=0;
  fieldlen=0;
  error = 0;
  j=1;
  block_number=1;
  outofmem=FALSE;
  BCC = 0x0000;

  for (;;)
    {
      if (wait_for_response(&response)==FAIL)
	return(FAIL);

      if (response == ENQ)
	{
	  alternate_answer(0);
	  i = 0;
	}

      else if (response == STX)
	{
	  save_i = i;
	  savefield=fieldlen;
	  BCC = 0x0000;
	}

      else if (response == ETB)
	{
	  crc_16(response);

	  if (wait_for_response(&response1)==FAIL)
	    return(FAIL);
	  if (wait_for_response(&response2)==FAIL)
	    return(FAIL);

	  crc_16(response1);
	  crc_16(response2);

	  if (BCC == 0x0000)
	    {
	      if (block_number == error)
		{
		  i = save_i;
		  serial_send(NAK);
		}
	      else
		{
		  alternate_answer((int) (j % 2));
		  j++;
		}
	      block_number++;
	    }
	  else
	    {
	      if(field[save_i]!=NULL)
		strcpy(third_handshake_data,field[save_i]);

	      for(k=save_i;k<i;k++)
		free(field[k]);

	      i = save_i;
	      fieldlen=savefield;
	      serial_send(NAK);
	    }
	}

      else if (response == ETX)
	{
	  crc_16(response);
	  if (wait_for_response(&response1)==FAIL)
	    return(FAIL);

	  if (wait_for_response(&response2)==FAIL)
	    return(FAIL);
	  crc_16(response1);
	  crc_16(response2);

	  if (BCC == 0x0000)
	    {
	      alternate_answer((int) (j % 2));
	      j++;
	    }
	  else
	    {
	      if(field[save_i]!=NULL)
		strcpy(third_handshake_data,field[save_i]);

	      for(k=save_i;k<i;k++)
		free(field[k]);

	      i = save_i;
	      fieldlen=savefield;
	      serial_send(NAK);
	    }
	}

      else if (response == EOT)
	{
	  lastfield=i;
	  return(SUCCESS);
	}

      else if ((response != DLE) && (response != SOH))
	{
	  crc_16(response);
	  third_handshake_data[fieldlen++] = toupper(response);

	  if(response==LF)
	    {
	      third_handshake_data[fieldlen] = 0;
	      field[i]=(char *)malloc(strlen(third_handshake_data)+1);
	      fieldlen=0;

	      if(field[i]!=NULL)
		{
		  strcpy(field[i],third_handshake_data);
		  if((i+1)<MAX_FIELD)
		    i++;
		}
	      else
		outofmem=TRUE;
	    }
	}
    }//end forever loop
}

void fail() {
	fprintf(stderr, "*** FAILED ***\n");
	close_serial();
        debug("Serial port closed.\n");
	exit(EXIT_FAILURE);
}

void do_dex()
{
  int  	 dex_com;
  char 	 ch;

  dex_com = NAK;

  int i;
  for(i = 0; i < MAX_TRIES; i++)
    {
      flush_serial();	// clear return buffer
      serial_send(ENQ);
      debug("ENQ sent.\n");
      delay(20);	//delay 20ms before checking for response

      if ((ch = wait_for_serial(200)) == ENQ)
	{
	  debug("ENQ recieved.\n");
	  dex_com = MASTER;
	  break;
	}

      if (ch == DLE)
	{
	  debug("DLE recieved.\n");
	  if (wait_for_response((unsigned char *) &ch) == FAIL)

	    {
	      ch = NAK;
	      dex_com = NAK;
	      break;
	    }
	  else
	    {
	      dex_com = SLAVE;
	      break;
	    }
	}

      debug("Didn't receive anything interesting, looping back.\n");
      delay(100);	//delay 100ms before trying again
    }  /* forever bracket */

  if (i == MAX_TRIES)
    {
       debug("Didn't recive a response after MAX_TRIES times. Giving up.\n");
       fail();
    }

  if (dex_com == SLAVE)      // GLOBAL COMMUNICATION
    {
      debug("Role: Slave\n");
      dont_ENQ_twice = 0;
      if (master_handshake(CHANGER_IS_SLAVE) == SUCCESS)
	{
	  debug("Master Handshake Successful\n");
	  if (slave_handshake() == SUCCESS)
	    {
	      debug("Slave Handshake Successful \n");
	      if (third_handshake(0) == SUCCESS)
		{
		  debug("Third Handshake Successful \n");
		}
	      else
		{
		  debug("Third Handshake Failed     \n");
		  fail();
		  ch=ESC;
		}
	    }
	  else
	    {
	      debug("Slave Handshake Failed     \n");
	      fail();
	      ch=ESC;
	    }
	}
      else
	{
	  debug("Master Handshake Failed    \n");
          fail();
	  ch=ESC;
	}
    }
  else if (dex_com == MASTER)
    {
      debug("Role: Master\n");

      dont_ENQ_twice = 1;
      if (slave_handshake() == SUCCESS)
	{
	  debug("Slave Handshake Successful \n");

	  if (master_handshake(CHANGER_IS_MASTER) == SUCCESS)
	    {
	      debug("Master Handshake Successful\n");

	      if (third_handshake(0) == SUCCESS)
		{
		  debug("Third Handshake Successful \n");
		}
	      else
		{
		  debug("Slave Handshake Failed     \n");
		  ch=ESC;
		  fail();
		}
	    }
	  else
	    {
	      debug("Third Handshake Failed     \n");
	      ch=ESC;
	      fail();
	    }
	}
      else
	{
	  debug("Master Handshake Failed    \n");
	  ch=ESC;
          fail();
	}
    }
  else
    {
      debug("DEX Communications Failed  \n");
      ch=ESC;
      fail();
    }
}

void dex_main (char *device) {
  init_serial(device);
  debug("Serial port initialized.\n");

  do_dex();
  debug("DEXing done.\n");

  close_serial();
  debug("Serial port closed.\n");

  // output
  int i;
  for(i = 0; i < lastfield; i++)
    printf("%s", field[i]);

  /* We leak all the memory associated with field.
     It's not worth the time to fix.
     This is acceptable because we only run once, but
     for this reason it would not be a good idea
     to call dex_main() in a daemon or something.
  */
}
