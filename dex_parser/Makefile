# Makefile for combining flex, bison, and gcc.
#
# Author: Joel Adams
# Modified: John Kloosterman, Feb. 23, 2011

BIN = dex_parser

$(BIN): dex.lex dex.y output.c
	flex dex.lex
	bison -d dex.y
	gcc -g lex.yy.c dex.tab.c output.c -o dex_parser -lfl

clean:
	rm -f lex.yy.c dex.tab.h dex.tab.c dex_parser output.o

