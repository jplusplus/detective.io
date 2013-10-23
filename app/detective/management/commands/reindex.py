# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

class Command(BaseCommand):
    help = "Reindex a given model."    
    args = 'app.Model'    

    def handle(self, *args, **options):
        if not args:
            raise CommandError('Please specify the model to reindex.')        
        # Get the model parts
        parts = args[0].split('.', 1)
        # Model given is malformed
        if len(parts) != 2:
            raise CommandError('Indicate the model to reindex by following the syntax "app.Model".')        
        # Get the model
        model = get_model( *parts )   
        # Callable model
        if model == None:
            raise CommandError('Unable to load the model "%s"' % args[0])  
        saved_ct = 0     
        print "Starting reindex. This can take a while...." 
        # Load every objects to reindex them one by one
        for o in model.objects.all(): 
            # Save the object without changing anything will force a reindex
            o.save()
            # Count saved objects
            saved_ct += 1
        print 'Model "%s" reindexed through %s object(s).' % (model.__name__, saved_ct)
