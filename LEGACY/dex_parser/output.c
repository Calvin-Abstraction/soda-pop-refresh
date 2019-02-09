/* output.c - Helper functions for parser output. 
 *
 * Author: John Kloosterman
 * Date: Feb. 23, 2011
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "output.h"

#define FALSE 0
#define TRUE 1

int use_xml = FALSE;
int use_html = FALSE;
int use_full_html = FALSE;
int use_text = FALSE;

/* Parse command line to see which set of output functions
   we will be running. */
void parse_command_line (int argc, char **argv) {
  if (argc != 2) {
    printf("dex_parser - parse raw DEX output into a more useful format.\n");
    printf("Syntax: dex_parser {-xml|-fullhtml|-html|-text}\n");
    printf("Input is read from stdin.\n");
    exit(EXIT_FAILURE);
  }
  
  if (strcmp(argv[1], "-xml") == 0) {
    use_xml = TRUE;
  }
  if (strcmp(argv[1], "-fullhtml") == 0) {
    use_html = TRUE;
    use_full_html = TRUE;
  }
  if (strcmp(argv[1], "-html") == 0) {
    use_html = TRUE;
  }
  if (strcmp(argv[1], "-text") == 0) {
    use_text = TRUE;
  }

  if (!use_xml && !use_html && !use_text) {
    printf("dex_parser - parse raw DEX output into a more useful format.\n");
    printf("Syntax: dex_parser {-xml|-fullhtml|-html|-text}\n");
    printf("Input isread from stdin.\n");
    exit(EXIT_FAILURE);
  }
}

/* XML output functions. */
char *xml_tag_switch_spaces (char *string) {
	int len = strlen(string);
	int i;
	char *ret = strdup(string);
	
	for (i = 0; i < len; i++)
		if (ret[i] == ' ') ret[i] = '_';	// this segfaults for a reason I can't think of.

	return ret;
}

void xml_tag_begin() {
	printf("<?xml version=\"1.0\"?><pop_report>");
}

void xml_tag_end() {
	printf("</pop_report>");
}

void xml_tag_string(char *tagname, char *data) {
	char *t = xml_tag_switch_spaces(tagname);
	printf("<%s>%s</%s>", t, data, t);
	free(t);
}

void xml_tag_int(char *tagname, int data) {
	char *t = xml_tag_switch_spaces(tagname);
	printf("<%s>%d</%s>", t, data, t);
	free(t);
}

void xml_tag_product(char *tagname, int data) {
	char *t = xml_tag_switch_spaces(tagname);
	printf("<%s product=\"%d\">%d</%s>", t, last_product, data, t);
	free(t);
}
/* end XML output */

/* Human-readable text output */
void text_tag_begin() {
	// nothing
}

void text_tag_end() {
	// nothing
}

void text_tag_string(char *tagname, char *data) {
	printf("%s: %s\n", tagname, data);
}

void text_tag_int(char *tagname, int data) {
	printf("%s: %d\n", tagname, data);
}

void text_tag_product(char *tagname, int data) {
    printf("product %d %s: %d\n", last_product, tagname, data);
}

/* end text output */

/* HTML output */
void html_tag_begin() {
	if (use_full_html)
		printf("<html><head><title>Pop machine data</title></head><body>");

	printf("<table>");
}

void html_tag_end() {
	printf("</table>");
	if (use_full_html)
		printf("</body></html>");
}

void html_tag_string(char *tagname, char *data) {
	printf("<tr><td>%s</td><td>%s</td></tr>", tagname, data);
}

void html_tag_int(char *tagname, int data) {
	printf("<tr><td>%s</td><td>%d</td></tr>", tagname, data);
}

void html_tag_product(char *tagname, int data) {
    printf("<tr><td>product %d %s</td><td>%d</td></tr>", last_product, tagname, data);
}

/* end HTML output */

/* General functions; decides based on command line
   which set of functions to call. */
void _tag_string(char *tagname, char *data) {
	if (use_xml)
		xml_tag_string(tagname, data);
	else if (use_html)
		html_tag_string(tagname, data);
	else if (use_text)
		text_tag_string(tagname, data);
}

void tag_int(char *tagname, int data) {
	if (use_xml)
		xml_tag_int(tagname, data);
	else if (use_html)
		html_tag_int(tagname, data);
	else if (use_text)
		text_tag_int(tagname, data);
}

void tag_product(char *tagname, int data) {
	if (use_xml)
		xml_tag_product(tagname, data);
	else if (use_html)
		html_tag_product(tagname, data);
	else if (use_text)
		text_tag_product(tagname, data);
}

void tag_begin() {
	if (use_xml)
		xml_tag_begin();
	else if (use_html)
		html_tag_begin();
}

void tag_end() {
	if (use_xml)
		xml_tag_end();
	else if (use_html)
		html_tag_end();
}
