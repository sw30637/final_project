'''
Complaint Ratios by NYC Zip Code for Two Agencies
By: Sarah Welt

This program compares two agencies in terms of number of complaints for each zip code.  
The map supports the pan tool, the wheel zoom tool, the box zoom tool, and the hover tool.  
'''

import csv
import shapefile
import sys
import math
import operator
from bokeh.plotting import *
from bokeh.sampledata.iris import flowers
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import random
from bokeh.objects import HoverTool
from collections import OrderedDict
from math import floor

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

def drawPlot(shapeFilename, mapPoints, agency1, agency2):
  # Read the ShapeFile
  dat = shapefile.Reader(shapeFilename)
  
  # Creates a dictionary for zip: {lat_list: [], lng_list: []}.
  zipCodes = []
  polygons = {'lat_list': [], 'lng_list': [], 'color_list': [], 'zip_code': [], 'bin_ratio':[], 'ratio_num':[], 'complaintsPerZip1':[], 'complaintsPerZip2':[]}
  compare = {agency1:0,agency2:0}

  # Qualitative 6-class Set1
  colors_palate = ['#E21C08','#CB1A14','#B41921','#9D172E','#86163B','#701447','#591354','#421161','#2B106E','#150F7B']
  bin_construction= ['0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9','0.9-1.0']
  bins = 0.1
  
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

        color = str()
        bin_ratio = 1
        if agency1 in mapPoints['zip_complaints'][currentZip].keys() and agency2 in mapPoints['zip_complaints'][currentZip].keys():
          ratio = mapPoints['zip_complaints'][currentZip][agency1]/((mapPoints['zip_complaints'][currentZip][agency2]+mapPoints['zip_complaints'][currentZip][agency1])*1.0)

        ratios = [ratio]
        #complaintsPerZip1 = [(['zip_complaints'][currentZip][agency1])]
        #complaintsPerZip2 = [(['zip_complaints'][currentZip][agency2])]

        if color != 'white':
          bin_ratio = int(floor(ratio//bins))
          color = colors_palate[bin_ratio]
          ratios = ratio
          #complaintsPerZip1 = complaintsPerZip1
          #complaintsPerZip2 = complaintsPerZip2

      else:
        color = 'white'

      polygons['zip_code'].append(currentZip)
      polygons['color_list'].append(color)
      polygons['bin_ratio'].append(bin_construction[bin_ratio])
      polygons['ratio_num'].append(ratios)
      #polygons['complaintsPerZip1'].append(complaintsPerZip1)
      #polygons['complaintsPerZip2'].append(complaintsPerZip2)

    record_index += 1

  # Creates the Plot
  output_file("ComplaintsRatio.html", title="ComplaintsRatio")
  hold()
  source = ColumnDataSource(data = dict(x = polygons['lat_list'], y =polygons['lng_list'], zip_code = polygons['zip_code'], ratio = polygons['ratio_num'], \
    complaintsPerZip1= polygons['complaintsPerZip1'], complaintsPerZip2= polygons['complaintsPerZip2'], bin_ratio = polygons['bin_ratio'], colors = polygons['color_list']))

  TOOLS="pan,wheel_zoom,box_zoom,reset,previewsave,hover"

  # Creates the polygons.
  patches(polygons['lng_list'], polygons['lat_list'], \
        fill_color=polygons['color_list'], line_color="gray", \
        source = source,\
        tools=TOOLS, plot_width=900, plot_height=700, \
        title="Complaint Comparision for Two Agencies by NYC Zip Code")
        
  for i in xrange(len(polygons['lat_list'])):
    scatter(0,0, color = polygons['color_list'][i], legend = polygons['bin_ratio'][i], loc='best')

  hover = curplot().select(dict(type = HoverTool))

  hover.tooltips = OrderedDict([("Zip Code",'@zip_code'),("Ratio Range",'@bin_ratio'),("Ratio",'@ratio'),("Agency 1",sys.argv[3]),("Agency 2",sys.argv[4])])                
  show()

if __name__ == '__main__':
  if len(sys.argv) != 5:
    print 'Usage:'
    print sys.argv[0] \
    +' <complaintsFilename> <shapeFilename> <Abbreviation for 1st Agency> <Abbreviation for 2nd Agency>'
    print '\ne.g.: ' + sys.argv[0] \
    + ' data:nyc311.csv shapefile:zip_code_040114.shp agency1:HPB agency2:DOB'
  mapPoints = loadComplaints(sys.argv[1])
  drawPlot(sys.argv[2], mapPoints, sys.argv[3], sys.argv[4])
