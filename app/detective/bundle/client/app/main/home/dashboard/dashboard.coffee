angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('home.dashboard',
        controller: DashboardCtrl
        templateUrl: '/partial/main/home/dashboard/dashboard.html'
        resolve: DashboardCtrl.resolve
        auth: true
    ) 
]