angular.module('detective').directive "card", ['Summary', (Summary)->
    restrict: 'E'
    require: "ngModel"
    scope: 
        individual: "=ngModel"
        getType: "&type"
    templateUrl: "/partial/card.html"
    replace: true
    link: (scope, elm, attr) ->
        scope.type = scope.getType().toLowerCase()
        scope.singleUrl = -> 
            if scope.meta
                "/#{scope.meta.scope}/#{scope.type}/#{scope.individual.id}/"
            else null
        scope.attr = (name)->
            if scope.meta
                _.findWhere scope.meta.fields, name: name
            else null  
        scope.get = (name)->
            scope.individual[name] or false if scope.individual?          
        # True if the given type is literal
        scope.isLiteral = (field)=>
            [
                "CharField",
                "DateTimeField",
                "URLField",
                "IntegerField"
            ].indexOf(field.type) > -1    
        scope.isString = (t)=> ["CharField", "URLField"].indexOf(t) > -1        
        Summary.get {id:'forms'}, (d)->         
            scope.meta = d[scope.type]
]