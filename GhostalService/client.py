import sys
import smtplib
import datetime

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT   = 587
DEBUG_MODE  = True

class SMTPMessage(str):

    def __new__(cls, to_addr, from_addr, content, subject='', bcc='', cc=''):

        from_addr = 'From: %s\r\n' % (from_addr) if from_addr else ''
        to_addr = 'To: %s\r\n' % (to_addr) if to_addr else ''
        cc = 'CC: %s\r\n' % (cc) if cc else ''
        bcc = 'BCC: %s\r\n' % (bcc) if bcc else ''
        subject = 'Subject: %s\r\n\n' % (subject) if subject else ''
        now = datetime.datetime.now()
        date = '%d/%d/%d' % (now.month, now.day, now.year)

        msg_str = ''.join([from_addr, to_addr, cc, bcc, subject, content])
        return str.__new__(cls, msg_str)

class SMTPBatchClient(smtplib.SMTP):

    def __init__(self, srv_name, srv_port, username=None, password=None, debug=False):

        ''' initial setup '''
        smtplib.SMTP.__init__(self, srv_name, srv_port)
        self.set_debuglevel(debug)

        ''' initiate smtp conversation '''
        try:
            self.ehlo()
        except smtplib.SMTPException:
            self.helo()

        ''' begin encryption '''
        try:
            self.starttls()
            ''' login if all credentials provided '''
            if all([username is not None, password is not None]):
                self.login(username, password)
                self._username = username
            elif any([username is not None, password is not None]):
                raise smtplib.SMTPAuthenticationError
        except smtplib.SMTPException:
            pass



        self._content = ''
        self._subject = ''

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def setcontent(self, content, subject=''):
        self._content = content
        self._subject = subject

    def fsetcontent(self, content_file, subject=''):
        with open(content_file) as input_handle:
            self._content = input_handle.read()
        self._subject = subject

    def _sendhelper(self, addr_gen, from_addr=None):

        if self._content == '':
            raise Exception('Content unset. Please call setcontent() before sending mail.')

        if from_addr is None:
            from_addr = self._username

        content, subject = (self._content, self._subject)
        for to_addr in addr_gen:
            msg = SMTPMessage(to_addr, from_addr, content, subject)
            self.sendmail(from_addr, [to_addr], msg)

    def sendall(self, to_addrs, from_addr=None):

        if type(to_addrs) == type(''):
            to_addrs = [to_addrs]

        self._sendhelper((a for a in to_addrs), from_addr)

    def fsendall(self, addr_file, from_addr=None):

        with open(addr_file) as input_handle:
                self._sendhelper((line.rstrip() for line in input_handle), from_addr)

if __name__ == '__main__':

    ''' parse command line arguments '''
    username  = sys.argv[1]
    password  = sys.argv[2]

    to_addrs = ['', '']
    addr_file = 'addrs.txt'
    content = 'testing python3 smtplib...\nhey look its an email!'
    subject = 'testing python3 smtplib'
    content_file = 'content.txt'

    with SMTPBatchClient(SMTP_SERVER, SMTP_PORT, username, password, debug=True) as con:

        ''' set content '''
        con.setcontent(content) 

        ''' send an email to a single recipient ''' 
        con.sendall(to_addrs[0])
    
        ''' set content and subject'''
        con.setcontent(content, subject) 

        ''' send an email to a single recipient ''' 
        con.sendall(to_addrs[0])
        
        ''' set content from file'''
        con.fsetcontent(content_file)

        ''' send an email to multiple recipients ''' 
        con.sendall(to_addrs)

        ''' set content from file and set subject '''
        con.fsetcontent(content_file, subject)

        ''' send an email to multiple recipients from an address file '''
        con.fsendall(addr_file)
