class window.IndividualSingleCtrl
    # Injects dependencies
    @$inject: ['$scope', '$stateParams', '$state', 'Individual',  'topic', 'individual', 'forms', '$filter', '$anchorScroll', '$location', 'Page', 'QueryFactory', '$sce']

    constructor: (@scope, @stateParams, @state, @Individual, @topic, @individual, @forms, @filter, @anchorScroll, @location, @Page, @QueryFactory, $sce)->
        @scope.get            = (n, def=null)=> @individual[n] or def if @individual?
        @scope.getTrusted     = (n)=>
            val = @scope.get n
            if val? and val.length > 0 then ($sce.trustAsHtml val) else ""
        @scope.hasRels        = @hasRels
        @scope.hasNetwork     = => (_.keys (@scope.graphnodes.leafs or {})).length > 1
        @scope.isLiteral      = @isLiteral
        @scope.hasValue       = (f)=>
            def = if f.type == "BooleanField" then false else null
            @scope.get(f.name, def) != null and f.name != 'name'
        @scope.hasValues      = (f)=> @scope.get(f.name, []).length > 0
        @scope.isString       = (t)=> ["CharField", "URLField"].indexOf(t) > -1
        @scope.isUrl          = (t)=> t is "URLField"
        @scope.isRelationship = (d)=> ["Relationship", "ExtendedRelationship"].indexOf(d.type) > -1
        @scope.isBoolean      = (t)=> ["BooleanField"].indexOf(t) > -1
        @scope.isRich         = (field)=> field.rules.is_rich or no
        @scope.isOEmbed       = (field)=> field.rules.is_oembed or no
        @scope.scrollTo       = @scrollTo
        @scope.singleUrl      = @singleUrl
        @scope.strToColor     = @filter("strToColor")
        @scope.getSources     = @getSources
        @scope.hasSources     = @hasSources
        @scope.deleteNode     = @deleteNode
        @scope.isAddr         = (f)=> f.name.toLowerCase().indexOf('address') > -1
        @scope.isImg          = (f)=> f.name is 'image'
        @scope.isMono         = (f)=> @scope.isAddr(f) or @scope.isImg(f) or @scope.isGeoloc(f)
        @scope.graphnodes     = []
        @scope.frontStyle     = (ref)=> 'background-color': @filter("strToColor")(ref)
        @scope.isLatitude     = (f) => ((do f.name.toLowerCase).indexOf 'latitude') >= 0
        @scope.isLongitude    = (f) => ((do f.name.toLowerCase).indexOf 'longitude') >= 0
        @scope.isGeoloc       = (f) => ((do f.name.toLowerCase).indexOf 'geolocation') >= 0
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Read route params
        @scope.topic      = @topic.slug
        @scope.username   = @topic.author.username
        @scope.type       = @stateParams.type
        @scope.id         = @stateParams.id
        @scope.individual = @individual
        # Get meta information for this type
        @scope.meta           = @forms[ @scope.type.toLowerCase() ]
        @scope.topicmeta      = @topic
        @scope.mailReportLink = @getMailReportLink
        # Get individual authors
        @scope.authors     = @Individual.authors()
        # Get source for the names
        @scope.nameSources = do @getNameSources
        # Load graph data
        graph_params =
            topic   : @scope.topic
            username: @scope.username
            type    : @stateParams.type
            id      : @stateParams.id
            depth   : 2
        @Individual.graph graph_params, (data) => @scope.graphnodes = data

        do @computeGeolocation
        # Set page's title
        title = @filter("individualPreview")(@individual)
        @Page.title title
        # Update human query
        @QueryFactory.updateHumanQuery title

    getSources: (field)=>
        _.where @scope.individual.field_sources, field: field.name

    getNameSources: =>
        field = _.findWhere @scope.meta.fields, name: 'name'
        @getSources field

    hasSources: (field)=>
        sources = @getSources field
        (not _.isEmpty sources) and _.some sources, (e)-> e? and e.reference?

    hasRels: ()=>
        if @scope.meta? and @individual?
            _.some @scope.meta.fields, (field)=>
                @scope.isRelationship(field) and
                @individual[field.name]? and
                @individual[field.name].length

    scrollTo: (id)=>
        @location.hash(id)
        @anchorScroll()
    singleUrl: (individual, type=false)=>
        type  = (type or @scope.type).toLowerCase()
        topic = (@forms[type] and @forms[type].topic) or @scope.topic
        "/#{@scope.username}/#{topic}/#{type}/#{individual.id}/"
    # True if the given type is literal
    isLiteral: (field)=>
        [
            "CharField",
            "DateTimeField",
            "URLField",
            "IntegerField",
            "BooleanField"
        ].indexOf(field.type) > -1

    deleteNode: (msg='Are you sure you want to delete this node?')=>
        # Ask user for confirmation
        if confirm(msg)
            @Individual.delete
                id   : @scope.id
                topic: @scope.topic
                type : @scope.type
            # Redirect to the type list
            setTimeout (=>
                @location.url("/#{@scope.username}/#{@scope.topic}/#{@scope.type}")
            ), 500

    computeGeolocation: =>
        if @scope.meta? and @scope.meta.fields?
            geoloc =
                meta :
                    name : 'geolocation'
                    verbose_name : 'Latitude/Longitude'
                    type : "CharField"
                individual :
                    longitude : undefined
                    latitude : undefined

            for index, field of @scope.meta.fields
                if @scope.isLatitude field
                    geoloc.individual.latitude = @scope.get field.name
                else if @scope.isLongitude field
                    geoloc.individual.longitude = @scope.get field.name

                break if geoloc.individual.longitude? and geoloc.individual.latitude?
            if geoloc.individual.longitude? and geoloc.individual.latitude?
                @scope.meta.fields.push geoloc.meta
                @individual['geolocation'] = "#{geoloc.individual.latitude}, #{geoloc.individual.longitude}"

    getMailReportLink: =>
        topic_title = @topic.title
        indiv_name  = @individual.name
        error_url   = @location.absUrl()

        subject = encodeURIComponent "[Detective.io] Error on page #{indiv_name} in #{topic_title}"
        body    = encodeURIComponent """
            Dear Detective.io team,

            I spotted a mistake on this page #{error_url}.

            What stands there should be corrected because … (add links that show the information on the site is erroneous).

            Yours,

            """
        "mailto:contact@detective.io?subject=#{subject}&body=#{body}"

angular.module('detective.controller').controller 'individualSingleCtrl', IndividualSingleCtrl
