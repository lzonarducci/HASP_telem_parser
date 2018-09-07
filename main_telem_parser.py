'''
This software was developed by Lorenzo Narducci at the University of Maryland
for the purpose of parsing the LSU HASP webpage for new telemetry data. You can
modify and adjust the program as needed to suit your own purposes. All additions
to the main code base are subject to the proper code reviews.

Collaborators:


Known Issues:
Randomly fails with a NoneType (NULL Pointer exception)

HowTo:
Run the main_telem_parser script with the telem_parser script in the same
folder. Follow the prompts in the command line. Valid payload numbers are 1-16
and any year can be input, though the program will not work if an incorrect year
is put in. The parser will run indefinitely until there is an input to the
command line, on which, it will terminate.
'''



import telem_parser
from multiprocessing import Process

def main():

	invalid = True

        # get the payload number
	while(invalid):
		payload_number = int(input("Enter your payload number: "))
		if (payload_number > 0 and payload_number < 17):
			invalid = False

	if payload_number < 10:
		payload_number = '0' + str(payload_number)
	else:
		payload_number = str(payload_number)

        # get the year
	year = int(input("Enter year: "))

        # start the parsing process, run until a command line input is received
	p = Process(target=telem_parser.telem_parser, args=(payload_number, year))

	p.start()

	input("")

	p.terminate()

if __name__ == "main":
	main()
