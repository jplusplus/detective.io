NotFoundCtrl = ($scope, Page)-> 
    Page.loading false
    Page.title "Page not found"
NotFoundCtrl.$inject = ['$scope', 'Page'];