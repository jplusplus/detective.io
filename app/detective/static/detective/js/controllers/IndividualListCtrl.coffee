class IndividualListCtrl
    # Injects dependancies
    @$inject: ['$scope', '$routeParams', 'Individual', 'Summary', 'Common', '$location',  'Page']

    constructor: (@scope, @routeParams, @Individual, @Summary, @Common, @location, @Page)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.hasPreviousPage = @hasPreviousPage
        @scope.hasNextPage     = @hasNextPage
        @scope.previousPage    = @previousPage
        @scope.nextPage        = @nextPage
        @scope.pages           = @pages
        @scope.nearestPages    = @nearestPages
        @scope.goToPage        = @goToPage
        @scope.singleUrl       = @singleUrl
        @scope.isLoading       = @isLoading
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Read route params
        @scope.username           = @routeParams.username
        @scope.topic              = @routeParams.topic
        @scope.type               = @routeParams.type or ""
        @scope.page               = @routeParams.page or 1
        @scope.limit              = 20
        @scope.individuals        = {}
        @scope.selectedIndividual = {}
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────
        @scope.$watch "selectedIndividual", @selectIndividual, true
        @scope.$watch "page", =>
            # Global loading mode
            @Page.loading false
            # Get parameters from context method (could be overloaded)
            params = @getParams()
            # Only if params are valid
            if params
                # Global loading mode
                @Page.loading true
                # Get individual from database
                @scope.individuals = @Individual.get params, =>
                    # Turn off loading mode
                    @Page.loading false
        # Update page value
        @scope.$on "$routeUpdate", => @scope.page = @routeParams.page or 1
        # ──────────────────────────────────────────────────────────────────────
        # Page setup
        # ──────────────────────────────────────────────────────────────────────
        @getVerbose()

    selectIndividual: (val, old)=>
        # Single entity selected
        if val.id?
            @location.path "/#{@scope.username}/#{@scope.topic}/#{@scope.type.toLowerCase()}/#{val.id}"

    # Verbose informations
    # (loaded contexualy)
    getVerbose: =>
        # Get meta information for this type
        @Summary.get {id: "forms", topic: @scope.topic}, (data)=>
            # Avoid set the wrong title
            # (when the controller is destroyed)
            unless @scope.$$destroyed
                @scope.meta = meta = data[@scope.type.toLowerCase()]
                if meta?
                    # Redirect "unlistable" resource
                    return @location.path "/#{@scope.username}/#{@scope.topic}" unless meta.rules.is_searchable
                    @scope.verbose_name        = meta.verbose_name
                    @scope.verbose_name_plural = meta.verbose_name_plural
                    # Set page's title
                    @Page.title meta.verbose_name_plural
                # Unkown type
                else @location.path "/404"

    # List parameters
    getParams: =>
        type    : @scope.type
        limit   : @scope.limit
        offset  : (@scope.page-1)*@scope.limit
        order_by: "name"

    singleUrl: (individual)=>
        type = (@scope.type or individual.model).toLowerCase()
        "/#{@scope.username}/#{@scope.topic}/#{type}/#{individual.id}"
    # Pages list
    pages: =>
        # No page yet
        unless @scope.individuals.meta? then return [1]
        # Use the meta info to determine the page number
        nb = @scope.individuals.meta.total_count/@scope.limit
        new Array Math.ceil(nb)
    nearestPages: =>
        pages = []
        scope = 4
        for i in _.range(parseInt(@scope.page) - scope, parseInt(@scope.page) + scope)
            # remove first and last pages
            pages.push(i) unless i <= 1 or i >= @pages().length
        return pages

    # Go to the given page
    goToPage: (page)=> @location.search "page", 1*page
    # True if there is a previous page
    hasPreviousPage: => @scope.individuals.meta? and @scope.page > 1
    # True if there is a next page
    hasNextPage: => @scope.individuals.meta? and @scope.individuals.meta.next? and @scope.individuals.meta.next isnt null
    # Go to the previous page
    previousPage: => @goToPage(1*@scope.page-1) if @hasPreviousPage()
    # Go to the next page
    nextPage: => @goToPage(1*@scope.page+1) if @hasNextPage()
    # Loading state
    isLoading: => not @scope.individuals.meta?



angular.module('detective').controller 'individualListCtrl', IndividualListCtrl