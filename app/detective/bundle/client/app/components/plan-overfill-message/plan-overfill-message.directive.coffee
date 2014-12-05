(angular.module 'detective.directive').directive 'planOverfillDisplayer', ['$rootScope', '$timeout', ($rootScope, $timeout) ->
    restrict : 'A'
    template : "<div ng-include src='templateUrl' class='plan-overfill-message' ng-if='!hidden'></div>"
    scope    :
        eventHandler: '&ngClick'

    link : (scope, element, attr) ->
        scope.hidden = false

        scope.close = =>
            scope.hidden = true

        $rootScope.$on "user:updated", (ev, user)=>
            scope.plan_name       = user.profile.plan
            scope.topics_max      = user.profile.topics_max
            scope.topics_count    = user.profile.topics_count
            scope.nodes_max       = user.profile.nodes_max
            scope.max_nodes_count = Math.max.apply(null, _.values(user.profile.nodes_count))
            scope.hidden          = false
            element.removeClass("plan-overfill-message--attention")
            # Differents messages to show. Order matter.
            if      scope.nodes_max    > -1 and scope.max_nodes_count >= scope.nodes_max - 10
                # Attention: nodes count >= (max - 10)
                scope.templateUrl = "/partial/components/plan-overfill-messages/attention-nodes.html"
                element.addClass("plan-overfill-message--attention")
            else if scope.nodes_max    > -1 and scope.max_nodes_count >= scope.nodes_max - 20
                # Warning: nodes count >= (max - 20)
                scope.templateUrl = "/partial/components/plan-overfill-messages/warning-nodes.html"
            else if scope.topics_max   > -1 and scope.topics_count    >= scope.topics_max
                # Attention: topics count == max
                scope.templateUrl = "/partial/components/plan-overfill-messages/attention-topics.html"
                element.addClass("plan-overfill-message--attention")
            else
                scope.hidden = true
]

# EOF
