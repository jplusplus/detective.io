angular.module("detective").directive "unique", ["Individual", (Individual)->
    restrict: 'A'
    require: "ngModel"
    link: (scope, elem, attrs, ctrl) ->

        elem.on "change", -> scope.$apply(->
            return if elem.val() is ""
            # Set validity to false temporary
            # to avoid submitting the form
            # with not-unique value
            ctrl.$setValidity "unique-tmp", false
            # Find the user
            params = type: "user"
            params["#{attrs.unique}__iexact"] = elem.val()
            # Get the individual
            Individual.get params, (d)->
                ctrl.$setValidity "unique", not d.meta.total_count
                ctrl.$setValidity "unique-tmp", true
        )
]