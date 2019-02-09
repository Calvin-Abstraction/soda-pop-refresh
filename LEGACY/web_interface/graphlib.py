#!/usr/bin/python
#
# Pretty graphs!
#
# Author: John Kloosterman
# Date: May 14, 2011

# # Last Updated on February 09, 2018
# By Ben Kastner

import time
import sqlite3
import sys
from databasepath import *

colour = "#8b2e2f"

def outputData():
    hours = [0] * 24
    days = [0] * 7
    months = [0] * 12
    yearDays = [0] * 366
    todayHours = [0] * 24

    conn = sqlite3.connect(databaseFile)
    c = conn.cursor()

    # We only want to do this for rows where we've sold something.
    # That might be hard to do.
    
    # num. of slots plus 1, since on the machine they are 1-indexed.
    num_products = 11

    # Historical data
    for i in range(num_products):
        # Historical Data
        # ===============
        c.execute("SELECT * FROM product WHERE product_id=? ORDER BY unix_time DESC", [i])
        
        # Don't bother with unmentioned products.
        prevRow = c.fetchone()
        if prevRow is not None:
            for row in c:
                # If we didn't sell anything, don't mark it down.
                numVended = (prevRow[3] - row[3])
                if numVended == 0:
                    continue;

                unixtime = row[0]        
                strtime = time.localtime(unixtime)
                
                # 24-hour time
                hours[strtime.tm_hour] += numVended

                # Monday is 0, European-style.
                days[strtime.tm_wday] += numVended

                # Month
                # This is 1-indexed. (see docs.python.org/library/time.html)
                months[strtime.tm_mon - 1] += numVended

                # Day of year
                # This is 1-indexed.
                yearDays[strtime.tm_yday - 1] += numVended

                prevRow = row

        # Data for today
        # ==============
        c.execute("SELECT * FROM product WHERE product_id=? AND unix_time > ? ORDER BY unix_time", [i, time.time() - 86400])
        prevRow = c.fetchone()
        if prevRow is not None:
            for row in c:
                unixtime = row[0]
                strtime = time.localtime(unixtime)
                numVended = row[3] - prevRow[3]
                todayHours[strtime.tm_hour] += numVended
                prevRow = row

    hourData = "var hourData = ["
    for i in range(len(hours)):
        hourData += str(hours[i])
        if i != (len(hours) - 1):
            hourData += ","
    hourData += "];"
    print hourData

    dayData = "var dayData = ["
    for i in range(len(days)):
        dayData += str(days[i])
        if i != (len(days) - 1):
            dayData += ","
    dayData += "];"
    print dayData

    monthData = "var monthData = ["
    for i in range(len(months)):
        monthData += str(months[i]) + ','
    monthData += "];"
    print monthData

    yearDayData = "var yearDayData = ["
    for i in range(len(yearDays)):
        yearDayData += str(yearDays[i]) + ','
    yearDayData += "];"
    print yearDayData

    todayHourData = "var todayHourData = ["
    for i in range(len(todayHours)):
        todayHourData += str(todayHours[i]) + ','
    todayHourData += "];"
    print todayHourData;

    conn.close()

# Last 10 temperatures. Note these will be from most to least recent, so
#  we use JavaScript to reverse this array before making it into a graph.
def outputTemps ():
    conn = sqlite3.connect(databaseFile)
    c = conn.cursor()
    temps = "var tempData = ["

    c.execute("SELECT * FROM temperature ORDER BY unix_time DESC LIMIT 20")
    for row in c:
        celsius = (row[1] - 32) * (5.0/9.0)
        temps += str(celsius) + ','

    temps += '];'

    conn.close()
    print temps

