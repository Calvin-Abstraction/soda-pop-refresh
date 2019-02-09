#!/usr/bin/python2
#
# Update the pop machine Twitter feed, @calvin_pop.
#
# Author: John Kloosterman
# Date: May 13, 2011

import twitter
import sqlite3
from databasepath import *

# Connect to database.
conn = sqlite3.connect(databaseFile)
c = conn.cursor()

# Get two last entries.
c.execute("SELECT * FROM temperature ORDER BY unix_time DESC LIMIT 2");
row = c.fetchone()
prevRow = c.fetchone()

if row is None:
    temperaturePart = ""
else:
    # Being Canadian, I like Celsius better.
    celsius = (row[1] - 32) * (5.0/9.0)
    temperaturePart = "I am chilling at {0:.3}&deg;C.".format(celsius)

if prevRow is None:
    durationPart = ""
else:
    secondsElapsed = row[0] - prevRow[0]
    if (secondsElapsed > 3500) and (secondsElapsed < 3700):
        hours = "hour"
    else:
        hours = "{0:.1} hours".format(secondsElapsed / 3600)
    durationPart = "In the last " + hours

# Our machine can hold up to 10 products.
num_products = 10
productParts = []
for i in range(num_products):
    c.execute("SELECT * FROM product WHERE product_id=? ORDER BY unix_time DESC LIMIT 2", [i])
    row = c.fetchone()
    prevRow = c.fetchone()

    # If we have no such product, don't bother.
    if row is None:
        continue

    # We need two data points to compute a difference.
    if prevRow is None:
        continue

    # Selling 0 of something isn't interesting.
    if (row[3] - prevRow[3]) == 0:
        continue

    # Find out the name of our product.
    c.execute("SELECT * FROM names WHERE product_id=?", [i])
    name_row = c.fetchone()

    if name_row is None:
        namePart = "product {0}", i
    else:
        namePart = name_row[1]

    numVended = row[3] - prevRow[3]

    if numVended != 1:
        # We need to pluralize the name. But if it ends in s, don't bother.
        # Vernor's is the main culprit here.
        if namePart[-1] != 's':
            namePart += 's'
        productParts.append('%d %s' % (numVended, namePart))
    else:
        # We vended only one, use 'a' instead of '1'.
        # But we need to check to see if the first letter of the name
        # is a vowel - then we have to use 'an'.
        # A&W's is the problem here.
        anVowels = set('aeioAEIO')
        if namePart[0] in anVowels:
            productParts.append('an ' + namePart)
        else:
            productParts.append('a ' + namePart)

# Close database connection.
conn.close()

# Only output a status if I have something interesting to say, i.e. I sold
#  a product.
if (len(productParts) != 0):

    # Pretty-print the list.
    if len(productParts) == 1:
        productPart = productParts[0]
    elif len(productParts) == 2:
        productPart = productParts[0] + " and " + productParts[1]
    else:
        productPart = ""
        for j in range(len(productParts) - 1):
            productPart += productParts[j] + ", "
        productPart += "and " + productParts[-1];
        
    status = "I sold " + productPart + "."
    # This pushed me over 140 characters if we sell everything.
    #    status += " " + temperaturePart
    print "Status length: "
    print len(status)
    print status

    # Post message to Twitter.
    # Open a connection with Twitter.
    api = twitter.Api(consumer_key='tUnW55yejSvYgf2YxNUEGw',
                  consumer_secret='DNIRqZZk3hbYNef20Ut7WdK7NmbFII3a01nOhq93o',
                  access_token_key='298003640-GyMTpvATkZ641lZiy1ylsWhENkceQT6iZAtmOwhJ',
                  access_token_secret='HzuNRTSL1EeHgQoq4R62n9QEc1rwWDXrQwNKG6ko')

    status = api.PostUpdate(status)
    print "Posted to Twitter."
else:
    print "I didn't have anything interesting to Tweet."
        

