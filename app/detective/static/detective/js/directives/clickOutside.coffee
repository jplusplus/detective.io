# @src http://stackoverflow.com/questions/12931369/click-everywhere-but-here-event
angular.module('detective.directive').directive "clickOutside", ($document) ->
    restrict: "A"
    link: (scope, elem, attr, ctrl) ->
        elem.bind "click", (e) ->
            # this part keeps it from firing the click on the document.
            e.stopPropagation()
        $document.bind "click.clickoutside", (e)->
            console.log e
            # magic here.
            scope.$apply attr.clickOutside
            true
        # Remove the document click
        scope.$on "$destroy", -> $document.unbind "click.clickoutside"