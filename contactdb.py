#! /usr/local/bin
# -*- coding: utf-8 -*- 
import bs4 
from datetime import datetime
import requests, re
from unicodedata import normalize

adregex = re.compile(r"((\w+)( \w+)?\s?),\s?(WI)\s?(\d\d\d\d\d(-\d\d\d\d)?)")

# create parseable soup object from the url
def getSoup(url):

  # get target webpage and check for status
  res = requests.get(url)
  try:
    res.raise_for_status()
  except Exception as exc:
    print('There was a problem: %s' % (exc))

  # create soup obj and return
  soup = bs4.BeautifulSoup(res.text, "html.parser")
  return soup

# get information contained in row div
# this function has more robust error handling than the others
# generally it is better that the program crash catastrophically
# this error handling was initially developed to save time
def parseRow(row):
  
  field = row.strong.text.lower()
  county = field[:-7]

  # get contact name
  try:
    contact = row.span.text
  except:
    contact = row.text.split("\r\n")[1]
    

  contactList = contact.split("-")
  contactName = contactList[0].strip()
  if len(contactList) > 1:
    contactTitle = contactList[1].strip()
  else:
    contactTitle = ""

  # structure data and return
  line = [county, contactName, contactTitle]
  clean = encode_ascii(line)
  return clean

# get information containted in panel div
def parsePanel(panel, county_code):
  
  # get address
  main = panel.select("address")
  primary = main[0]
  panel_list = []
  for item in primary.contents:
    # here we weed for dumb characters and empty strings
    if item.string != None:
      string = item.string.strip()
      if not string or string == '(':
        continue
      else:
        panel_list.append(string)
    else:
      continue

  # extract phone number 
  phone = panel_list[len(panel_list)-1]
  panel_list.remove(panel_list[len(panel_list)-1])
  if phone[0] != '(':
    phone = '(' + phone
  
  # build address 
  address = []
  for item in panel_list:
    address.append(item.strip())
    
  # TODO: split address into fields for address[list] city_name, postal_code.
  """
  print(address[len(address)-1].encode("ascii", "ignore"))
  res = adregex.search(address[len(address)-1].encode("ascii", "ignore"))
  print(res.group(1))
  """
  
  # get footer items
  footer = panel.select('.panel-footer a')
  website = footer[0].contents[0]
  email = footer[1].contents[0]

  # structure data and return
  line = [address, phone, website, email]
  clean = encode_ascii(line)
  return clean

# structure individual county data
def buildCounty(rowList, panelList):
  
  # assemble data and return
  county = {
    'countyName': rowList[0], 
    'contactName': rowList[1],
    'contactTitle': rowList[2],
    'address': panelList[0], 
    'phone': panelList[1], 
    'website': panelList[2], 
    'email': panelList[3]
  }
  return county

# call relavent functions to assemble datatbase
# this fuction should be called from the outside to with the url as arg[0]
def makeCountyDb(url):

  # create soup obj
  soup = getSoup(url)
  res = soup.find_all(attrs={'class': 'user-row'})

  #for row in res:
    #print(row)

  # initialize database
  counties = {}

  # iterate over table rows
  for row in res:

    # call fucitons to get row and panel information as strings
    rowList = parseRow(row)
    county_code = re.sub(r' ', r'', rowList[0])
    if county_code == "menomine":
      county_code = "menominee"
    panel = soup.find(attrs={'class': county_code})
    panelList = parsePanel(panel, county_code)

    # call fuction to assemble dictionary from strings and add to database
    county = buildCounty(rowList, panelList)
    counties[rowList[0]] = county

  return counties

def encode_ascii(line):

  clean = []
  for item in line:
    if isinstance(item, list):
      sub_list = []
      for i in item:
        sub_list.append(i.encode("ascii", "ignore"))
      clean.append(sub_list)
    else:
      clean.append(item.encode("ascii", "replace").replace("?", " "))
      
  return clean

# main branch if script is called directly 
if __name__ == "__main__":

  # initialize time reporting
  start = datetime.now()

  # hardcoded url for runing as __main__
  url = 'http://www.wlion.org/LIOs'
  
  # call cor function
  counties = makeCountyDb(url)

  # report runing time and useage info
  time = (datetime.now() - start)
  
  print("LIO contact information structured in %s" %(time))
  print("Useage: counties['county name']['desired field']")

    
  
    




        


