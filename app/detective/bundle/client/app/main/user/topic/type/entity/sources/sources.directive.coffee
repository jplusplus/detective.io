# this directive help us to display a display popover for our sources
angular.module('detective.directive').directive 'sourcesPopover', ['UtilsFactory', (UtilsFactory)->
    restrict: "A"
    templateUrl: "/partial/main/user/topic/type/entity/sources/sources.html"
    replace: true
    scope:
        sources: '=sourcesList'
        orientation: '=?sourcesPopoverOrientation'
    controller: ["$scope", ($scope)->
        $scope.sources = _.uniq $scope.sources, no, (item) -> item.reference
        $scope.isSourceURLValid = (source)=>
            UtilsFactory.isValidURL(source.reference)
    ]
]