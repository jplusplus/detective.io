class IndividualListCtrl
    # Injects dependancies    
    @$inject: ['$scope', '$routeParams', 'Individual', 'Summary', '$location', '$filter', 'Page']

    constructor: (@scope, @routeParams, @Individual, @Summary, @location, @filter, @Page)->              
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────  
        @scope.strToColor      = @filter("strToColor")
        @scope.hasPreviousPage = @hasPreviousPage
        @scope.hasNextPage     = @hasNextPage
        @scope.previousPage    = @previousPage
        @scope.nextPage        = @nextPage
        @scope.pages           = @pages
        @scope.goToPage        = @goToPage
        @scope.singleUrl       = @singleUrl
        @scope.isLoading       = @isLoading
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────  
        # Read route params
        @scope.scope       = @routeParams.scope
        @scope.type        = @routeParams.type
        @scope.page        = @routeParams.page or 1
        @scope.limit       = 20
        @scope.individuals = {}        
        # Get meta information for this type
        @Summary.get id: "forms", (data)=> 
            @scope.meta = data[@scope.type.toLowerCase()]
            # Set page's title
            @Page.setTitle @scope.meta.verbose_name_plural
        # ──────────────────────────────────────────────────────────────────────
        # Scope watchers
        # ──────────────────────────────────────────────────────────────────────  
        @scope.$watch "page", =>
            # Get individual from database
            @scope.individuals = @Individual.get 
                type    : @scope.type
                limit   : @scope.limit
                offset  : @scope.limit * (@scope.page - 1)
                order_by: "name"
        # Update page value
        @scope.$on "$routeUpdate", => @scope.page = @routeParams.page or 1

        
    singleUrl: (individual)=> "/node/#{@scope.type}/#{individual.id}"
    # Pages list
    pages: => 
        # No page yet
        unless @scope.individuals.meta? then return [1]
        # Use the meta info to determine the page number
        nb = @scope.individuals.meta.total_count/@scope.limit
        new Array Math.ceil(nb)
    # Go to the given page
    goToPage: (page)=> @location.search "page", 1*page
    # True if there is a previous page
    hasPreviousPage: => @scope.individuals.meta? and @scope.page > 1
    # True if there is a next page
    hasNextPage: => @scope.individuals.meta? and @scope.individuals.meta.next isnt null
    # Go to the previous page
    previousPage: => @goToPage(1*@scope.page-1) if @hasPreviousPage()
    # Go to the next page
    nextPage: => @goToPage(1*@scope.page+1) if @hasNextPage()
    # Loading state
    isLoading: => not @scope.individuals.meta?


    
angular.module('detective').controller 'individualListCtrl', IndividualListCtrl