# Output the stuff that needs to go in the <head> section of the file.
def graphHeaders():
    print """
    <script src="js/rgraph/RGraph.common.core.js" type="text/javascript"></script>
    <script src="js/rgraph/RGraph.common.annotate.js" type="text/javascript"></script>
    <script src="js/rgraph/RGraph.common.context.js" type="text/javascript"></script>

    <script src="js/rgraph/RGraph.common.tooltips.js" type="text/javascript"></script>
    <script src="js/rgraph/RGraph.common.resizing.js" type="text/javascript"></script>
    <script src="js/rgraph/RGraph.bar.js" type="text/javascript"></script>
    <script src="js/rgraph/RGraph.line.js" type="text/javascript"></script>

    <script type="text/javascript">
    window.onload = function() { """
    outputData()
    outputTemps()
    print """
         var monthBar = new RGraph.Bar('monthChart', monthData);
         monthBar.Set('chart.labels', ['Jan.', 'Feb.', 
		'Mar.', 'Apr.', 'May', 'June', 'July', 'Aug.', 
		'Sept.', 'Oct.', 'Nov.', 'Dec.'])
         monthBar.Set('chart.title', 'Sales by Month');
         monthBar.Set('chart.colors', ["{0}"]);
         monthBar.Draw();

         /* Strictly speaking, we're a day off on non-leap-years.
            Nobody will notice. */
         var DOYLabels = [];
         DOYLabels[0] = "Jan.";
         DOYLabels[1+31] = "Feb.";
         DOYLabels[1+31+29] = "Mar.";
         DOYLabels[1+31+29+31] = "Apr.";
         DOYLabels[1+31+29+31+30] = "May";
         DOYLabels[1+31+29+31+30+31] = "June";
         DOYLabels[1+31+29+31+30+31+30] = "July";
         DOYLabels[1+31+29+31+39+31+30+31] = "Aug.";
         DOYLabels[1+31+29+31+39+31+30+31+31] = "Sept.";
         DOYLabels[1+31+29+31+39+31+30+31+31+30] = "Oct.";
         DOYLabels[1+31+29+31+39+31+30+31+31+30+31] = "Nov.";
         DOYLabels[1+31+29+31+39+31+30+31+31+30+31+30] = "Dec.";

         /* This ensures there are 366 'items' in the array. */
         DOYLabels[366] = ""; 

         var DOYLine = new RGraph.Line('doyChart', yearDayData);
         DOYLine.Set('chart.labels', DOYLabels);
         DOYLine.Set('chart.title', 'Sales by Day of Year');
         DOYLine.Set('chart.colors', ["{0}"]);
         DOYLine.Draw();

         var dayBar = new RGraph.Bar('dayChart', dayData);
         dayBar.Set('chart.labels', ['Mon.', 'Tues.', 'Wed.', 
		'Thurs.', 'Fri.', 'Sat.', 'Sun.'])
         dayBar.Set('chart.title', 'Sales by Weekday');
         dayBar.Set('chart.colors', ["{0}"]);
         dayBar.Draw();

         var hours = [];
         var isPM = false;
         for (var i = 12; i < 36; i++) {{
            if ((i % 12) == 0) {{
                if (isPM)
                   hours.push("PM");
                else {{
                   hours.push("AM");
                   isPM = !isPM;
                }}
            }}
            else hours.push(i % 12);
         }}

         var hourBar = new RGraph.Bar('hourChart', hourData);
         hourBar.Set('chart.labels', hours);
         hourBar.Set('chart.title', 'Sales by Hour of Day');
         hourBar.Set('chart.colors', ["{0}"]);
         hourBar.Draw();

         tempData.reverse()
         var tempLine = new RGraph.Line('tempChart', tempData);
         tempLine.Set('chart.title', 'Pop temperature trend (degrees C)');
         tempLine.Set('chart.colors', ["{0}"]);
         tempLine.Set('chart.background.grid.vlines', false);
         tempLine.Draw();

         var currentHour = (new Date()).getHours();
         var todayHourLabels = hours;

         /* We need to cycle the todayHourData array by the current hour
            in order to show the graph as receding into the past. */
         for (var i = 0; i < currentHour; i++) {{
            todayHourData.push(todayHourData.shift());
            todayHourLabels.push(todayHourLabels.shift());
         }}

         var todayBar = new RGraph.Bar('todayChart', todayHourData);
         todayBar.Set('chart.title', 'Sales in the past 24 hours');
         todayBar.Set('chart.colors', ["{0}"]);
         todayBar.Set('chart.labels', todayHourLabels);
         todayBar.Draw();
      }}
</script>""".format(colour)


# Output the stuff that needs to go in the body part of the file.
def graphBody(width, height):
   print """
   <h3>Recent Data</h3>
   <div><canvas id="todayChart" width="{0}" height="{1}">HTML5 Canvas support necessary to see graphs.</canvas></div>
   <div><canvas id="tempChart" width="{0}" height="{1}"></canvas></div>
   <h3>Historical Trends</h3>
   <div><canvas id="doyChart" width="{0}" height="{1}"></canvas></div>   
   <br/>
   <div><canvas id="hourChart" width="{0}" height="{1}"></canvas></div>
   <br/>
   <div><canvas id="dayChart" width="{0}" height="{1}"></canvas></div>
   <br/>
   <div><canvas id="monthChart" width="{0}" height="{1}"></canvas></div>
""".format(width, height)

