angular.module('detective').config ["$stateProvider", ($stateProvider)->
    $stateProvider.state('user-topic-article',
        url: '/:username/:topic/p/:slug/'
        controller: ArticleCtrl
        templateUrl: "/partial/main/user/topic/article/article.html"
        resolve:
            topic: UserTopicCtrl.resolve.topic
    )
]