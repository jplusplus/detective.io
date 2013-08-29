class BreadcrumbCtrl
    @$inject: ['$scope', 'Breadcrumb']

    constructor: (@scope, @Breadcrumb)->  
        @scope.isHome = @isHome
        # Monitor breadcrumb refresh
        @scope.$on "breadcrumbRefresh", => @scope.breadcrumbs = @Breadcrumb.getAll()

    # True if we are at home
    isHome: => @scope.breadcrumbs? and @scope.breadcrumbs.length is 1 and @scope.breadcrumbs[0].path is '/'

angular.module('detective').controller 'breadcrumbCtrl', BreadcrumbCtrl