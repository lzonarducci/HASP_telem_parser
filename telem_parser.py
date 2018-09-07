'''
This script parses text from the HASP telemetry website and takes the latest 
file and checks to see if new information has been pushed to it. If new 
information was put in the file, it prints it to the command line and saves 
it to a single file. It runs in an infinite loop.
'''

import requests
import re
import urllib
import time

def telem_parser(payload_number, year):

	prev_version = ""
	prev_last_line = ""

        # run indefinitely
	while(True):

		web_text = grab_text_from_website(payload_number, year)

		telem_files = parse_table(web_text)

		(contains_new, new_line_start_pos, telem_array) = check_if_new(payload_number, telem_files, prev_version, prev_last_line, year)

		print(contains_new)

		if (contains_new):

			save_new_text(telem_array, new_line_start_pos)

			prev_version = telem_files[-1]

			prev_last_line = telem_array[-1]

		time.sleep(5)

def grab_text_from_website(payload_number, year):
	# Takes the html plaintext from the laspace hasp website for the given payload number

	page = requests.get("https://laspace.lsu.edu/hasp/groups/{}/data/data.php?pname=Payload_{}&py={}".format(year, payload_number, year))

	return page.text.split("\n")

def parse_table(web_text):
	# takes the html text and creates a list of all the files posted

	table_start_found = False

	files = []

        # grab the files
	for line in web_text:
		if line == "<TABLE class='flightdata'><TR><TH class='flightdata'>Filename</TH><th class='flightdata'>File Date</th><th class='flightdata'>Filesize</th></TR>":
			table_start_found = True
		if table_start_found:
			matched_regex = re.match(r"<TR><TD class='flightdata'><a href=Payload_\d\d/sp\d_\d\d-\d\d-\d\d-\d\d-\d\d-\d\d\.raw>(sp\d_\d\d-\d\d-\d\d-\d\d-\d\d-\d\d\.raw)</a></td><td class='flightdata'>\d\d/\d\d/\d\d \d\d:\d\d:\d\d (A|P)M</td><td class='flightdata'>\d\.?\d KB</td></TR>", line)
			if matched_regex:
				files.append(matched_regex.group(1))

	return files

def parse_telem_file(payload_number, curr_version, year):
	# takes the payload number and the current file and grabs the data

	page = requests.get("https://laspace.lsu.edu/hasp/groups/{}/data/Payload_{}/{}".format(year, payload_number, curr_version))

	return page.text.split("\n")

def check_if_new(payload_number, telem_files, prev_version, prev_last_line, year):
	# checks to see if new data has been added to the current file or if the file is new
	
	# if the program just entered, just grab all the stuff in the latest file:
	if(prev_version == ''):
		print('New instance')
		return (True, 0, parse_telem_file(payload_number, telem_files[-1], year))

        # if there is a new file, go here:
	if (prev_version != telem_files[-1]):
                # check if there is new data in the previous file and grab that
                # along with all of the new file's data
		telem_array = parse_telem_file(payload_number, telem_files[-2], year)
		telem_array_new_file = parse_telem_file(payload_number, telem_files[-1], year)
		for telem in telem_array_new_file:
			telem_array.append(telem)
		for i in range(0, len(telem_array)):
			if (telem_array[i] == prev_last_line):
				if (len(telem_array) > i+1):
					print('New file')
					return (True, i+1, telem_array)
				else:
					# we should never reach here, but it could happen I suppose?
					print('?')
					return (False, -1, telem_array)
			else:
				return (True, 0, telem_array)
	else:
                # file is the same, but contains new data, potentially.
		telem_array = parse_telem_file(payload_number, telem_files[-1], year)
		for i in range(0, len(telem_array)):
			if (type(telem_array[i]) == None):
				print("hello there")
			elif (telem_array[i] == prev_last_line):
				# check if there is a repeat of this line in the rest of the array
				if (len(telem_array) > i+1):
					print('new data')
					return (True, i+1, telem_array)
				else:
                                        # This is to catch if a line exists twice
                                        # from say, if the payload reset recently.
                                        # We want to take the last line of repeated
                                        # lines.
					print(telem_array[i+1:])
					if (prev_last_line in telem_array[i+1:]):
						print('pass')
						continue
				
				return (False, -1, telem_array)

def save_new_text(telem_array, start_pos):
	# prints the new data to command line and saves it to a single text document

	fp = open("telemetry.txt",'a')

	for i in range(start_pos, len(telem_array)):
		print(telem_array[i])
		fp.write(telem_array[i])
