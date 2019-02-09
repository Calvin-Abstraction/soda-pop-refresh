#!/usr/bin/python
# parsexml.py - input interesting data from xml file output by dex_parser into database
#
# Author: John Kloosterman
# Date: Feb. 26, 2011

import xml.parsers.expat
import sqlite3
import time
import sys
from settings import *

# Global variables
#
# We have an array of dictionaries about each product.
# so products[i]['attr'] = something.
products = {}
curAttrs = {}
tempValue = 0;
tempUnit = 'A';

def start_element(name, attrs):
    global curTag
    global curAttrs
    curTag = name
    curAttrs = attrs

def end_element(name):
    i = 0

# create the dictionary for product if not already there.
# Python is annoying sometimes. Maybe it's because I don't know it well enough.
def create_product_dict():
    if curAttrs['product'] not in products:
        products[curAttrs['product']] = {}

def char_data(data):
    global products
    global tempValue
    global tempUnit
    if curTag == "price":
        create_product_dict()
        products[curAttrs['product']]['price'] = data
    elif curTag == "paid_products_vended_since_initialization":
        create_product_dict();
        products[curAttrs['product']]['vended'] = data    
    elif curTag == "temperature_value":
        tempValue = float(data)
    elif curTag == "temperature_units":
        tempUnit = data

if __name__ == '__main__':
	if (len(sys.argv) == 1):
		print "parsexml.py - input XML file output by dex_parser to database."
		print "Syntax: parsexml.py <xmlfile>"
		sys.exit()

	f = open(sys.argv[1], 'r');
	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data

	p.ParseFile(f)
	f.close()

	# Check to make sure the data is good enough to commit to the database.
	# Right now this means there is at least one product.

	if len(products) == 0:
		print "No products found. Bad parse - exiting."
		sys.exit()

	# Commit it to the database.
	conn = sqlite3.connect(databaseFile)

	for product, d in products.iteritems():
            # Only insert a row if we sold something.
            if d['vended'] != 0:
                conn.execute("insert into product values (?,?,?,?)", [time.time(), int(product), float(d['price']) / 100, int(d['vended'])])

	conn.execute("insert into temperature values (?,?,?)", [time.time(), tempValue, tempUnit])

	conn.commit()
	conn.close()
