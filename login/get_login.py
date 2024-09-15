import yaml
import pathlib


def get_email_login():
    with open(pathlib.Path('login.yml'), "r") as f:
        login_data = yaml.safe_load(f)
        return (login_data['email'], login_data['app_password'], login_data['test_recipient'])

def main():
    print(get_email_login())


if(__name__ == '__main__'):
    main()
