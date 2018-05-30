# This script updates fields in XML metadata (FGDC standard tags), that was originally created in ArcCatalog
# for county data geodatabases and shapefiles. 

import os
import openpyxl
import time
import contactdb

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
	


def get_cname(root):#get county name from xml file
	for fname in root.iter('enttypl'):
		file_name = fname.text
		file_list = file_name.split('_')
		county_name=file_list[0]
		return county_name.strip('\n')

def change_links(root):	#iterate over the sub-elements within the citation element and change link to public
    for elem in root.iter('onlink'):
            if ('UW' in elem.text): #if the link contains 'UW_System' 
            #take what is after UW_System/ ie the file name and append it to the public_link variable
                    for fname in root.iter('enttypl'):
                            file_name = fname.text
                            new_link = 'https://gisdata.wisc.edu/public/' + file_name + '.zip'
                    elem.text = new_link #change link to public version
def update_purpose(root): #remove restrictions from 'purpose' section of metadata
	for elem in root.iter('purpose'):
		p = elem.text
		if ('faculty' in p):
			elem.text = 'This layer is intended for reference and mapping purposes, and may be used for basic applications such as viewing, querying, and map output production, or to provide a basemap to support graphical overlays and analysis with other spatial data.'		
def remove_restrictions(root): #remove usage restrictions from metadata
	for elem in root.iter('accconst'):
		if('Access is granted to licensee only' in elem.text):
			elem.text = '' 
	for elem in root.iter('useconst'):
		if('For educational noncommercial use only' in elem.text):
			elem.text = '' 
def add_lang(root):#add note about update in supplimental info section
	for elem in root.iter('descript'):
		test = elem.find('supplinf')
		if test is None: #if no supplimental information add necessary metadata update note
			add = ET.SubElement(elem,'supplinf')
			t = 'This metadata was updated in fall of 2017 to reflect that the data is no longer restricted and has been opened for public use.'
			elem.find('supplinf').text = t
		else: #if supplimental information already exists, append metadata update not to existing info
			info = elem.find('supplinf').text
			newInfo = info + ' This metadata was updated in fall of 2017 to reflect that the data is no longer restricted and has been opened for public use.'
			elem.find('supplinf').text = newInfo
def ch_pub_date(root):
	for elem in root.iter('pubdate'):
		elem.text = time.strftime('%Y%m%d')		
def add_link(county_name,root):#if county now has a website, get county url from excel sheet and add to metadata			
	from openpyxl import load_workbook
	try:
		wb = load_workbook(filename='P:\\Operation_Unrestrict\\1Tools_Docs_Test_Other\\OpenData_urls.xlsx', read_only=True)
		ws = wb['Sheet1']
	except IOError:
		print "Excel url file cannot be found."
	url_dict={}
	for row in ws.rows: #make dictionary with county name as key and website url as value
		url_dict[row[0].value]=row[1].value
	url_dict={str(k): str(v) for k, v in url_dict.items()}
	if county_name in url_dict:
		url = url_dict[county_name]
		for elem in root.iter('citeinfo'):
			ET.SubElement(elem, 'onlink').text = url
def update_contacts(county_name,root):
        for elem in root.iter('ptcontac'):
            for tag in elem.iter('cntper'):
                tag.text = counties[county_name.lower().strip()]['contactName'].encode('ascii', 'ignore')
            for tag in elem.iter('cntvoice'):
                tag.text = counties[county_name.lower().strip()]['phone'].decode('ascii','ignore')
            for tag in elem.iter('cntemail'):
                tag.text = counties[county_name.lower().strip()]['email'].decode('ascii','ignore')           
def open_files(input, output):
	if os.path.isfile(input):
		try:
			tree=ET.ElementTree(file=input)
			root = tree.getroot()
			print 'processing file...'
			change_links(root)
			update_purpose(root)
			remove_restrictions(root)
			add_lang(root)
			ch_pub_date(root)
			add_link(get_cname(root),root)
			update_contacts(get_cname(root),root)
			for fname in root.iter('enttypl'):
				file_name = fname.text.replace('\n', '').replace('\r', '') + '.xml'
			try:
				tree.write(os.path.join(output, file_name))
				print 'Updates complete for', file_name
			except IOError: print 'Cound not write file.'
		except IOError: print "Input file cannot be found."		
	elif os.path.isdir(input):
		try:
			os.chdir(input)
		except IOError: print 'Input folder cannot be found.'
		try:
			for filename in os.listdir(input):
				tree=ET.ElementTree(file=filename)
				root = tree.getroot()
				change_links(root)
				update_purpose(root)
				remove_restrictions(root)
				add_lang(root)
				ch_pub_date(root)
				add_link(get_cname(root),root)
				update_contacts(get_cname(root),root)
				for fname in root.iter('enttypl'):
					file_name = fname.text.replace('\n', '').replace('\r', '') + '.xml'
				try:
					tree.write(os.path.join(output, file_name))
					print 'Updates complete for', file_name
				except IOError: print 'Cound not write file named' + file_name
		except: print filename + ' in ' + input + ' directory could not be processed.'
		
	else: 
		print 'That is neither a folder nor a file. Please try again'
		input_f=raw_input('Drag folder or file here and hit enter:')	
		save_f=raw_input('What folder would you like to save this file in? Drag folder here and hit enter:')
		open_files(input_f, save_f)
		
if __name__ == "__main__":
    
    counties = contactdb.makeCountyDb('http://www.wlion.org/LIOs')
            
    
    
    input_f= raw_input('Drag folder or file here and hit enter:')	
    save_f= raw_input('What folder would you like to save this file in? Drag folder here and hit enter:')
    print 'preparing to process file/s'
    open_files(input_f, save_f)

