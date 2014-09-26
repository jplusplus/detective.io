# @src http://stackoverflow.com/questions/12931369/click-everywhere-but-here-event
angular.module('detective.directive').directive "clickOutside", ($document, $parse) ->
    restrict: "A"
    link: (scope, elem, attr, ctrl) ->
        clickHandler = $parse attr.clickOutside
        elem.bind "click", (e) ->
            # this part keeps it from firing the click on the document.
            e.stopPropagation()
        $document.bind "click.clickoutside", (e)->
            # magic here.
            scope.$apply ->
                clickHandler scope, {$event: e}


            true
        # Remove the document click
        scope.$on "$destroy", -> $document.unbind "click.clickoutside"