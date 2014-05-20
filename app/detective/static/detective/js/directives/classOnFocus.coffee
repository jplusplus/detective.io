angular.module('detective.directive').directive "classOnFocus", ->
	restrict: "A"    
	link: (scope, element, attr) ->
		element.delegate ':input', 'focus', (node)->
			element.addClass attr.classOnFocus
		element.delegate ':input', 'blur', (node)->
			element.removeClass attr.classOnFocus
