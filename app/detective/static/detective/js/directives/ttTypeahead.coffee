angular.module('detective.directive').directive "ttTypeahead", ($rootScope, $filter, $compile, $stateParams, User, TopicsFactory)->
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
                $scope.getModelVerbose = ->
                    model = do $scope.getModel
                    if model
                        for _model in TopicsFactory.topic.models
                            if _model.name is model
                                return _model.verbose_name
                    return model
                $scope.getFigureBg = -> $filter("strToColor") $scope.getModel()
                $scope.isList = -> !context.predicate or context.predicate.name isnt '<<INSTANCE>>'

                element = compiled $scope
                do $scope.$apply
                html = do element.html
                do $scope.$destroy
                html

    scope:
        model                 : "=ttModel"
        individual            : "&ttIndividual"
        topic                 : "&ttTopic"
        create                : "&ttCreate"
        submit                : "&ttSubmit"
        endpoint              : "&ttEndpoint"
        remoteUrl             : "&ttRemoteUrl"
        prefetchUrl           : "&ttPrefetchUrl"
        disableLoadingIcon    : "&ttDisableLoadingIcon"
        disableEmptyResults   : "&ttDisableEmptyResults"
        disableEntityCreation : "&ttDisableEntityCreation"
        emptyResultsSelected  : "&ttEmptyResultsSelected"
        transform             : "&ttTransform"
        valueKey              : "@"
        value                 : '=?'
        limit                 : "@"
        change                : "&"


    link: (scope, element, attrs) ->
        wrapper = undefined

        shouldPrependSearchIcon = ->
            _.has(attrs, 'ttPrependSearchIcon')

        shouldDisableEmptyResults = ->
            _.has(attrs, 'ttDisableEmptyResults')

        shouldDisableEntityCreation = ->
            disabled = false
            if _.has(attrs, 'ttDisableEntityCreation')
                # if attribute is empty (<div tt-disable-entity-creation>) we
                # should simply disable entity creation
                if _.isEmpty(attrs['ttDisableEntityCreation'])
                    disabled = true
                # otherwise  we should evaluation this attribute value
                else
                    disabled = scope.disableEntityCreation()
            disabled

        hasEmptyCallback = ->
            _.has(attrs, 'ttEmptyResultsSelected')

        getEmptyResultDiv = ->
            if shouldDisableEntityCreation()
                div = [
                    "<div>",
                        "<div class='tt-suggestion tt-suggestion__line'>",
                            "Please choose an existing entity.",
                        "</div>",
                    "</div>"
                ]
            else
                div = [
                    "<div class='tt-suggestion'>",
                        "<div class='tt-suggestion__line tt-suggestion__line--with-empty-results'>",
                            "<div class='tt-suggestion__line__figure'>",
                                "<i class='fa fa-plus'></i>",
                            "</div>",
                            "The entity you just typed in is new in the base.<br/>",
                            "Do you want to create it?",
                        "</div>",
                    "</div>"
                ]
            div.join ""

        getSearchIcon = ->
            (wrapper or element.parent()).find('.tt-search-icon i')

        appendSearchIcon = (ttElement)->
            prepend = shouldPrependSearchIcon()
            wrapper = ttElement
            if not wrapper.find('.tt-search-icon').length
                search_icon = $("""
                    <span class='tt-search-icon'>
                        <i class='fa fa-search'></i>
                    </span>
                """)
                wrapper.toggleClass('twitter-typeahead--prepend-icon', prepend)
                wrapper.append search_icon

        # handle loading states
        setLoading = ->
            return if scope.disableLoadingIcon()
            search_icon = getSearchIcon()
            search_icon.removeClass('fa-search')
            search_icon.addClass('fa-circle-o-notch fa-spin')

        setLoaded = ->
            search_icon = getSearchIcon()
            search_icon.removeClass('fa-circle-o-notch fa-spin')
            search_icon.addClass('fa-search')

        # Helper to save the search response
        responseFilter = (response) ->
            if scope.transform()?
                objects = scope.transform(objects: response.objects)
            else
                objects = response.objects
            # Save latest dataset to detect unselected value
            lastDataset = objects
            objects

        onRequestCompleted = (xhr, status)->
            setLoaded()
            data = xhr.responseJSON
            if data? and not data.objects.length
                scope.empty_val = element.val()


        # Set a default value
        element.val scope.model.name if scope.model?
        element.val scope.value if scope.value?

        scope.$watch 'value', (val, old)->
            element.typeahead('val', val) if val
        , yes

        start = =>
            # Select the individual to look for
            individual = scope.individual() or ""
            itopic     = "detective/common"
            if scope.topic? and (do scope.topic)? and (do scope.topic) isnt '/'
                itopic = do scope.topic
            else if $stateParams.username? and $stateParams.topic?
                itopic = "#{$stateParams.username}/#{$stateParams.topic}"
            iendpoint  = scope.endpoint() or 'search'
            # Generate URLs
            prefetchUrl = scope.prefetchUrl() or  "/api/#{itopic}/v1/#{individual}/mine/"
            remoteUrl   = scope.remoteUrl() or "/api/#{itopic}/v1/#{individual}/#{iendpoint}/?q=%QUERY"

            lastDataset = []
            element.typeahead 'destroy'

            bh = new Bloodhound
                datumTokenizer : Bloodhound.tokenizers.obj.whitespace
                queryTokenizer : Bloodhound.tokenizers.whitespace
                dupDetector : (a, b) ->
                    a_id = a.id
                    b_id = b.id
                    if a_id? and b_id?
                        return a_id is b_id
                    false
                prefetch :
                    url : prefetchUrl
                    filter : responseFilter
                remote :
                    url : remoteUrl
                    filter : responseFilter
                    ajax:
                        beforeSend: setLoading
                        complete: onRequestCompleted


            bh.storage = null # Hack to disable localStorage caching
            do bh.initialize

            options =
                # Create the typehead
                hint : yes
                highlight : yes


            typeahead_params =
                displayKey : (scope.valueKey or "name")
                name : 'suggestions-' + itopic.replace '/', '-'
                source : do bh.ttAdapter
                templates :
                    suggestion : (template.compile [
                        '<div>',
                            '<div class="tt-suggestion__line" ng-class="{\'tt-suggestion__line--with-model\': getModel()}">',
                                '[[name||label]]',
                                '<div class="tt-suggestion__line__model" ng-show="getModel()">',
                                    '<div class="tt-suggestion__line__figure" ng-style="{ background: getFigureBg()}">',
                                        '<i ng-show="isList()" class="fa fa-list"></i>',
                                    '</div>',
                                    '[[getModelVerbose()]]',
                                '</div>',
                            '</div>',
                        '</div>'
                    ].join "").render

            unless shouldDisableEmptyResults()
                typeahead_params.templates['empty'] = getEmptyResultDiv()

            # typeahead initialization
            typeahead = element.typeahead options, typeahead_params


            # when typeahead is initialized we can add search/loading indicator
            appendSearchIcon(typeahead.parent())


            # Unbind all events
            (((element.off "keyup").off "change").off "typeahead:selected").off "typeahead:uservalue"

            # Watch keys
            element.on "keyup", (event)->
                # Enter is pressed
                if event.keyCode is 13 and scope.submit?
                    # Apply the scope change
                    scope.$apply =>
                        do scope.submit

            # Watch select event
            element.on "typeahead:selected", (input, individual)->
                if not _.isEmpty(attrs.ttModel)
                    scope.$apply =>
                        # workaround to have same types between individual and
                        # scope.model (source, destionation), if destination
                        # is undefined, the angularJS deep copy will not work.
                        unless scope.model?
                            scope.model = {}

                        if hasEmptyCallback() and not individual
                            angular.copy {name: scope.empty_val}, scope.model
                            scope.empty_val = undefined
                            do scope.emptyResultsSelected
                        else
                            angular.copy individual, scope.model
                            do scope.change


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

            # Loading events

        scope.$watch =>
            do scope.topic
        , (newValue, oldValue) =>
            if newValue? and newValue isnt oldValue
                do start
        , yes

        do start