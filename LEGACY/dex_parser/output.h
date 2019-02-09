/* output.h - Helper functions for parser output. 
 */

#ifndef _OUTPUT_H
#define _OUTPUT_H

void parse_command_line (int argc, char **argv);

#define tag_string(x, y) \
	_tag_string(x, (char *) y);

void _tag_string(char *tagname, char *data);
void tag_int(char *tagname, int data);
void tag_product(char *tagname, int data);

void tag_begin();
void tag_end();

int last_product;

#endif
