#!/usr/bin/python
#

import cgi
import time
import sqlite3
import copy
import sys
from databasepath import *

def infoTable():
	# Connect to database.
	conn = sqlite3.connect(databaseFile)
	c = conn.cursor()

	# Table about products
	print '<h3>Pop Vended</h3>'
	print '<table class="infoTable">'
	print '<tr><th>Type</th>'
	print '<th>Price</th>'
	print "<th>Stock</th>"
	print '<th>Today</th>'

	# Get first product entry to say the first date we have data.
	# c.execute("SELECT unix_time FROM product ORDER BY unix_time LIMIT 1")
	# first_entry = c.fetchone()

	print '<th>Total</th>'
	print '</tr>'

	# get first one for comparisons.
	# do it for each product.
	num_products = 11

	for i in range(num_products):
		c.execute("SELECT * FROM product WHERE product_id=? ORDER BY unix_time LIMIT 1", [i])
		first_row = c.fetchone()

		# If the product is never mentioned, ignore it.
		# can't use rowcount
		if first_row is None:
			continue

		print "<tr>"

		# Get latest entry
		c.execute("SELECT * FROM product WHERE product_id=? ORDER BY unix_time DESC LIMIT 1", [i])
		last_row = c.fetchone()
	
		# Get first entry 24 hours (86400 seconds) ago.
		c.execute("SELECT * FROM product WHERE product_id=? AND unix_time >= ? LIMIT 1", [i, time.time() - 86400])
		midnight_row = c.fetchone()

		# This happens when the product is only mentioned once.
		if last_row is None:
			continue

		if midnight_row is None:
			print "" # does this do anything?

		# Product ID
		# Name
		print "<td class='name'>"
		c.execute("SELECT * FROM names WHERE product_id=?", [i])
		name_row = c.fetchone();
	
		if name_row is None:
			print "Unnnamed product: id", i
		else:
			print cgi.escape(name_row[1])

		print "</td>"

		# Price
		print "<td>", "${0}".format(last_row[2]), "</td>"

		# Number left in machine
		# Get time of last refill, and how many were in there.
		c.execute("SELECT unix_time, number FROM refills WHERE product_id=? ORDER BY unix_time DESC LIMIT 1", [i]);
		refill_row = c.fetchone()
		refill_time = refill_row[0]
		refill_amount = refill_row[1]

		# Get the counter at the closest time before the refill.
		c.execute("SELECT num_vended FROM product WHERE product_id=? AND unix_time < ? ORDER BY unix_time DESC LIMIT 1", [ i, refill_time] )
		vended_refill_row = c.fetchone()
		vended_since_refill = last_row[3] - vended_refill_row[0]
		left_in_machine = refill_amount - vended_since_refill
		
		if left_in_machine <= 0:
			print "<td class='empty'>"
			print "Sold Out"
		else:
			print "<td>"
			print left_in_machine
		print "</td>"

		# Today
#		print "<td>", last_row[3] - midnight_row[3], "</td>"
		# Since began tracking
		print "<td>", last_row[3] - first_row[3], "</td>"

		print "</tr>"
		
	# End table
	print "</table>"

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
		print "<h3>Temperature</h3>"
		if row[2] == 'F':
			celsius = (row[1] - 32) * (5.0/9.0)
			print "<p>The pop is chilling at {0:.3}&deg;C ({1}&deg;F).</p>".format(celsius, row[1])
		else:
			print "<p>The pop is chilling at {0}&deg;{1}.</p>".format(row[1], row[2])


	# Last updated
	# if row is not None:
	#	print '<div id="updated">'
	#	print "Data was last updated at", time.ctime(row[0])
	#	print '</div>'

	# Close database
	conn.close()
