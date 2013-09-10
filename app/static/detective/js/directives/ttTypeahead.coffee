angular.module('detective').directive "ttTypeahead", ()->
    lastDataset = []
    # Use underscore's template 
    # @TODO use $compile from angular
    engine =
        compile: (template)->
            compiled = _.template(template)
            render: (context)-> compiled(context)
    scope:         
        model : "=ttModel" 
        individual: "&ttIndividual"  
        create: "&ttCreate"  
    link: (scope, element, attrs) ->
        # Select the individual to look for
        individual = (scope.individual() or "").toLowerCase()
        # Set a default value
        element.val scope.model.name if scope.model?
        # Helper to save the search response
        saveResponse = (response)-> lastDataset = response.objects
        # Create the typehead
        element.typeahead    
            name: individual
            template: [
                "<%= name %>",
                "<% if (typeof(model) != 'undefined') { %>",
                    "<div class='model'>",
                        "<%= model %>",
                    "</div>",
                "<% } %>"
            ].join ""
            engine: engine
            valueKey: "name"
            prefetch: 
                url: "/api/v1/#{individual}/mine/"    
                filter: saveResponse
            remote: 
                url: "/api/v1/#{individual}/search/?q=%QUERY"
                filter: saveResponse
                    
        # Watch select event
        element.on "typeahead:selected", (input, individual)->      
            if scope.model?
                angular.copy(individual, scope.model);
                scope.$apply()

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
            $input = $(this)
            # Filter using the current value
            datum = _.findWhere lastDataset, "name": $input.val()            
            # If datum exist, use the selected event
            ev = "typeahead:" + (if datum then "selected" else "uservalue")            
            # Trigger this even
            $input.trigger ev, datum


