class window.IndividualListCtrl
    # Injects dependencies
    @$inject: ['$scope', '$stateParams', '$state', 'Individual', 'Summary', 'Common', '$location',  'Page', '$timeout', '$rootScope']

    constructor: (@scope, @stateParams, @state, @Individual, @Summary, @Common, @location, @Page, @timeout, @rootScope)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.hasPreviousPage = @hasPreviousPage
        @scope.hasNextPage     = @hasNextPage
        @scope.previousPage    = @previousPage
        @scope.nextPage        = @nextPage
        @scope.pages           = @pages
        @scope.nearestPages    = @nearestPages
        @scope.getPage         = @getPage
        @scope.singleUrl       = @singleUrl
        @scope.editUrl         = @editUrl
        @scope.isLoading       = @isLoading
        @scope.csvExport       = @csvExport
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Read route params
        @scope.username           = @stateParams.username
        @scope.topic              = @stateParams.topic
        @scope.type               = @stateParams.type or ""
        @scope.page               = @stateParams.page or 1
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
        @scope.$on "$routeUpdate", => @scope.page = parseInt @stateParams.page or 1
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
        @Summary.get {id: "forms", topic: @scope.topic, username: @scope.username}, (data)=>
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
                else @state.go("404")

    # List parameters
    getParams: =>
        type    : @scope.type
        limit   : @scope.limit
        offset  : (@scope.page-1)*@scope.limit
        order_by: "name"

    singleUrl: (individual)=>
        type = (@scope.type or individual.model).toLowerCase()
        "/#{@scope.username}/#{@scope.topic}/#{type}/#{individual.id}"

    editUrl: (individual)=>
        type = (@scope.type or individual.model).toLowerCase()
        "/#{@scope.username}/#{@scope.topic}/contribute/?type=#{type}&id=#{individual.id}"

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
    getPage: (page)=>
        params = @stateParams
        params.page = 1*page
        @state.href @state.current, params
    # True if there is a previous page
    hasPreviousPage: => @scope.individuals.meta? and @scope.page > 1
    # True if there is a next page
    hasNextPage: =>
        return false unless @scope.individuals.meta?
        meta     = @scope.individuals.meta
        nb_pages = Math.ceil(meta.total_count / meta.limit)
        @scope.page < nb_pages

    # Go to the previous page
    previousPage: => @getPage(1*@scope.page-1) if @hasPreviousPage()
    # Go to the next page
    nextPage: => @getPage(1*@scope.page+1) if @hasNextPage()
    # Loading state
    isLoading: => not @scope.individuals.meta?

    csvExport: =>
        if @scope.individuals.objects? and @scope.individuals.objects.length > 0
            that = this
            @requestCsvExport (d) ->
                if d.status == "enqueued"
                    that.scope.exporting_csv = yes
                    # ask if the job is finished
                    @retry = 0
                    refresh_timeout = that.timeout refresh_status = =>
                        that.Common.get {type:"jobs", id:d.token}, (data) =>
                            if data? and data.result? and data.result != ""
                                that.askToDownload(JSON.parse(data.result).file_name)
                            else if data? and data.status == "failed"
                                that.rootScope.$broadcast 'http:error', "Sorry, the export has failed."
                                that.scope.exporting_csv = no
                            else
                                @retry = 0
                                # retart the function
                                refresh_timeout = that.timeout(refresh_status, 2000) if that.scope.exporting_csv
                        , (error) =>
                            if @retry < 5
                                refresh_timeout = that.timeout(refresh_status, 2000) if that.scope.exporting_csv
                                @retry += 1
                            else
                                that.rootScope.$broadcast 'http:error', "Sorry, the export has failed. Please try again in a fiew moment"
                                that.scope.exporting_csv = no
                    # cancel the timeout if the view is destroyed
                    that.scope.$on '$destroy', =>
                        that.timeout.cancel(refresh_timeout)
                else
                    # ask to download
                    that.askToDownload(d.file_name)

    askToDownload: (file_name) =>
        @scope.exporting_csv = no
        window.location.replace(file_name)

    requestCsvExport: (cb) =>
        @Summary.export { type : @scope.type }, cb, (d) =>
            @scope.exporting_csv = no

angular.module('detective').controller 'individualListCtrl', IndividualListCtrl

# EOF
