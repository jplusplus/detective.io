class BreadcrumbCtrl
    @$inject: ['$scope', 'Breadcrumb']

    constructor: (@scope, @Breadcrumb)->  
        # Monitor breadcrumb refresh
        @scope.$on "breadcrumbRefresh", => @scope.breadcrumb = @Breadcrumb.getAll()


angular.module('detective').controller 'breadcrumbCtrl', BreadcrumbCtrl