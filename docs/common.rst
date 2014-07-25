========================
Common API documentation
========================

The common API aims to manage common elements in Detective.io. It allows for
exemple to explore and manage open topics, users login, quote request, etc

.. http:get:: /api/common/v1/topic/

    The topics the current user (even anonymous), has access to.

    **Example request**:

    .. sourcecode:: http

        GET /api/common/v1/topic/ HTTP/1.1
        Host: detective.io
        Accept: application/json, text/javascript


    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        { "meta" : { "limit" : 20,
              "next" : null,
              "offset" : 0,
              "previous" : null,
              "total_count" : 1
            },
          "objects" : [
              { "about" : "",
                "author" : null,
                "background" : null,
                "description" : "A comprehensive database of every person and every organization linked to innovative energy projects.",
                "featured" : false,
                "id" : 2,
                "link" : null,
                "models" : [ { "is_searchable" : false,
                      "name" : "Amount",
                      "verbose_name" : "amount",
                      "verbose_name_plural" : "amounts"
                    },
                    { "is_searchable" : false,
                      "name" : "Commentary",
                      "verbose_name" : "commentary",
                      "verbose_name_plural" : "commentarys"
                    },
                    { "is_searchable" : true,
                      "name" : "Country",
                      "verbose_name" : "Country",
                      "verbose_name_plural" : "Countries"
                    },
                    { "is_searchable" : false,
                      "name" : "Distribution",
                      "verbose_name" : "distribution",
                      "verbose_name_plural" : "distributions"
                    },
                    { "is_searchable" : true,
                      "name" : "EnergyProduct",
                      "verbose_name" : "Energy product",
                      "verbose_name_plural" : "Energy products"
                    },
                    { "is_searchable" : true,
                      "name" : "EnergyProject",
                      "verbose_name" : "Energy project",
                      "verbose_name_plural" : "Energy projects"
                    },
                    { "is_searchable" : false,
                      "name" : "FundraisingRound",
                      "verbose_name" : "fundraising round",
                      "verbose_name_plural" : "fundraising rounds"
                    },
                    { "is_searchable" : true,
                      "name" : "Organization",
                      "verbose_name" : "Organization",
                      "verbose_name_plural" : "Organizations"
                    },
                    { "is_searchable" : true,
                      "name" : "Person",
                      "verbose_name" : "Person",
                      "verbose_name_plural" : "Persons"
                    },
                    { "is_searchable" : false,
                      "name" : "Price",
                      "verbose_name" : "price",
                      "verbose_name_plural" : "prices"
                    },
                    { "is_searchable" : false,
                      "name" : "Revenue",
                      "verbose_name" : "revenue",
                      "verbose_name_plural" : "revenues"
                    }
                  ],
                "module" : "energy",
                "ontology" : null,
                "public" : true,
                "resource_uri" : "",
                "search_placeholder" : "Search for organizations, energy products, persons, energy projects and countries",
                "slug" : "energy",
                "thumbnail" : null,
                "title" : "Innovative energy projects in developing countries "
              }
            ]
        }


    :query offset: offset number. default is 0
    :query limit: limit number. default is 30
    :reqheader Accept: the response content type depends on `Accept` header
    :reqheader Authorization: optional OAuth token to authenticate
    :resheader Content-Type: this depends on `Accept` header of request
    :statuscode 200: no error

.. http:get:: /api/common/v1/user

  The users signed up.

  **Example request**:

  .. sourcecode:: http

    GET /api/common/v1/user/ HTTP/1.1
    Host: detective.io
    Accept: application/json, text/javascript

  **Example response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Vary: Accept
    Content-Type: text/javascript

    { "meta": {
        "limit": 20,
        "next": null,
        "offset": 0,
        "previous": null,
        "total_count": 1
      },
      "objects": [
        { "email": "☘",
          "first_name": "",
          "id": 1,
          "is_staff": false,
          "last_name": "",
          "password": "☘",
          "resource_uri": "",
          "username": "detective"
        }
      ]
    }

  :query offset: offset number. default is 0
  :query limit: limit number. default is 30
  :reqheader Accept: the response content type depends on `Accept` header
  :reqheader Authorization: optional OAuth token to authenticate
  :resheader Content-Type: this depends on `Accept` header of request
  :statuscode 200: no error
