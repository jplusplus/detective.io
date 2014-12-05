angular.module('detective').directive('noDuplicates', [
    ()->
        require: 'ngModel'
        
        link: (scope, elem, attrs, modelCtrl)->

            # put new parsers at begining of model parsers 
            modelCtrl.$parsers.unshift (viewValue)->
                elements = scope.$eval attrs.noDuplicates 
                elements = elements or []
                included = elements.indexOf(viewValue) != -1
                if not included
                    modelCtrl.$setValidity('nodup', yes)
                    return viewValue
                else 
                    modelCtrl.$setValidity('nodup', no)
                    return undefined

])