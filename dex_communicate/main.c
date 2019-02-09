/*
 * main.c
 *
 *  Created on: Feb 22, 2011
 *      Author: jsk9
 */

#include <stdio.h>
#include <stdlib.h>
#include "dex.h"

int main (int argc, char **argv) {
  if (argc < 2) {
    puts("dex_communicate - pull audit data from pop machine connected at <device>.");
    puts("Syntax: dex_communicate <device>");
    exit(EXIT_FAILURE);
  }

  dex_main(argv[1]);
  
  return 0;
}
