#!/usr/bin/python2
# Combine Twitter feed, graphs, etc. into one page.
#
#

import MySQLdb
from graphlib import *
from statuslib import *

import cgitb
cgitb.enable()

twitterWidget = """
<script src="http://widgets.twimg.com/j/2/widget.js"></script>
<script type="text/javascript">
new TWTR.Widget({
  version: 2,
  type: 'profile',
  rpp: 6,
  interval: 6000,
  width: 325,
  height: 300,
  theme: {
    shell: {
      background: '#3e718a',
      color: '#ffffff'
    },
    tweets: {
      background: '#ffffff',
      color: '#3e718a',
      links: '#8ec1da'
    }
  },
  features: {
    scrollbar: true,
    loop: false,
    live: true,
    hashtags: true,
    timestamp: true,
    avatars: false,
    behavior: 'all'
  }
}).render().setUser('calvin_pop').start();
</script>
"""

googleAnalytics = """
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-23444084-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
"""

html5badge = """
<p style='text-align: center'>
This page is valid HTML5. </p>

<p style='text-align: center'>
<a href="http://validator.w3.org/check?uri=http%3A%2F%2Fsoda-pop.calvin.edu">
<img src="http://www.w3.org/html/logo/badge/html5-badge-h-graphics.png" width="133" height="64" alt="HTML5 Powered with Graphics, 3D &amp; Effects" title="HTML5 Powered with Graphics, 3D &amp; Effects">
</a>"""

# If we use border-radius, we can't use this.
cssbadge = """<br/>
<br/>
<a href="http://jigsaw.w3.org/css-validator/check/referer">
    <img style="border:0;width:88px;height:31px"
        src="http://jigsaw.w3.org/css-validator/images/vcss-blue"
        alt="Valid CSS!" />
</a>
</p>
"""

# Connect to mySQL
conn = MySQLdb.connect( host='localhost',
                        user='popmachine',
                        passwd='2SQV77Hp770I2VXuxbmTPb',
                        db='popmachine' )

# This can't be xhtmlized because of the Twitter widget.
print "Content-type: text/html"
print ""

# By the way, we're HTML5. So there's no head or body tags, and this doctype
# is correct.
print """<!DOCTYPE html>
<meta charset="UTF-8">
"""

print "<title>Calvin CS Pop Machine</title>"
print googleAnalytics
graphHeaders( conn )
print "<link rel='stylesheet' href='popmachine.css' media='screen'/>"

print """
<h1> Calvin Computer Science Pop Machine </h1>
"""

print "<table class='mainTable'>"
print "<tr><td style='vertical-align: top'>"
infoTable( conn )
print "<h3>Twitter</h3>"
print twitterWidget
print "<br/><br/>"
print html5badge
print "</td>"

print "<td>"
print """
<h3>Information</h3>
<p>I am the Calvin Computer Science department's pop machine. <br/> 
I live in the corner of SB321, the CS lounge. <br/>
You should come visit me some time.</p>"""
graphBody( 600, 300)

print "</td></tr></table>"
print "<p class='credits'>Maintainer: John Kloosterman &lt;jsk9&gt;</p>"
