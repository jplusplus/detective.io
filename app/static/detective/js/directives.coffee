detective.directive "scrollTo", ->
    (scope, element, attrs) ->
        scope.$watch "$last", (v) ->
            $(window).scrollTo(element, attrs.scrollTo or 0) if v

detective.directive "typeahead", ($parse)->
    # Use underscore's template 
    # @TODO use $compile from angular
    engine =
        compile: (template)->
            compiled = _.template(template)
            render: (context)-> compiled(context)
    scope:         
        model: "=ttModel"
    link: (scope, element, attrs) ->        
        individual = attrs.ttIndividual.toLowerCase()
        # Set a default value
        element.val scope.model.name if scope.model?
        # Create the typehead
        element.typeahead(        
            name: individual
            template: "<%= name %>"
            engine: engine
            valueKey: "__value__"
            remote: 
                url: "/api/v1/#{individual}/search/?q=%QUERY"
                filter: (response)-> 
                    # Format to datum requirements
                    _.each response.objects, (el, idx)-> el["__value__"] = el["name"]
                    # Return objects list
                    response.objects
        )

        # Watch select event
        element.on "typeahead:selected", (input, individual)->                        
            if scope.model?
                scope.model = individual
                scope.$apply()

detective.directive "watchLoginMandatory", ["$rootScope", "$location", "User", ($root, $location, User) ->
    link: () ->
        $root.$on "$routeChangeStart", (event, current) -> 
            if current.auth and not User.is_logged                
                next = $location.url()
                $location.url("/login?next=#{next}") 
]
