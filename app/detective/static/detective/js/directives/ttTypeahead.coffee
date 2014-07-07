angular.module('detective.directive').directive "ttTypeahead", ($rootScope, $filter, $compile, $routeParams, User)->
    lastDataset = []

    template =
        compile: (template) ->
            compiled = $compile(template)
            render: (context) ->
                $scope = $rootScope.$new yes
                $scope = angular.extend($scope, context)
                $scope.getModel = ->
                    if context.model?
                        context.model
                    else if context.predicate? and context.predicate.name is '<<INSTANCE>>'
                        context.object
                    else if context.subject?
                        context.subject.label
                    else
                        no
                $scope.getFigureBg = -> $filter("strToColor") $scope.getModel()
                $scope.isList = -> !context.predicate or context.predicate.name isnt '<<INSTANCE>>'

                element = compiled $scope
                do $scope.$apply
                html = do element.html
                do $scope.$destroy
                html

    scope:
        model     : "=ttModel"
        individual: "&ttIndividual"
        topic     : "&ttTopic"
        create    : "&ttCreate"
        submit    : "&ttSubmit"
        remote    : "@"
        prefetch  : "@"
        valueKey  : "@"
        value     : '=?'
        limit     : "@"
        change    : "&"
    link: (scope, element, attrs) ->
        # Select the individual to look for
        individual = (scope.individual() or "").toLowerCase()
        itopic     = (scope.topic() or $routeParams.topic or "common").toLowerCase()
        # Set a default value
        element.val scope.model.name if scope.model?
        element.val scope.value if scope.value?

        scope.$watch 'value', (val)->
            element.val val

        scope.$parent.$watch (-> element.val()), (val)->
            scope.value = val

        # Helper to save the search response
        saveResponse = (response) ->
            lastDataset = response.objects

        bh = new Bloodhound
            datumTokenizer : Bloodhound.tokenizers.obj.whitespace (scope.valueKey or "name")
            queryTokenizer : Bloodhound.tokenizers.whitespace
            dupDetector : (a, b) ->
                a_id = a.id || a.subject.name
                b_id = b.id || b.subject.name
                a_id is b_id
            prefetch :
                url : scope.prefetch or "/api/#{itopic}/v1/#{individual}/mine/"
                filter : saveResponse
            remote :
                url : scope.remote or "/api/#{itopic}/v1/#{individual}/search/?q=%QUERY"
                filter : saveResponse
        bh.storage = null # Hack to disable localStorage caching
        do bh.initialize

        # Create the typehead
        options =
            hint : yes
            highlight : yes
        element.typeahead options,
            displayKey : (scope.valueKey or "name")
            name : 'suggestions'
            source : do bh.ttAdapter
            templates : {
                suggestion : (template.compile [
                    '<div>',
                        '<div class="tt-suggestion__line" ng-class="{\'tt-suggestion__line--with-model\': getModel()}">',
                            '[[name||label]]',
                            '<div class="tt-suggestion__line__model" ng-show="getModel()">',
                                '<div class="tt-suggestion__line__model__figure" ng-style="{ background: getFigureBg()}">',
                                    '<i ng-show="isList()" class="fa fa-list"></i>',
                                '</div>',
                                '[[getModel()]]',
                            '</div>',
                        '</div>',
                    '</div>'
                ].join "").render
            }

        # Watch keys
        element.on "keyup", (event)->
            # Enter is pressed
            if event.keyCode is 13 and scope.submit?
                # Apply the scope change
                scope.$apply =>
                    do scope.submit


        # Watch select event
        element.on "typeahead:selected", (input, individual)->
            if scope.model?
                scope.$apply =>
                    angular.copy(individual, scope.model);
            do scope.change if scope.change?

        # Watch user value event
        element.on "typeahead:uservalue", ()->
            return unless scope.model?
            # Empty selected model
            delete scope.model.id
            # Record the value
            scope.model.name = $(this).val()
            # Evaluate the 'create' expression
            do scope.create if typeof(scope.create) is "function"
            # Apply the scope change
            do scope.$apply

        # Watch change event
        element.on "change", (input)->
            # Filter using the current value
            datum = _.findWhere lastDataset, "name": element.val()
            # If datum exist, use the selected event
            ev = "typeahead:" + (if datum then "selected" else "uservalue")
            # Trigger this even
            element.trigger ev, datum


