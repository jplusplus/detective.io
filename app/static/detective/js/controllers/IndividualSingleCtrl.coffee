class IndividualSingleCtrl
    # Injects dependancies    
    @$inject: ['$scope', '$routeParams', 'Individual', 'Summary', '$filter', '$anchorScroll', '$location', 'Page']

    constructor: (@scope, @routeParams, @Individual, @Summary, @filter, @anchorScroll, @location, @Page)->  
        # Global loading mode!
        Page.loading true
        @scope.get            = (n)=> @scope.individual[n] or false if @scope.individual?
        @scope.hasRels        = @hasRels  
        @scope.isLiteral      = @isLiteral
        @scope.isString       = (t)=> ["CharField", "URLField"].indexOf(t) > -1
        @scope.isRelationship = (d)=> ["Relationship", "ExtendedRelationship"].indexOf(d.type) > -1
        @scope.scrollTo       = @scrollTo  
        @scope.singleUrl      = @singleUrl
        @scope.strToColor     = @filter("strToColor")
        @scope.deleteNode     = @deleteNode
        @scope.isAddr         = (f)=> f.name.toLowerCase().indexOf('address') > -1
        @scope.isImg          = (f)=> f.name is 'image'
        @scope.isMono         = (f)=> @scope.isAddr(f) or @scope.isImg(f) 
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────  
        # Read route params
        @scope.scope = @routeParams.scope
        @scope.type  = @routeParams.type
        @scope.id    = @routeParams.id
        params =
            scope: @scope.scope
            type : @scope.type
            id   : @scope.id
        # Get individual from database
        @Individual.get params, (data)=> 
            # Avoid set the wrong title
            # (when the controller is destroyed)
            unless @scope.$$destroyed
                @scope.individual = data
                # Set page's title
                @Page.title @filter("individualPreview")(data)      
                 # Global loading off 
                Page.loading false        
        # Not found
        , => @location.path "/404"
        # Get meta information for this type
        @Summary.get id: "forms", (data)=> 
            @scope.resource = data
            @scope.meta     = data[@scope.type.toLowerCase()]        
        

    hasRels: ()=> 
        if @scope.meta? and @scope.individual?
            _.some @scope.meta.fields, (field)=> 
                @scope.isRelationship(field)  and @scope.individual[field.name].length

    scrollTo: (id)=> 
        @location.hash(id)
        @anchorScroll()
    singleUrl: (individual, type=false)=> 
        type  = (type or @scope.type).toLowerCase()
        scope = (@scope.resource[type] and @scope.resource[type].scope) or @scope.scope
        "/#{scope}/#{type}/#{individual.id}/"
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
                scope: @scope.scope
                type : @scope.type
            # Redirect to the type list
            setTimeout (=>
                @location.url("/#{@scope.scope}/#{@scope.type}")
            ), 500

    
angular.module('detective').controller 'individualSingleCtrl', IndividualSingleCtrl
