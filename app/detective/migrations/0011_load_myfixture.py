# -*- coding: utf-8 -*-
from south.v2    import DataMigration

class Migration(DataMigration):

    def forwards(self, orm):
        fixtures = [
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "personal_payer",
                    "subject": "FundraisingRound",
                    "label": "was financed by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "payer",
                    "subject": "FundraisingRound",
                    "label": "was financed by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "educated_in",
                    "subject": "Person",
                    "label": "was educated in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "based_in",
                    "subject": "Person",
                    "label": "is based in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "activity_in_organization",
                    "subject": "Person",
                    "label": "has activity in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "previous_activity_in_organization",
                    "subject": "Person",
                    "label": "had previous activity in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "price",
                    "subject": "EnergyProduct",
                    "label": "is sold at"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "author",
                    "subject": "Commentary",
                    "label": "was written by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "distribution",
                    "subject": "EnergyProduct",
                    "label": "is distributed in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "operator",
                    "subject": "EnergyProduct",
                    "label": "is operated by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "price",
                    "subject": "EnergyProduct",
                    "label": "is sold at"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "adviser",
                    "subject": "Organization",
                    "label": "is advised by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "key_person",
                    "subject": "Organization",
                    "label": "is staffed by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "partner",
                    "subject": "Organization",
                    "label": "has a partnership with"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "fundraising_round",
                    "subject": "Organization",
                    "label": "was financed by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "monitoring_body",
                    "subject": "Organization",
                    "label": "is monitored by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "litigation_against",
                    "subject": "Organization",
                    "label": "has a litigation against"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "revenue",
                    "subject": "Organization",
                    "label": "has revenue of"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "board_member",
                    "subject": "Organization",
                    "label": "has board of directors with"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "commentary",
                    "subject": "EnergyProject",
                    "label": "is analyzed by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "owner",
                    "subject": "EnergyProject",
                    "label": "is owned by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "partner",
                    "subject": "EnergyProject",
                    "label": "has a partnership with"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "activity_in_country",
                    "subject": "EnergyProject",
                    "label": "has activity in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "activity_in_country",
                    "subject": "Distribution",
                    "label": "has activity in"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "product",
                    "subject": "EnergyProject",
                    "label": "has product of"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "commentary",
                    "subject": "EnergyProject",
                    "label": "is analyzed by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "owner",
                    "subject": "EnergyProject",
                    "label": "is owned by"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "partner",
                    "subject": "EnergyProject",
                    "label": "has partnership with"
                }
            },
            {
                "pk": None,
                "model": "detective.searchterm",
                "fields": {
                    "topic": 2,
                    "name": "activity_in_country",
                    "subject": "EnergyProject",
                    "label": "has activity in"
                }
            }
        ]
        for st in fixtures:
            st["fields"]["topic"] = orm["detective.topic"].objects.get(id=st["fields"]["topic"])
            obj = orm["detective.searchterm"](**st["fields"])
            obj.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    no_dry_run = True
    models = {
        u'detective.article': {
            'Meta': {'object_name': 'Article'},
            'content': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['detective.Topic']"})
        },
        u'detective.quoterequest': {
            'Meta': {'object_name': 'QuoteRequest'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100'}),
            'employer': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'records': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'detective.searchterm': {
            'Meta': {'object_name': 'SearchTerm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['detective.Topic']"})
        },
        u'detective.topic': {
            'Meta': {'object_name': 'Topic'},
            'about': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'background': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.SlugField', [], {'max_length': '250', 'blank': 'True'}),
            'ontology': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '250'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        }
    }


    complete_apps = ['detective']
    symmetrical = True
