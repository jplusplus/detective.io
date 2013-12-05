# -*- coding: utf-8 -*-
import os
from app.detective import owl
module    = '%s.models' % __package__
directory = os.path.dirname(os.path.realpath(__file__))
ontology  = "%s/ontology.owl" % directory

print owl.parse(ontology, module)