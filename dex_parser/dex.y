%{
/* dex.y - yacc/bison parser for raw DEX files.
 *
 * Author: John Kloosterman
 * Date: Feb. 23, 2011
 */

#include <stdio.h>
#include <string.h>
#include "output.h"

/* On x86 and x64, sizeof(long) = sizeof(void *).
   This is handy, since I can pass strings through YYSTYPE. */
#define YYSTYPE long

#define SILENT_ERRORS

void yyerror(const char *str) {
#ifndef SILENT_ERRORS
        fprintf(stderr,"error: %s\n",str);
#endif
}

int yywrap() {
        return 1;
} 

int main(int argc, char **argv) {
	parse_command_line(argc, argv);
	tag_begin();
        yyparse();
	tag_end();
} 
%}

%token STAR DXS DXE ST ID1 ID4 VA1 VA2 VA3 CA1 CA3 CA4 CA9 CA17 BA1 DA1 TA2 LS PA1 PA2 PA5 LE EA2 EA3 EA7 MA5
SD1 G85 SE NUMBER NAME LF WS RFRG TIME DO CR
%%

statements:
	statement
	| statements statement
	| statements error
	;

statement:
	dexstart
	| id
	| product
	| currency_info
	| dispensed
	| coin_accepter
	| bill_accepter
	| cash
	| exact_change
	| paid_vend
	| test_vend
	| free_vend
	| temperature
	| time
	| power_outages
	| door_open
	| resets
	| dexend
	;

dexstart:
	DXS STAR NUMBER STAR NAME STAR NAME STAR NUMBER
	{
		tag_int("communications id", $3);
		tag_string("functional identifier", $5);
		tag_string("version", $7);
		tag_int("transmission control number", $9);
	}
	;

id:
	ID1 STAR NAME STAR NAME STAR NUMBER STAR STAR NAME STAR
	{
		tag_string("serial number", $3);
		tag_string("model number", $5);
		tag_int("build standard", $7);
		tag_string("asset number", $10);
	}
	;

currency_info:
	ID4 STAR NUMBER STAR NUMBER STAR NUMBER
	{
		tag_int("decimal point position", $3);
		tag_int("currency code", $5);
	}
	;

cash:
	CA3 STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER
	{
		tag_int("value of cash in since last reset", $3);		//      283014 (prb. good)
		tag_int("value of coins in since last reset", $5);		//	84639
		tag_int("value of coins sent to tubes since last reset", $7);	//	15974
		tag_int("value of bills in since last reset", $9);		//	1823
		tag_int("value of cash in since initialization", $11);		//      283014 (prb. good)
		tag_int("value of coins in since initialization", $13);		//	84639
		tag_int("value of coins to tubes since initialization", $15);	//	15974
		tag_int("value of bills in since initialization", $17);		//	1823
	}
	;

dispensed:
	CA4 STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER
	{
		tag_int("value of coins dispensed since initialization", $3);
		tag_int("value of coins manually dispensed since initialization", $5);
		tag_int("value of coins dispensed since last reset", $7);
		tag_int("value of coins manually dispensed since last reset", $9);
	}
	;

exact_change:
	CA9 STAR NUMBER STAR NUMBER
	{
	    tag_int("value of vends while in exact change condition since last reset", $3);
	    tag_int("value of vends while in exact change condition since initialization", $5);
	}
	;

product:
	product1 product2
	| product1 product2 product5
	;

product1:
	PA1 STAR NUMBER STAR NUMBER STAR
	{
	    last_product = $3;
	    tag_product("price", $5);
	}
	;

product2:
	PA2 STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER
	{
	    tag_product("paid products vended since initialization", $3);
	    tag_product("value of paid products vended since initialization", $5);
	    tag_product("paid products vended since last reset", $7);
	    tag_product("value of paid products vended since last reset", $9);
	}
	;

product5:
	PA5 STAR STAR STAR NUMBER
	{
		tag_product("number of times selected while sold out", $5);
	}
	;

paid_vend:
	VA1 STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER
	{
		tag_int("value of paid vend sales since initialization", $3);
		tag_int("number of paid vend sales since initialization", $5);
		tag_int("value of paid vend sales since last reset", $7);
		tag_int("number of paid vend sales since last reset", $9);
		/* + 2 tagalongs - discounts and discount value. */
	}
	;

test_vend:
	VA2 STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER
	{
		tag_int("value of test vend sales since initialization", $3);
		tag_int("number of test vend sales since initialization", $5);
		tag_int("value of test vend sales since last reset", $7);
		tag_int("number of test vend sales since last reset", $9);
	}
	;

free_vend:
	VA3 STAR NUMBER STAR NUMBER STAR NUMBER STAR NUMBER
	{
		tag_int("value of free vend sales since initialization", $3);
		tag_int("number of free vend sales since initialization", $5);
		tag_int("value of free vend sales since last reset", $7);
		tag_int("number of free vend sales since last reset", $9);
	}
	;

coin_accepter:
	CA1 STAR NUMBER STAR NAME STAR NUMBER STAR STAR
	{
		tag_int("coin mechanism serial number", $3);
		tag_string("coin mechanism model", $5);
		tag_int("coin menchanism software revision", $7);
	}
	;

bill_accepter:
	BA1 STAR NUMBER STAR NAME STAR NUMBER STAR STAR
	{
		tag_int("bill accepter serial number", $3);
		tag_string("bill accepter model", $5);
		tag_int("bill accepter software revision", $7);
	}
	;

door_open:
	EA2 STAR DO STAR NUMBER STAR NUMBER
	{
		tag_int("number of times door opened since last reset", $5);
		tag_int("number of times door opened since initialization", $7);
	}
	;

resets:
	EA3 STAR NUMBER
	{
		tag_int("number of data reads", $3);
	}
	;

power_outages:
	EA7 STAR NUMBER STAR NUMBER
	{
		tag_int("power outages since last reset", $3);
		tag_int("power outages since initialization", $5);
	}
	;

temperature:
	MA5 STAR RFRG STAR NAME STAR NAME STAR NAME
	{
		tag_string("temperature state", $5);
		tag_string("temperature value", $7);
		tag_string("temperature units", $9);
	}
	;

time:
	MA5 STAR TIME STAR NUMBER STAR NUMBER STAR NAME STAR NAME
	{
		tag_int("date", $5);
		tag_int("time", $7);
	}
	;

dexend:
	DXE STAR NUMBER STAR NUMBER
	{
		// tag_int("end transmission control number 1", $3);
		// tag_int("end transmission control number 2", $3);
	}
	;

