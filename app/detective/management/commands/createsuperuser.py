from django.contrib.auth.management import get_default_username
from django.core                    import exceptions
from django.core.management.base    import BaseCommand
from django.utils.translation       import ugettext as _
from neo4django.auth.models         import User

import getpass
import re
import sys


RE_VALID_USERNAME = re.compile('[\w.@+-]+$')

EMAIL_RE = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain

def is_valid_email(value):
    if not EMAIL_RE.search(value):
        raise exceptions.ValidationError(_('Enter a valid e-mail address.'))

class Command(BaseCommand):
    help = ""    

    def handle(self, *args, **options):
        default_username = get_default_username()
        try:
            # Get a username
            while 1:
                input_msg = 'Username'
                if default_username:
                    input_msg += ' (leave blank to use %r)' % default_username
                username = raw_input(input_msg + ': ')

                if default_username and username == '':
                    username = default_username

                if not RE_VALID_USERNAME.match(username):
                    sys.stderr.write("Error: That username is invalid. Use only letters, digits and underscores.\n")
                    username = None
                    continue
                try:
                    User.objects.get(username=username)
                except User.DoesNotExist:
                    break
                else:
                    sys.stderr.write("Error: That username is already taken.\n")
                    username = None

            # Get an email
            while 1:
                email = raw_input('E-mail address: ')
                try:
                    is_valid_email(email)
                except exceptions.ValidationError:
                    sys.stderr.write("Error: That e-mail address is invalid.\n")
                    email = None
                else:
                    break

            # Get a password
            while 1:                
                password = getpass.getpass()
                password2 = getpass.getpass('Password (again): ')
                if password != password2:
                    sys.stderr.write("Error: Your passwords didn't match.\n")
                    password = None
                    continue
                if password.strip() == '':
                    sys.stderr.write("Error: Blank passwords aren't allowed.\n")
                    password = None
                    continue
                break
                
        except KeyboardInterrupt:
            sys.stderr.write("\nOperation cancelled.\n")
            sys.exit(1)

        User.objects.create_superuser(username, email, password)
        self.stdout.write("Superuser created successfully.\n")