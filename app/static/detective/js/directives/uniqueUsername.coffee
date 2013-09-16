angular.module("detective").directive "uniqueUsername", ["Individual", (Individual)->    
    restrict: 'A'
    require: "ngModel"
    link: (scope, elem, attrs, ctrl) ->
        # Set validity to false temporary 
        # to avoid submitting the form 
        # with not-unique value
        ctrl.$parsers.push -> ctrl.$setValidity "unique-tmp", false

        elem.on "change", -> scope.$apply(->
            return if elem.val() is ""
            # Find the user    
            params = 
                type     : "user"
                username : elem.val()                
           
            # Get the individual
            Individual.get params, (d)->            
                ctrl.$setValidity "unique", not d.meta.total_count      
                ctrl.$setValidity "unique-tmp", true
        )         
]