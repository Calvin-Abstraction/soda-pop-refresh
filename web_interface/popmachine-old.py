#!/usr/bin/python
#
# CGI python script to serve the dynamic web page about the pop machine.
#
# Author: John Kloosterman
# Date: March 1, 2011
#
# To see the database schema, look at xmltodb/createdb.py
#
# CSS and prettification by Mary Seerveld
#

import cgi
import time
import sqlite3

# Database filename. Change as needed.
databaseFile = "/home/john/dexdata.sqlite"

# Stylesheet:
styleSheet = """<style type="text/css">
  <![CDATA[
  body {
    color: black;
    background-color: #6666FF;
    margin:0;
    padding:0;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    font-family:Lucida Grande, Helvetica, sans-serif;
    }
  div#content {
      background-color:#FFFFFF;
      margin: 0;
    text-align: center;
    position:relative;
    margin: auto;
    padding: 20px;
    width: 650px;
    height: 100%;
    top:0;
    border-right: 40px solid #003399;
    border-left: 40px solid #003399;
    }
     h4 {
     font-size: 1.4em;
     font-family:Lucida Grande, Helvetica, sans-serif;
     font-weight:bold;
     margin:.5em;
     color:#003399;
     }
     table {
     margin: auto;
     border:1px solid #6666FF;
     width:500px;
     }
     td {
     border:1px solid #3399FF;
     }
     p {
     margin-bottom: 3em;
     }
     div#credit {
     margin-top: 4em;
     font-size: .8em;
     }
  ]]>
 </style>"""

# Connect to database.
conn = sqlite3.connect(databaseFile)
c = conn.cursor()

# CGI content type.
print 'Content-type: application/xhtml+xml'
print ''

# HTML header
print '<?xml version="1.0" encoding="utf-8"?>'
print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"'
print '    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">'
print '  <head>'
print styleSheet
print '    <title>Calvin CS pop machine</title>'
print '  </head>'
print '<body>'

# Information
print '<div id="content">'
print "<h1>Calvin CS Pop Machine</h1>"
print "<h4>Information</h4>"
print "<p>I am the Calvin Computer Science department's pop machine."
print "I sit in the corner of SB321, and am the only machine serving Coke on campus.</p>"
print """<p>You can see some graphs of the data <a href="graphs.py">here</a>.</p>"""

# Temperature and update time.
# Get the 2 most recent temperature entries.
# The penultimate is used for the product header, so we need it now.
c.execute("SELECT * FROM temperature ORDER BY unix_time DESC LIMIT 2");
row = c.fetchone()
prevrow = c.fetchone()

# In case there is only one row.
if prevrow is None:
	prevrow = row

if row is None:
	print "<b>Error:</b> no temperatures in database."
else:
	print "<h4>Temperature</h4>"
	if row[2] == 'F':
		celsius = (row[1] - 32) * (5.0/9.0)
		print "<p>The pop is chilling at {0:.3}&deg;C ({1}&deg;F).</p>".format(celsius, row[1])
	else:
		print "<p>The pop is chilling at {0}&deg;{1}.</p>".format(row[1], row[2])

# Table about products
print "<h4>Products</h4>"
print "<table>"
print '<tr><th style="width: 250px;">Product</th>'
print '<th style="width: 57px;">Price</th>'
# print "<th>Vended since previously read (interval of {0:.2} hours)</th>".format((row[0] - prevrow[0]) / 3600)
print '<th style="width: 200px;">Vended since<br/>{0}</th>'.format(time.strftime('%I %p, %b. %d', time.localtime(prevrow[0])))
#print '<th style="width: 200px;">Vended since<br/>{0}</th>'.format(time.ctime(prevrow[0]))

# Get first product entry to say the first date we have data.
c.execute("SELECT unix_time FROM product ORDER BY unix_time LIMIT 1")
first_entry = c.fetchone()

if first_entry is None:
	print '<th style="width: 200px;">Vended since<br/>(now)</th></tr>'
else:
	print '<th style="width: 200px;">Vended since<br/>{0}</th></tr>'.format(time.strftime('%b. %d, %Y', time.gmtime(first_entry[0])))

# get first one for comparisons.
# do it for each product.
num_products = 10

for i in range(num_products):
	c.execute("SELECT * FROM product WHERE product_id=? ORDER BY unix_time LIMIT 1", [i])
	first_row = c.fetchone()

	# If the product is never mentioned, ignore it.
	# can't use rowcount
	if first_row is None:
		continue

	print "<tr>"

	c.execute("SELECT * FROM product WHERE product_id=? ORDER BY unix_time DESC LIMIT 2", [i])
	penultimate_row = c.fetchone()
	ultimate_row = c.fetchone()
	
	# This happens when the product is only mentioned once.
	if ultimate_row is None:
		ultimate_row = penultimate_row

	# Product ID
	# print "<td>", ultimate_row[1], "</td>"
	# Name
	print "<td>"
	c.execute("SELECT * FROM names WHERE product_id=?", [i])
	name_row = c.fetchone();
	
	if name_row is None:
		print "Unnnamed product: id", i
	else:
		print cgi.escape(name_row[1])

	print "</td>"

	# Price
	print "<td>", "${0}".format(ultimate_row[2]), "</td>"
	# Since last read
	print "<td>", penultimate_row[3] - ultimate_row[3], "</td>"
	# Since began tracking
	print "<td>", penultimate_row[3] - first_row[3], "</td>"

	print "</tr>"

# End table
print "</table>"

# Last updated
if row is not None:
	print '<div id="credit">'
	print "Data was last updated at", time.ctime(row[0])
	print "<br/><br/>"

# Maintainer
print "Maintained by John Kloosterman &lt;jsk9&gt;<br/>"
print "Web design by Mary Seerveld &lt;mos2&gt;</div></div>"

# HTML footer
print "</body></html>"

# Close database
conn.close()
