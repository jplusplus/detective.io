from django.db import models

class QuoteRequest(models.Model):
    RECORDS_SIZE = (
        (0, "Less than 200"),
        (200, "Between 200 and 1000"),
        (1000, "Between 1000 & 10k"),
        (10000, "More than 10k"),
        (-1, "I don't know yet"),
    )
    USERS_SIZE = (
        (1, "1"),
        (5, "1-5"),
        (0, "More than 5"),
        (-1, "I don't know yet"),
    )
    PUBLIC = (
        (True, "Yes, public"),
        (False, "No, just for a small group of users"),
    )
    name     = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    email    = models.EmailField(max_length=100)
    phone    = models.CharField(max_length=100, blank=True, null=True)
    domain   = models.TextField(help_text="Which domain do you want to investigate on?")
    records  = models.IntegerField(choices=RECORDS_SIZE, blank=True, null=True, help_text="How many entities do you plan to store?")
    users    = models.IntegerField(choices=USERS_SIZE, blank=True, null=True, help_text="How many people will work on the investigation?")
    public   = models.NullBooleanField(choices=PUBLIC, null=True, help_text="Will the data be public?")
    comment  = models.TextField(blank=True, null=True, help_text="Anything else you want to tell us?")

    def __unicode__(self):
        return "%s - %s" % (self.name, self.email,)