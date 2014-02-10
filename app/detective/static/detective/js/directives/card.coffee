angular.module('detective').directive "card", ['Summary', (Summary)->
    restrict: 'E'
    require: "ngModel"
    scope:
        individual: "=ngModel"
        topic     : "="
        username  : "="
        getType   : "&type"
    templateUrl: "/partial/card.html"
    replace: true
    link: (scope, elm, attr) ->
        scope.type = scope.getType().toLowerCase()
        scope.singleUrl = ->
            if scope.meta
                "/#{scope.username}/#{scope.topic}/#{scope.type}/#{scope.individual.id}/"
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
        scope.hasValue = (f)=> f.name != 'name' and scope.get(f.name)
        Summary.get {id:'forms', topic: scope.topic}, (d)->
            scope.meta = d[scope.type]
]