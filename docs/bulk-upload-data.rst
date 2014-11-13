========================
Bulk upload data
========================

Detective.io accept *.csv* files describing models and relations.  

.. code-block:: json

    [
        {
            "name": "Person",
            "fields": [
                { "name": "name", "type": "string" }
                { "name": "owns", "type": "Relationship", "related_model": "Company"}
            ]
        },
        {
            "name": "Company",
            "fields": [
                { "name": "name" }
            ]
        }
    ]

person.csv

.. code-block:: csv

    person_id;name
            1;Matthieu Grimbert

company.csv

.. code-block:: csv

    company_id;name
             2;Doge Inc.

person_owns_company.csv

.. code-block:: csv

    person_id;owns;company_id
            1;    ;2