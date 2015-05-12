'''
NYC Agency with the Greatest Number of Complaints by Zip
By: Sarah Welt

This program creates a choropleth map for NYC in which the shape color for each zip code 
represents the agency with the greatest number of complaints.  The map supports the pan tool, 
the wheel zoom tool, the box zoom tool, and the hover tool.  
'''

import csv
import shapefile
import sys
import operator
from bokeh.plotting import *
from bokeh.sampledata.iris import flowers
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import random
from bokeh.objects import HoverTool
from collections import OrderedDict

agencyDict = {}

def loadComplaints(complaintsFilename):
  # Reads all complaints and keeps zips which have complaints.
  with open(complaintsFilename) as f:
    csvReader = csv.reader(f)
    headers = csvReader.next()
    zipIndex = headers.index('Incident Zip')
    latColIndex = headers.index('Latitude')
    lngColIndex = headers.index('Longitude')
    agencyIndex = headers.index('Agency')

    lat = []
    lng = []  
    
    colors = []
    complaintsPerZip = {}

    for row in csvReader:
      try:
        lat.append(float(row[latColIndex]))
        lng.append(float(row[lngColIndex]))
        agency = row[agencyIndex]
        zipCode = row[zipIndex]
        if not agency in agencyDict:          
          agencyDict[agency] = len(agencyDict)

        if zipCode in complaintsPerZip:
          if agency in complaintsPerZip[zipCode]:
            complaintsPerZip[zipCode][agency]+=1
          else:
            complaintsPerZip[zipCode][agency]=1
        else:
          complaintsPerZip[zipCode]={}
          complaintsPerZip[zipCode][agency]=1

      except:
        pass

    return {'zip_complaints': complaintsPerZip}

def drawPlot(shapeFilename, mapPoints):
  # Read the ShapeFile
  dat = shapefile.Reader(shapeFilename)
  
  # Creates a dictionary for zip: {lat_list: [], lng_list: []}.
  zipCodes = []
  polygons = {'lat_list': [], 'lng_list': [], 'color_list' : [],'top_agency': [], 'zip_code': [], 'number_of_complaints':[]}

  colors = {}
  
  for j, i in enumerate(agencyDict.keys()):
    r = lambda: random.randint(0,255)
    colors[i] = ('#%02X%02X%02X'%(r(),0,r()))
  
  record_index = 0
  for r in dat.iterRecords():
    currentZip = r[0]

    if currentZip in currentZip:
      zipCodes.append(currentZip)

      # Gets shape for this zip.
      shape = dat.shapeRecord(record_index).shape
      points = shape.points

      # Breaks into lists for lat/lng.
      lngs = [p[0] for p in points]
      lats = [p[1] for p in points]

      # Stores lat/lng for current zip shape.
      polygons['lng_list'].append(lngs)
      polygons['lat_list'].append(lats)


      # Calculate color, according to number of complaints
      if currentZip in mapPoints['zip_complaints']:

        # Top complaint type
        sortedlist = sorted(mapPoints['zip_complaints'][currentZip].items(), key=operator.itemgetter(1), reverse=True)
        agency = sortedlist[0][0]

        if agency in colors:
          color = colors[agency]
        else:
          color = 'white'

      else:
        color = 'white'
      polygons['number_of_complaints'].append(sortedlist[0][1])
      polygons['top_agency'].append(agency)
      polygons['zip_code'].append(currentZip)
      polygons['color_list'].append(color)

    record_index += 1


  # Creates the Plot
  color_set = list(set(polygons['color_list']))
  output_file("ComplaintsAgency.html", title="ComplaintsAgency")
  hold()
  source = ColumnDataSource(data = dict(x = polygons['lat_list'], y =polygons['lng_list'], zip_code = polygons['zip_code'], top_agency = polygons['top_agency'], number_of_complaints = polygons['number_of_complaints'], colors = polygons['color_list']))
  TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave,hover"

  # Creates the polygons.
  patches(polygons['lng_list'], polygons['lat_list'], \
        fill_color=polygons['color_list'], line_color="gray", \
        source = source,\
        tools=TOOLS, plot_width=900, plot_height=700, \
        title="Agency with the Most Complaints in Each NYC Zip Code")
  for i in xrange(len(polygons['lat_list'])):
    scatter(0,0, color = polygons['color_list'][i], legend = polygons['top_agency'][i])

  hover = curplot().select(dict(type = HoverTool))

  hover.tooltips = OrderedDict([("Zip Code",'@zip_code'),("Top Agency",'@top_agency'),("Number of Complaints",'@number_of_complaints')])
                  
  show()

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print 'Usage:'
    print sys.argv[0] \
    + ' <complaintsfilename> <shapefilename>'
    print '\ne.g.: ' + sys.argv[0] \
    + ' data:nyc311.csv shapefile:zip_code_040114.shp'
  else:
    mapPoints = loadComplaints(sys.argv[1])
    drawPlot(sys.argv[2], mapPoints)
