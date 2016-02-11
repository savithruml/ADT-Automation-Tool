import os
import datetime
import smtplib
from twilio.rest import TwilioRestClient
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def send_mail(mail_id, file_download):
	
	os.chdir('/home-backup/ADT/adt_tools')
	sender_mail = ''
	receiver_mail = mail_id
	mesg = '\nBelow are the scrubbed files\n'
    
	try:
		msg = MIMEMultipart()
		msg['From'] = ''
		msg['To'] = 'E-Mailers'
		msg['Subject'] = 'IMPORTANT: ADT Scrub Process Completed'
		msg.attach(MIMEText(mesg, 'plain'))
		msg.attach(MIMEText(file("/home-backup/ADT/adt_tools/good_download/GOOD" + file_download + ".log").read()))
		smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
		smtp_session.ehlo()
		smtp_session.starttls()
		smtp_session.ehlo()
		smtp_session.login(sender_mail, '')
		smtp_session.sendmail(sender_mail, receiver_mail, msg.as_string())
		smtp_session.quit()
		print '\nDone Processing! Access files here: /opt/admin_files/data/'
		

	except smtplib.SMTPException:
		print 'Failed sending mail'
	
	
def message_Twilio(to_number):

    sid = ""
    token = ""

    client = TwilioRestClient(sid, token)
    body = '\nADT FILE SCRUB COMPLETED'
    
    client.messages.create(to = to_number, from_= '',
                            body=body,)

def call_Twilio(to_number):
	
	sid = ""
	token = ""

	client = TwilioRestClient(sid, token)
	
	url_msg = 'http://twimlets.com/message?Message%5B0%5D=Attention%20E-mailers%20this%20is%20an%20automated%20message%20from%20the%20IT%20department.%20The%20ADT%20Scrub%20Process%20has%20been%20Completed&'
	#'http://twimlets.com/message?Message%5B0%5D=Attention%20E-mailers%2C%20ADT%20Scrub%20Process%20has%20been%20Completed&'

	call = client.calls.create(to='', from_='',
			url=url_msg, method='GET', fallback_method='GET',
			status_callback_method='GET', record='false')

def main():
	
	pass

if __name__ == '__main__':
    main()
