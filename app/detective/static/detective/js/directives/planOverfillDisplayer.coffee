(angular.module 'detective.directive').directive 'planOverfillDisplayer', ['$rootScope', '$timeout', 'User', ($rootScope, $timeout, User) ->
    restrict : 'A'
    template : "<div ng-include src='templateUrl' class='plan-overfill-message' ng-if='!hidden'></div>"
    scope    :
        eventHandler: '&ngClick'

    link : (scope, element, attr) ->
        scope.hidden = false

        scope.close = =>
            scope.hidden = true

        $rootScope.$on "user:updated", =>
            scope.plan_name       = User.profile.plan
            scope.topics_max      = User.profile.topics_max
            scope.topics_count    = User.profile.topics_count
            scope.nodes_max       = User.profile.nodes_max
            scope.max_nodes_count = Math.max.apply(null, _.values(User.profile.nodes_count))
            scope.hidden          = false
            element.removeClass("plan-overfill-message--attention")
            # Differents messages to show. Order matter.
            if      scope.nodes_max    > -1 and scope.max_nodes_count >= scope.nodes_max - 10
                # Attention: nodes count >= (max - 10)
                scope.templateUrl = "/partial/home.plan-overfill-messages/attention-nodes.html"
                element.addClass("plan-overfill-message--attention")
            else if scope.nodes_max    > -1 and scope.max_nodes_count >= scope.nodes_max - 20
                # Warning: nodes count >= (max - 20)
                scope.templateUrl = "/partial/home.plan-overfill-messages/warning-nodes.html"
            else if scope.topics_max   > -1 and scope.topics_count    >= scope.topics_max
                # Attention: topics count == max
                scope.templateUrl = "/partial/home.plan-overfill-messages/attention-topics.html"
                element.addClass("plan-overfill-message--attention")
            else
                scope.hidden = true
]

# EOF
