#!/usr/bin/env python

from datetime import datetime
import smtplib
import threading


def add_to_logfile(message):
    '''Opens a logfile and appends the error message to it.'''
    with open('log.txt', 'a') as logfile:
        text = '{0}: {1}\n\n'.format(str(datetime.now()), message)
        logfile.write(text)
        
def send_message(subject, message, thread=False):
    '''Texts me a notification'''
    def send(subject, message):
        username = r'michael0x2a.notifier@gmail.com'
        password = r'HelloWorld'
        target = "michael.lee.0x2a@gmail.com"
        
        full_message = '\n'.join([
            'From: {0}'.format(username),
            'To: {0}'.format(number),
            'Subject: {0}'.format(subject),
            message
        ])
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(10)
        server.starttls()
        server.login(username, password)
        server.sendmail(username, target, message)
        server.quit()
    
    if thread:
        t = threading.Thread(target=send, args=(subject, message))
    else:
        send(subject, message)
    
    
def log(message):
    add_to_logfile(message)
    #send_message('Guerilla Kinect Update', message)
    
    