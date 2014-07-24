class TopicBannerCtrl
    # Injects dependencies
    @$inject: ['$scope', '$stateParams', 'Summary']

    constructor: (@scope, @stateParams, @Summary)->
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
        @scope.topic_selected = @stateParams.topic
        # get forms classes
        @Summary.get({id: "forms"}, @retrieveTopicForms)
        # render the graph on filters change
        @scope.$watch("filters_selected", @renderGraph, true) # From angular doc : 
        # true means that inequality of the watchExpression is determined according to the angular.equals function. 
        # To save the value of the object for later comparison, the angular.copy function is used.
        # This therefore means that watching complex objects will have adverse memory and performance implications.

    retrieveTopicForms: (forms) =>
        @scope.forms            = _.filter(_.values(forms), ((f)-> f.rules? && f.rules.is_searchable))
        @scope.filters_names    = _.map(@scope.forms, ((form) -> form.name))
        @scope.filters_selected = angular.copy(@scope.filters_names)
        # FIXME: a lot of methods depend of these data

    # on the "Show all" checkbox click
    toggleSelectAll: =>
        # deselect all
        if @scope.filters_selected.length == @scope.filters_names.length
            @scope.filters_selected = []
        # select all
        else
            @scope.filters_selected = angular.copy(@scope.filters_names)

    # on a checkbox click
    toggleFiltersSelection: (filter_name) =>
        idx = @scope.filters_selected.indexOf(filter_name)
        # is currently selected
        if idx > -1
            @scope.filters_selected.splice(idx, 1)
        # is newly selected
        else
            @scope.filters_selected.push(filter_name)

    # show/hide the graph navigation
    toggleGraphNavigation: =>
        @scope.graphNavigationEnabled = not @scope.graphNavigationEnabled
        if @scope.graphNavigationEnabled and not @scope.graphnodes?
            @Summary.get {id: "graph", topic: @scope.topic_selected}, (data) =>
                # save graph data used by @renderGraph
                @data = data
                @renderGraph()

    # filter the data and render the graph via @scope.graphnodes
    # shared with detective/js/directives/topic.single.graph.coffee
    renderGraph: =>
        if @data?
            data = angular.copy(@data)
            # filter by filters_selected
            data.leafs = _.object(_.filter(_.pairs(@data.leafs), (leaf) =>
                @scope.filters_selected.indexOf(leaf[1]._type.toLowerCase()) > -1
            ))
            @scope.graphnodes = data

angular.module('detective.controller').controller 'TopicBannerCtrl', TopicBannerCtrl

# EOF
