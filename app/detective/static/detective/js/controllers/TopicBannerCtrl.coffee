class TopicBannerCtrl
    # Injects dependencies
    @$inject: ['$scope', '$routeParams', 'Summary']

    constructor: (@scope, @routeParams, @Summary)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.toggleGraphNavigation  = @toggleGraphNavigation
        @scope.toggleFiltersSelection = @toggleFiltersSelection
        @scope.toggleSelectAll        = @toggleSelectAll
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        @scope.graphNavigationEnabled = false
        @scope.filters_selected       = []
        @scope.filters_names          = []
        # ──────────────────────────────────────────────────────────────────────
        # Get the current topic as default topic
        @scope.topic_selected = @routeParams.topic
        # get forms classes
        @Summary.get id:"forms", (d)=>
            @scope.forms            = _.filter(_.values(d), ((f)-> f.rules? && f.rules.is_searchable))
            @scope.filters_names    = _.map(@scope.forms, ((form) -> form.name))
            @scope.filters_selected = angular.copy(@scope.filters_names)

    toggleSelectAll: =>
        # deselect all
        if @scope.filters_selected.length == @scope.filters_names.length
            @scope.filters_selected = []
        # select all
        else
            @scope.filters_selected = angular.copy(@scope.filters_names)

    toggleFiltersSelection: (filter_name) =>
        idx = @scope.filters_selected.indexOf(filter_name)
        # is currently selected
        if idx > -1
            @scope.filters_selected.splice(idx, 1)
        # is newly selected
        else
            @scope.filters_selected.push(filter_name)

    toggleGraphNavigation: =>
        @scope.graphNavigationEnabled = not @scope.graphNavigationEnabled
        if @scope.graphNavigationEnabled and not @scope.graphnodes?
            @Summary.get {id: "graph", topic: @scope.topic_selected}, (data) =>
                console.log data
                @scope.graphnodes = data

angular.module('detective.controller').controller 'TopicBannerCtrl', TopicBannerCtrl

# EOF
