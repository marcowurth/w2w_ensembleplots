############################################################################
###  script that tests if entry in last error logfile                    ###
###  send the error message per mail                                     ###
############################################################################

import os
import datetime
import smtplib
from email.mime.text import MIMEText


def main():

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',\
                logs = 'logs/errors/',
                mail_account = 'additional_data/')

    with open(path['base'] + path['mail_account'] + 'mail_account_marco.txt', 'r') as f:
        lines = f.readlines()
        mail = lines[0][:-1]
        password = lines[1][:-1]

    for filename in os.listdir(path['base'] + path['logs']):
        if os.stat(path['base'] + path['logs'] + filename)[6] > 0:
            # send mail with error message of the error logfile:
            d = datetime.datetime.utcfromtimestamp(\
                 os.stat(path['base'] + path['logs'] + filename)[8])
            with open(path['base'] + path['logs'] + filename, 'r') as logfile:
                msg = MIMEText(logfile.read())
            msg['Subject'] = 'Error in LSDF cronjob on {:02}.{:02}.{} {:02}:{:02}UTC'.format(\
                                d.day, d.month, d.year, d.hour, d.minute)
            msg['From'] = mail
            msg['To'] = mail

            s = smtplib.SMTP('smtp.kit.edu', 587)
            s.starttls()
            s.login(mail, password)
            s.sendmail(mail, mail, msg.as_string())
            s.quit()

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    main()
