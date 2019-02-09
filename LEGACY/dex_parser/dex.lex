%{
/* dex.lex - flex lexer for raw DEX output
 * 
 * Author: John Kloosterman
 * Date: Feb. 23, 2011
 */

#include <stdio.h>
#include <string.h>
#include "dex.tab.h"
%}
%%
\*		return STAR;
DXS		return DXS;
DXE		return DXE;

ST		return ST;
ID1		return ID1;
ID4		return ID4;

VA1		return VA1;
VA2		return VA2;
VA3		return VA3;

CA1		return CA1;
CA3		return CA3;
CA4		return CA4;
CA9		return CA9;
CA17		return CA17;

BA1		return BA1;
DA2		return DA1;
TA2		return TA2;

PA1		return PA1;
PA2		return PA2;
PA5		return PA5;
EA2		return EA2;  
EA3		return EA3;
EA7		return EA7;
MA5		return MA5;
G85		return G85;
SE		return SE;

DO		return DO;	/* EA2 arguments */
CR		return CR;

RFRG		return RFRG; 	/* MA5 arguments */
TIME		return TIME;

[-0-9]+			yylval = atoi(yytext); 		return NUMBER;  
[-,A-Z0-9\/\. ]+	yylval = (long) strdup(yytext); return NAME;

[\n]*                   	/* ignore end of line */;
[ \t\r]*                  	/* ignore whitespace and carriage returns */;
