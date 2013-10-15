# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import json
from django.db.models.loading import get_model

class Command(BaseCommand):
    help = "Parse the given JSON file to insert the data into database."    
    args = 'filename.json'
    root = None


    def handle(self, *args, **options):

        if not args:
            raise CommandError('Please specify path to JSON file.')

        json_data = open(args[0])   
        nodes = json.load(json_data) # deserialises it
        json_data.close()

        saved = 0
        for node in nodes:
            # Get the model of the fixture
            model = get_model( *node["model"].split('.', 1) )   
            # Callable model
            if hasattr(model, '__call__'):
                # Create an object with its fields
                obj = model(**node["fields"])
                # Then save the obj
                obj.save()
                # Increment the saved count
                saved += 1

        if saved <= 1:       
            print "%s object saved from file!" % saved
        else:
            print "%s objects saved from file!" % saved