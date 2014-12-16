angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('home.tour',
        url: 'tour/?scrollTo'
        controller: TourCtrl
        templateUrl: '/partial/main/home/tour/tour.html'
    )
]