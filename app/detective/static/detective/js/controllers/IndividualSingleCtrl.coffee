class IndividualSingleCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Individual', 'Summary', '$filter', '$anchorScroll', '$location', 'Page', 'topic']

    constructor: (@scope, @routeParams, @Individual, @Summary, @filter, @anchorScroll, @location, @Page, topic)->
        # Global loading mode!
        Page.loading true
        @scope.get            = (n)=> @scope.individual[n] or false if @scope.individual?
        @scope.hasRels        = @hasRels
        @scope.hasNetwork     = => (_.keys (@scope.graphnodes.leafs or {})).length > 1
        @scope.isLiteral      = @isLiteral
        @scope.isString       = (t)=> ["CharField", "URLField"].indexOf(t) > -1
        @scope.isRelationship = (d)=> ["Relationship", "ExtendedRelationship"].indexOf(d.type) > -1
        @scope.scrollTo       = @scrollTo
        @scope.singleUrl      = @singleUrl
        @scope.strToColor     = @filter("strToColor")
        @scope.getSource      = @getSource
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
        @scope.topic     = @routeParams.topic
        @scope.username  = @routeParams.username
        @scope.type      = @routeParams.type
        @scope.id        = @routeParams.id
        params =
            topic: @scope.topic
            type : @scope.type
            id   : @scope.id
        # Get individual from database
        @Individual.get params, (data)=>
            # Avoid set the wrong title
            # (when the controller is destroyed)
            unless @scope.$$destroyed
                @scope.individual = data
                do @computeGeolocation
                # Set page's title
                @Page.title @filter("individualPreview")(data)
                 # Global loading off
                Page.loading false
        # Not found
        , => @scope.is404(yes)
        # Get meta information for this type
        @Summary.get { id: "forms", topic: @scope.topic}, (data)=>
            @scope.resource = data
            @scope.meta     = data[@scope.type.toLowerCase()]

        graph_params = angular.copy params
        graph_params.depth = 2

        @Individual.graph graph_params, (data) =>
            @scope.graphnodes = data

        @scope.topicmeta = topic

    getSource: (field)=>
        _.find @scope.individual.field_sources, (fs)=> fs.field is field.name   

    hasRels: ()=>
        if @scope.meta? and @scope.individual?
            _.some @scope.meta.fields, (field)=>
                @scope.isRelationship(field) and
                @scope.individual[field.name]? and
                @scope.individual[field.name].length

    scrollTo: (id)=>
        @location.hash(id)
        @anchorScroll()
    singleUrl: (individual, type=false)=>
        type  = (type or @scope.type).toLowerCase()
        topic = (@scope.resource[type] and @scope.resource[type].topic) or @scope.topic
        "/#{@scope.username}/#{topic}/#{type}/#{individual.id}/"
    # True if the given type is literal
    isLiteral: (field)=>
        [
            "CharField",
            "DateTimeField",
            "URLField",
            "IntegerField"
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
                @scope.individual['geolocation'] = "#{geoloc.individual.latitude}, #{geoloc.individual.longitude}"


angular.module('detective.controller').controller 'individualSingleCtrl', IndividualSingleCtrl
