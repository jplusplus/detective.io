from django.core.mail import EmailMultiAlternatives, get_connection, send_mail


from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.core import signing
from django.template import loader
from django.views import generic

from password_reset.forms import PasswordRecoveryForm
from password_reset.views import Reset


# Monkey patching for Recover (took from `password_reset.views`), now it use the
# newest version of send_mail, see below
class SaltMixin(object):
    salt = 'password_recovery'
    url_salt = 'password_recovery_url'

class Recover(SaltMixin, generic.FormView):
    case_sensitive = True
    form_class = PasswordRecoveryForm
    template_name = 'password_reset/recovery_form.html'
    email_template_name = 'password_reset/recovery_email.txt'
    email_subject_template_name = 'password_reset/recovery_email_subject.txt'
    search_fields = ['username', 'email']

    def get_success_url(self):
        return reverse('password_reset_sent', args=[self.mail_signature])

    def expires(self):
        # returns the number of days for token validity
        return Reset().token_expires / (24 * 3600)

    def send_notification(self):
        context = {
            'site':   RequestSite(self.request),
            'user':   self.user,
            'token':  signing.dumps(self.user.pk, salt=self.salt),
            'secure': self.request.is_secure(),
            'expiration_days': self.expires()
        }
        body = loader.render_to_string(self.email_template_name,
                                       context).strip()
        subject = loader.render_to_string(self.email_subject_template_name,
                                          context).strip()
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                  [self.user.email])
