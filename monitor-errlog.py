
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import subprocess

def send_email():
	to_address = "XXX@XXX.com"
	from_address = "ZZZ@ZZZ.com"
	cc_address = ""
	subject = "Urgent Errors in the Universe Errlog"

	cmd = "strings {} {} | mail -s '{}' -r {} {}".format(hold, errlog, subject, from_address, to_address)
	ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

	logger.info("Urgent Errors - Sent e-mail")
	logger.info(subprocess.STDOUT)

SEND_ON_CHANGE = True
if SEND_ON_CHANGE:
	errlog_md5_path = "/tmp/errlog_md5.txt"
	if not os.path.exists(errlog_md5_path):
		errlog_md5_file = open(errlog_md5_path,"w")
		errlog_md5_file.close()

else:
	# Things to monitor for - Either reads from a file or hardcoded
	watch_words_path = "/path/to/watch_words.txt"
	if os.path.exists(watch_words_path):
		with open(watch_words_path, "r") as f:
			content = f.readlines()
		watch_words = [line.strip() for line in content]

	else:
		watch_words = [
    		"Unable to load subroutine",
    	]


error = ''
errlog = "/usr/uv/errlog"
hold = "/tmp/send-errorlog.txt"
log = "/home/logs/send-errlog.log"

if not os.path.exists(log):
	log_file = open(log,"w")
	log_file.close()

# Set up a log file that automatically makes copies of itself at 10kb and only keeps the last 5
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(log, maxBytes=10240, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(handler)

# If there is an errlog
if os.path.exists(errlog):

	# Send Errlog if there are any changes
	if SEND_ON_CHANGE:
		with open(errlog_md5_path,"r+") as f:
			old_hash = f.read()
			errlog_file = open(errlog,"rb")
			new_hash = hashlib.md5(errlog_file.read()).hexdigest()
			errlog_file.close()
			if old_hash != new_hash:
				send_email()
				f.seek(0)
				f.truncate()
				f.write(new_hash)

			else:
				logger.info("No Errors.")

	else:
		# Check each line of the errlog and find the latest error
		with open(errlog) as errlog_file:
			for line in errlog_file:
				if any(word in line for word in watch_words):
					error = line.strip()

		if error:
        	# If the hold file doesn't exist, create it
			if not os.path.exists(hold):
				hold_file = open(hold,"w")
				hold_file.close()

			with open(hold, "r+") as hold_file:
				line = hold_file.read()
    
				# If we have a new error then send an e-mail and update what we have on file
				if line.strip() != error:
					send_email()

					hold_file.seek(0)
					hold_file.truncate()
					hold_file.write(error)
		else:
			logger.info("No Errors.")
