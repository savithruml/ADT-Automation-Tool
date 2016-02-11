#!/usr/bin/env

import os 
import sys
import csv
import datetime
import logging
import fnmatch
import pysftp
import inform
import requests
import shutil
import time
from time import sleep
from flask import Flask, render_template, request

application = Flask(__name__)
		

def informUser(mail_id, to_number, check_msg, check_call, file_download):
	
	if to_number.startswith('+1'):
		
		if len(check_msg) == 9 and len(check_call) == 9:
			inform.send_mail(mail_id, file_download)
			inform.message_Twilio(to_number)
			inform.call_Twilio(to_number)
					
		elif len(check_msg) == 9 and len(check_call) == 2:
			inform.send_mail(mail_id, file_download)
			inform.message_Twilio(to_number)
						
		elif len(check_msg) == 2 and len(check_call) == 9:
			inform.send_mail(mail_id, file_download)
			inform.call_Twilio(to_number)
						
		else:
			inform.send_mail(mail_id, file_download)
						
	else:
		inform.send_mail(mail_id, file_download)
		
	logging.info('Informed E-Mail Division')
			

def sftpUpload(grp_path):
	
	try:
		os.chdir(grp_path)
		tmp = os.listdir(grp_path)
		srv = pysftp.Connection(host="xfer.dncsolution.com", username="ADTDNE_ZetaInteractive2", password="#VK7JuB*}3W/S-3")

		for file in tmp:
			if file.endswith('.csv'):
				srv.put(grp_path + '/' + file, '/Inbox/' + file)
				logging.info('Uploaded {}'.format(file))
		srv.close()	
			
	except:
		logging.info('Unable to connect to sftp server-Upload Fail')
		

def sftpDownload(file_download):
	
	try:
		srv = pysftp.Connection(host="xfer.dncsolution.com", username="ADTDNE_ZetaInteractive2", password="#VK7JuB*}3W/S-3") 

		while len(srv.listdir('/Inbox')) >= 1:
			time.sleep(90)

		files = srv.listdir('/Outbox')
		for file in files:
			if fnmatch.fnmatch(file, file_download):
				srv.get('/Outbox/' + file) 
				logging.info('Downloaded {}'.format(file))
			else:
				pass
		srv.close()
		
	except:
		logging.info('Unable to connect to sftp server-Download Fail')


def checkFiles(mail_id, to_number, check_msg, check_call, file_download):
	
	tmp_path = '/opt/admin_files/data/'
	os.chdir(tmp_path)
	tmp = os.listdir(tmp_path)
	
	tmp_file = open('GOOD' + file_download + '.log', 'a+')
	
	for files in tmp:
		if files.startswith('GOOD') and files.endswith('.txt'):
			if fnmatch.fnmatch(files, file_download):
				tmp_file.write('/opt/admin_files/data/' + files + '\n')
	
	tmp_file.close()
	tmp_log = 'GOOD' + file_download + '.log'
	
	try:
		shutil.move(tmp_path + tmp_log, '/home-backup/ADT/adt_tools/good_download/')
	except:
		os.remove('/home-backup/ADT/adt_tools/good_download/' + tmp_log)
		shutil.move(tmp_path + tmp_log, '/home-backup/ADT/adt_tools/good_download/')

	informUser(mail_id, to_number, check_msg, check_call, file_download)
	return tmp_log
	

@application.route('/index', methods=['POST', 'GET'])
def date():
	
	file_download = str(request.form['file_download'])
	mail_id = str(request.form['mail_id'])
	to_number = str(request.form['to_number'])
	check_msg = str(request.form.getlist('check1'))
	check_call = str(request.form.getlist('check2'))
	sftpDownload(file_download)
	
	tmp = os.getcwd()
	tmp_dir = os.listdir(tmp)
	os.chdir(tmp)
	
	open('scrub_filenames', 'w').close()
	static_filenames = open('scrub_filenames', 'a+')
	
	for files in tmp_dir:
		if files.startswith('GOOD') and files.endswith('.csv'):
			if fnmatch.fnmatch(files, file_download):
				static_filenames.write(files + '\n')
	static_filenames.close()
	os.system('./unscrub.sh')
	time.sleep(10)
	logging.info('Executed "./unscrub.sh"')
	tmp_log_return = checkFiles(mail_id, to_number, check_msg, check_call, file_download)
	return render_template('index.html', tmp_file_download = '/home-backup/ADT/adt_tools/static/' + tmp_log_return)
				
	
@application.route('/date', methods=['POST', 'GET'])
def index():
	
	file_upload = str(request.form['file_upload'])
	file_groups = str(request.form['file_groups']).upper()
	scrub_value = str(request.form.getlist('scrub_value'))
	#print len(scrub_value)
	
	file_upload_tmp = file_upload.split(',')
	file_groups_tmp = file_groups.split(',')
	upload_tmp = [x.strip(' ') for x in file_upload_tmp]
	groups_tmp = [y.strip(' ') for y in file_groups_tmp]
	
	for group in groups_tmp:
		grp_path = '/home-backup/ADT/group' + group
		os.chdir(grp_path)
		os.system('rm -rf ADT* && rm -rf GOOD*')
		open('filenames', 'w').close()
		for file in upload_tmp:
			filename = open('filenames', 'a+')
			filename.write(file + '\n')	
		filename.close()
		
		if len(scrub_value) == 10:
			os.system('./scrub.sh')
			logging.info('Executed "./scrub.sh"')
			os.system('./scrub_static_today.sh')
			logging.info('Executed "./scrub_static_today.sh"')
			sftpUpload(grp_path)	
			
		elif len(scrub_value) == 11:
			os.system('./scrub.sh')
			logging.info('Executed "./scrub.sh"')
			os.system('./scrub_static_oneday.sh')
			logging.info('Executed "./scrub_static_oneday.sh"')
			sftpUpload(grp_path)
			
		elif len(scrub_value) == 12:
			os.system('./scrub.sh')
			logging.info('Executed "./scrub.sh"')
			os.system('./scrub_static_twoday.sh')
			logging.info('Executed "./scrub_static_twoday.sh"')
			sftpUpload(grp_path)
			
		elif len(scrub_value) == 13:
			os.system('./scrub.sh')
			logging.info('Executed "./scrub.sh"')
			os.system('./scrub_static_threeday.sh')
			logging.info('Executed "./scrub_static_threeday.sh"')
			sftpUpload(grp_path)
			
		elif len(scrub_value) == 14:
			os.system('./scrub.sh')
			logging.info('Executed "./scrub.sh"')
			os.system('./scrub_static_fourday.sh')
			logging.info('Executed "./scrub_static_fourday.sh"')
			sftpUpload(grp_path)
			
		else:
			return render_template('error.html')
			
	return render_template('date.html')
		

@application.route('/login', methods=['POST', 'GET'])
def login():
	
	usr_name = str(request.form['username'])
	usr_pass = str(request.form['password'])
	
	if usr_name == 'admin' and usr_pass == 'ChangeMe123':
		return render_template('ipcomm.html')
	else:
		return render_template('loginfail.html')

@application.route('/')
def main():
	
	logging.basicConfig(level=logging.INFO, filename='status.log', 
					     format='%(asctime)s %(message)s')
	
	return render_template('login.html')

if __name__ == '__main__':
    application.run(debug=True)