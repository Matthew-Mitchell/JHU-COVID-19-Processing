
from datetime import date, timedelta, datetime
import re

flask_base_dir = '/home/matt/Documents/Projects/WebDev/mmitchell_net/FlaskApp/'

#New Data
flask_data_dir = flask_base_dir + 'static/data/'

yesterday = datetime.now()-timedelta(1)
data_filename = 'Confirmed_Cases_through_{}.csv'.format(yesterday.strftime('%b%d'))

#New Line Graph Image
flask_img_dir = flask_base_dir + 'static/images/covid19/'
line_graph_filename = 'Line_Chart_by_Country_{}.png'.format(yesterday.strftime('%b%d'))

now = datetime.now().strftime('%m/%d/%y %I:%M%p')

pageFile = flask_base_dir + 'templates/corona.html'
with open(pageFile) as f:
	    contents = f.readlines()
	    for i, line in enumerate(contents):
	        if '.csv' in line:
	        	to_replace = re.findall('Confirmed_Cases_through_.*[.]csv', line)[0]
	        	contents[i] = line.replace(to_replace, data_filename)
	        elif 'Line_Chart_by_Country' in line:
	        	to_replace = re.findall('Line_Chart_by_Country_.*[.]png', line)[0]
	        	contents[i] = line.replace(to_replace, line_graph_filename)
	        elif 'Updated on' in line:
	        	to_replace = re.findall('Updated on .* EST', line)[0]
	        	newText = 'Updated on ' + now + ' EST'
	        	contents[i] = line.replace(to_replace, newText)
print('Updating Webpage.')
print('New Line Graph:', line_graph_filename)
print('New Data File:', data_filename)
print('Updated at:', now)
# # Update HTML Contents
f = open(pageFile, "w")
f.writelines(contents)
f.close() 