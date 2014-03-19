angular.module('detective.directive').directive "ttTypeahead", ($parse, $routeParams, User)->
    lastDataset = []
    # Use underscore's template
    # @TODO use $compile from angular
    engine =
        compile: (template)->
            compiled = _.template(template)
            render: (context)-> compiled(context)
    scope:
        model     : "=ttModel"
        individual: "&ttIndividual"
        topic     : "&ttTopic"
        create    : "&ttCreate"
        remote    : "@"
        prefetch  : "@"
        valueKey  : "@"
        limit     : "@"
        change    : "&"
    link: (scope, element, attrs) ->
        # Select the individual to look for
        individual = (scope.individual() or "").toLowerCase()
        itopic     = (scope.topic() or $routeParams.topic or "common").toLowerCase()
        # Set a default value
        element.val scope.model.name if scope.model?
        # Helper to save the search response
        saveResponse = (response)-> lastDataset = response.objects
        # Create the typehead
        element.typeahead
            name: individual
            limit: scope.limit or 5
            template: [
                "<%= name || label %>",
                "<% if (typeof(model) != 'undefined') { %>",
                    "<div class='model'>",
                        "<%= model %>",
                    "</div>",
                "<% } else if (typeof(predicate) != 'undefined' && predicate.name == '<<INSTANCE>>') { %>",
                    "<div class='model'>",
                        "<%= object %>",
                    "</div>",
                "<% } else if (typeof(subject) != 'undefined') { %>",
                    "<div class='model'>",
                        "<i class='icon-list right05'></i>"
                        "<%= subject.label %>",
                    "</div>",
                "<% } %>"
            ].join ""
            engine: engine
            valueKey: scope.valueKey or "name"
            prefetch:
                cache: !User.is_logged
                url: scope.prefetch or "/api/#{itopic}/v1/#{individual}/mine/"
                filter: saveResponse
            remote:
                cache: !User.is_logged
                url: scope.remote or "/api/#{itopic}/v1/#{individual}/search/?q=%QUERY"
                filter: saveResponse

        # Watch select event
        element.on "typeahead:selected", (input, individual)->
            if scope.model?
                angular.copy(individual, scope.model);
                scope.$apply()
            scope.change() if scope.change?

        # Watch user value event
        element.on "typeahead:uservalue", ()->
            return unless scope.model?
            # Empty selected model
            delete scope.model.id
            # Record the value
            scope.model.name = $(this).val()
            # Evaluate the 'create' expression
            scope.create() if typeof(scope.create) is "function"
            # Apply the scope change
            scope.$apply()

        # Watch change event
        element.on "change", (input)->
            # Filter using the current value
            datum = _.findWhere lastDataset, "name": element.val()
            # If datum exist, use the selected event
            ev = "typeahead:" + (if datum then "selected" else "uservalue")
            # Trigger this even
            element.trigger ev, datum


