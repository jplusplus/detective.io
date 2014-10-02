#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Detective.io
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU GENERAL PUBLIC LICENSE v3
# -----------------------------------------------------------------------------
# Creation : 30-Sep-2014
# Last mod : 02-Oct-2014
# -----------------------------------------------------------------------------
from app.detective.models             import Topic
from app.detective.topics.common.jobs import process_bulk_parsing_and_save_as_model
from tastypie.test                    import ResourceTestCase
import json

class JobsTestCase(ResourceTestCase):
    fixtures = [
        'app/detective/fixtures/default_topics.json',
        'app/detective/fixtures/tests_pillen.json'
    ]

    def test_bulk_upload(self):
        topic = Topic.objects.get(slug="test-pillen")
        files = (
            (
                "pillen.csv", (
                    ("Pill_id,name,logo,image,image_back,break_notch,color,weight,diameter,thickness,place,date,more_infos"),
                    ("57713,Peer,,,,True,yellow,,,,,,"),
                    ("57457,Apple,,,,False,,,,,,,"),
                    ("57229,newone,,,,False,,,,,,,"),
                    ("57217,Ahorn,,,,False,,,,,,,"),
                    ("57160,Nouvelle,,,,False,,,,,,,"),
                    ("57157,blibli,,,,False,,,,,,,"),
                    ("56618,bloup,,,,False,,,,,,,"),
                    ("56269,My new pill,,,,False,,,,,,,"),
                    ("56267,test,,,,False,,,,,,,"),
                    ("56263,No Name,No Name,http://www.mindzone.info/uploads/bild1-hrkEbw.jpg,http://www.mindzone.info/uploads/bild2-7RIakC.jpg,True,gräulich mit Sprenkeln,301.4,8.6 ,4.2,Zürich,2014-08-15 00:00:00,http://www.saferparty.ch/tl_files/images/download/file/Warnungen_PDF_2014/MDMA_hoch_August_2014.pdf"),
                    ("55993,bn,,,,False,,,,,,2014-08-04 22:00:00-05:00,"),
                    ("55991,Herz,Herz,http://www.mindzone.info/uploads/bild1-3Do2Ib.jpg,http://www.mindzone.info/uploads/bild2-RTdvKU.jpg,False,Orange mit Sprenkeln,353.3 ,9.1,5.1,Zürich,2014-07-18 20:00:00-05:00,http://saferparty.ch/warnungen.html"),
                    ("55983,C,C,http://www.mindzone.info/uploads/bild1-fblABz.jpg,http://www.mindzone.info/uploads/bild2-OnKCgz.jpg,False,Pink mit Sprenkel,247.7,8.1, 3.9,Zürich,2014-05-20 20:00:00-05:00,"),
                    ("55981,Geist (Pac - Man),Geist (Pac - Man),http://www.mindzone.info/uploads/bild1-ShEXs5.jpg,http://www.mindzone.info/uploads/bild2-s7lsuD.jpg,True,weiss/grau,,,,,,"),
                    ("55976,Handgranate,Handgranate,http://www.mindzone.info/uploads/bild1-T2hx3C.jpg,http://www.mindzone.info/uploads/bild2-TS37I9.jpg,False,hell Grün,274.7,9.1, 5.6,Zürich,2014-07-11 20:00:00-05:00,http://saferparty.ch/warnungen.html"),
                    ("55964,Facebook,Facebook,http://www.mindzone.info/uploads/bild1-GliztW.jpg,http://www.mindzone.info/uploads/bild2-3pgwvb.jpg,True,Weiss,302.7,8.1,5.0,Zürich,2014-07-25 22:00:00-05:00,http://saferparty.ch/warnungen.html"),
                    ("55961,Superman,Superman,http://www.mindzone.info/uploads/bild1-qrJuqx.jpg,http://www.mindzone.info/uploads/bild2-prUV6N.jpg,True,Gelb mit Sprenkeln,372.1,10.9,,Zürich,2014-07-10 22:00:00-05:00,"),
                    ("55959,Mitsubishi,Mitsubishi,http://www.mindzone.info/uploads/bild1-lRxXy9.jpg,http://www.mindzone.info/uploads/bild2-WpQ36r.jpg,False,Rot,229.6,9.1,3.9,Zürich,2014-08-01 18:00:00-05:00,"),
                    ("55947,Ahorn,Ahorn,http://www.mindzone.info/uploads/bild1-ix7TFV.jpg,http://www.mindzone.info/uploads/bild2-2slj54.jpg,False,dunkelblau,367.5,8.2,6.3,Zürich,2014-08-08 22:00:00-05:00,http://www.saferparty.ch/tl_files/images/download/file/Warnungen_PDF_2014/XTC_mit_Piperonal_August_2014a.pdf")
                )
            ),
            (
                "molecules.csv", (
                    ("Molecule_id,name,toxicity_threshold,description"),
                    ("57714,bidule,,"),
                    ("57230,new,,"),
                    ("57219,mdma,,"),
                    ("57218,mdma,,"),
                    ("57159,Mdma,,"),
                    ("56621,Fichtre,,"),
                    ("56498,roro,,"),
                    ("56268,,,"),
                    ("56265,,,"),
                    ("56264,MDMA HCL,,"),
                    ("55987,MBZP,,"),
                    ("55986,mCPP,,"),
                    ("55985,MDMA,,"),
                    ("55969,Coffein,,"),
                    ("55967,Amphetamin*HCl,,"),
                    ("55963,MDMA*HCI,120,"),
                    ("55950,Piperonal,,\"<b>Piperonal</b><span>, also known as&#160;</span><b>heliotropin</b><span>, is an&#160;</span><a href=\"\"http://en.wikipedia.org/wiki/Organic_compound\"\" title=\"\"Organic compound\"\">organic compound</a><span>&#160;that is commonly found in fragrances and flavors. The molecule is structurally related to&#160;</span><a href=\"\"http://en.wikipedia.org/wiki/Benzaldehyde\"\" title=\"\"Benzaldehyde\"\">benzaldehyde</a><span>&#160;and&#160;</span><a href=\"\"http://en.wikipedia.org/wiki/Vanillin\"\" title=\"\"Vanillin\"\">vanillin</a><span>. It exists as a white or colorless solid. It has a floral odor commonly described as being similar to that of vanillin and&#160;</span><a href=\"\"http://en.wikipedia.org/wiki/Cherry\"\" title=\"\"Cherry\"\">cherry</a><span>. It is used as flavoring, e.g. in&#160;</span><a href=\"\"http://en.wikipedia.org/wiki/Perfume\"\" title=\"\"Perfume\"\">perfumes</a><span>&#160;or chocolate.</span>\"")
                )
            ),
            (
                "composition.csv", (
                    ("Pill_id,molecules_contained,Molecule_id,quantity_(in_milligrams)."),
                    ("57713,,57714,250"),
                    ("57457,,57230,9"),
                )
            ),
        )
        # run the job without job runner
        response = process_bulk_parsing_and_save_as_model(topic, files)
        # check
        models   = topic.get_models_module()
        Pill     = models.Pill
        Molecule = models.Molecule
        self.assertEquals(len(response.get("errors"))            , 0, response)
        self.assertEquals(response.get("inserted").get("objects"), sum( (len(file[1])-1 for file in files if file[0] in ["pillen.csv", "molecules.csv"])))
        self.assertEquals(response.get("inserted").get("objects"), topic.entities_count())
        self.assertEquals(response.get("inserted").get("links")  , sum( (len(file[1])-1 for file in files if file[0] in ["composition.csv"])))
        self.assertEquals(Pill.objects.all().count()             , next((len(file[1])-1 for file in files if file[0] == "pillen.csv")))
        self.assertEquals(Molecule.objects.all().count()         , next((len(file[1])-1 for file in files if file[0] == "molecules.csv")))
        def get_relationship_reference(pilule_id, mol_id):
            resp = self.api_client.get('/api/detective/test-pillen/v1/pill/%d/relationships/molecules_contained/%d/' % (pilule_id, mol_id), follow=True, format='json')
            self.assertValidJSONResponse(resp)
            resp = json.loads(resp.content)
            return resp
        two_items_related = (Pill.objects.get(name="Peer").id, Molecule.objects.get(name="bidule").id)
        relation          = get_relationship_reference(*two_items_related)
        self.assertTrue   (int(relation["_relationship"])       > 0)
        self.assertEquals (relation["_endnodes"]                , list(two_items_related))
        self.assertIn     ("quantity_(in_milligrams)."          , relation.keys())
        self.assertEquals (relation["quantity_(in_milligrams)."], "250")
        Pill.objects.all().delete()
        Molecule.objects.all().delete()

# EOF
