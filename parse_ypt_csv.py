import argparse
import csv
import pathlib
import rich
import datetime
import regex as re

import yaml
import pathlib


from email_handling.send_email import send_email
from login.get_login import get_email_login

class Leader:
    def __init__(self, name, email, expiration):
        self.name = name
        self.email = email
        self.expiration = expiration

    def __str__(self) -> str:
        string_rep = f'{self.name} {self.email} {self.expiration}'
        return string_rep
    
    def as_email_recipient(self) -> str:
        string_rep = f'{self.name} <{self.email}>'
        return string_rep

class ypt_report:
    def __init__(self, csv_file:pathlib.Path, excluded_leaders = [], signature="YIS,\nI forgot to fill out the signature in my config.yml file ;)"):
        # assert (csv_file.is_file() == True), "invalid path to CSV"
        f = csv_file.open("r")
        lines = f.readlines()

        self.excluded_leaders = excluded_leaders
        self.signature = signature
        
        self.parse_and_trim_header(lines)

        # reader = csv.DictReader(self.lines)
        # for row in reader:
        #     print(row)

    def parse_and_trim_header(self, lines):
        # We need to grab the organization name and the date the report was generated.
        re_org_name = re.compile("Organization Name: ((.*) (\d+), .*)$")
        trim_before_index = 0
        for (i, line) in enumerate(lines):
            match_org = re_org_name.search(line)
            if match_org:
                self.org_name = match_org.group(1)  # This is the combined organization name including the chartered organization.
                self.unit_type = match_org.group(2) # Pack, troop, crew, etc
                self.unit_number = int(match_org.group(3)) # Unit number converted to an integer to avoid inserting leading zeroes later
                trim_before_index = i + 1
                break
        
        lines = lines[trim_before_index:]                

        re_date_generated = re.compile("Date Report Generated: (.*)$")
        for (i, line) in enumerate(lines):
            match = re_date_generated.search(line)
            if match:
                self.date_generated = match.group(1)
                trim_before_index = i + 3 # There are two extra lines that we don't need after the date line
                break
        
        lines = lines[trim_before_index:]

        print(self.org_name)
        print(f'Generated on {self.date_generated}')

        self.trained_leaders = []
        self.leaders_who_need_ypt = []

        reader = csv.DictReader(lines)
        ypt_cutoff = datetime.date(2026, 1, 1)
        for row in reader:
            ypt_expiration = row["Y01_Expires"]
            name = row["First_Name"] + ' ' + row["Last_Name"]

            if(name in self.excluded_leaders):
                print(f'Excluding {name} from report')
                continue
            email = row["Email_Address"]
            exp_month = int(ypt_expiration[0:2])
            exp_day = int(ypt_expiration[3:5])
            exp_year = int(ypt_expiration[6:10])
            try:
                ypt_exp_date = datetime.date(exp_year, exp_month, exp_day)

            except:
                print(f'*Error* {exp_year}, {exp_month}, {exp_day}')
            leader = Leader(name, email, ypt_exp_date)
            
            if(ypt_exp_date < ypt_cutoff):
                self.leaders_who_need_ypt.append(leader)
            else:
                self.trained_leaders.append(leader)
            
            # print(f'{name:20}{ypt_expiration}  {email}')
    
    # Amanda C <scoutmamabear613@gmail.com>, Nicole Sousa <activia@hotmail.com>, "lisa.ericson@gmail.com" <lisa.ericson@gmail.com>, Laura Wang <heidtlau@gmail.com>, "bpgalante@gmail.com" <bpgalante@gmail.com>
    def get_leader_email_lists(self) -> dict:
        leader_emails = {}
        leader_emails['trained'] = []
        leader_emails['needYPT'] = []

        for leader in self.trained_leaders:
            leader_emails['trained'].append(leader.as_email_recipient())
        
        for leader in self.leaders_who_need_ypt:
            leader_emails['needYPT'].append(leader.as_email_recipient())

        return leader_emails
    
    def __str__(self) -> str:
        string_rep = "Trained leaders:\n"
        for leader in self.trained_leaders:
            string_rep += f'{leader}\n'

        
        string_rep += "\nLeaders who need YPT:\n"
        for leader in self.leaders_who_need_ypt:
            string_rep += f'{leader}\n'

        trained_count = len(self.trained_leaders)
        untrained_count = len(self.leaders_who_need_ypt)
        total_count = trained_count + untrained_count
        percent_trained = (trained_count / total_count) * 100
        string_rep += f'\n{trained_count}/{total_count} leaders trained ({percent_trained:.0f}%)\n'
        return string_rep
    
    def send_ypt_reminder_emails(self, test_only=False):
        (sender, password) = get_email_login()

        subject = f'[{self.unit_type} {self.unit_number} Training] YPT Recertification Reminder'

        leader:Leader
        for leader in self.leaders_who_need_ypt:
            email_body =  f'Hello {leader.name},\n'
            email_body += f'This is an automated reminder that your YPT certification expires on {leader.expiration} and needs to be retaken before Nov 1, 2024.'
            email_body += f'\nPlease log in to my.scouting.org and find the YPT course in the training center.\n'
            email_body += f'Thank you!\n\n'
            email_body += self.signature

            if(test_only):
                print("\n** TEST - EMAIL NOT SENT **")
                print(f'subject:{subject}')
                print(f'from:{sender}')
                print(f'to:{leader.as_email_recipient()}')
                print(f'body:\n{email_body}')

            else:
                send_email(subject=subject,
                            body = email_body,
                            sender = sender,
                            recipients = [leader.as_email_recipient()],
                            password = password)
            
                print(f'Reminder email sent to {leader.as_email_recipient()}\n')    
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", required=True, help="Path to a CSV report downloaded from the BSA YPT report tool")
    parser.add_argument("-e", "--email", action='store_true', help="Email leaders who need to complete YPT")
    parser.add_argument("-t", "--test", action='store_true', help="Print out details without actually sending any emails, if combined with the -e/--email flag")

    args = parser.parse_args()

    config = None
    with open(pathlib.Path('config.yml'), "r") as f:
        config = yaml.safe_load(f)

    report = ypt_report(pathlib.Path(args.filename), excluded_leaders=config['excluded-leaders'], signature=config['sender-signature'])

    print(f'\n{report}')

    print('Emails of leaders who need YPT:\n')

    need_YPT_emails = report.get_leader_email_lists()['needYPT']
    print(need_YPT_emails)

    if(args.email):
        print(f'Sending reminder emails to {len(need_YPT_emails)} leaders...\n')
        report.send_ypt_reminder_emails(test_only = args.test)

    

    pass

if(__name__ == "__main__"):
    main()