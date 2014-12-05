angular.module('detective.config').config [
    "$stateProvider", "$urlRouterProvider", "$locationProvider",
    ($stateProvider, $urlRouterProvider, $locationProvider)->
        # HTML5 Mode yeah!
        $locationProvider.html5Mode true
        # Not found URL
        $urlRouterProvider.otherwise("/404");

        # ui-router configuration
        $stateProvider
            .state('home',
                url: "/"
                template: '<ui-view/>'
                controller: ["Auth", "$state", (Auth, $state)->
                    unless $state.includes("home.*")
                        if Auth.isAuthenticated()
                            $state.go "home.dashboard"
                        else
                            $state.go "home.tour"
                ]
            )
            .state('home.tour',
                url: 'tour/?scrollTo'
                controller: TourCtrl
                templateUrl: '/partial/main/home/tour/tour.html'
            )
            .state('home.dashboard',
                controller: DashboardCtrl
                templateUrl: '/partial/main/home/dashboard/dashboard.html'
                resolve: DashboardCtrl.resolve
                auth: true
            )
            .state('404-page',
                url: "/404/"
                controller: NotFoundCtrl
                templateUrl: '/partial/main/404/404.html'
            )
            .state('404',
                controller: NotFoundCtrl
                templateUrl: '/partial/main/404/404.html'
            )
            .state('403',
                controller: NotFoundCtrl
                templateUrl: '/partial/main/403/403.html'
            )
            .state('plans',
                url: "/plans/"
                templateUrl: '/partial/main/plans/plans.html'
                controller: ["Page", (Page) ->
                    Page.title "Paid plans"
                ]
            )
            # Accounts
            .state('activate',
                url: "/account/activate/?token"
                controller: UserCtrl
                templateUrl: '/partial/main/account/activation/activation.html'
            )
            .state('reset-password',
                url: "/account/reset-password/?token"
                controller: UserCtrl
                templateUrl: '/partial/main/account/reset-password/reset-password.html'
            )
            .state('reset-password-confirm',
                url: "/account/reset-password-confirm/?token"
                controller: UserCtrl
                templateUrl: '/partial/main/account/reset-password-confirmation/reset-password-confirmation.html'
            )
            .state('login',
                url: "/login/?nextState&nextParams"
                auth: false # authenticated users cannot access this page
                controller: LoginCtrl
                templateUrl: '/partial/main/account/login/login.html'
            )
            .state('signup',
                url: "/signup/?email"
                auth: false # authenticated users cannot access this page
                controller: UserCtrl
                templateUrl: '/partial/main/account/signup/signup.html'
            )
            .state('signup-invitation'
                url: "/signup/:token/"
                controller: UserCtrl
                templateUrl: '/partial/main/account/signup/signup.html'
            )
            .state('subscribe'
                url: "/subscribe/?plan"
                templateUrl: '/partial/main/account/subscribe/subscribe.html'
                controller: UserCtrl
            )
            .state('user-topic-create',
                url: '/create/'
                controller: CreateTopicCtrl
                reloadOnSearch: no
                templateUrl: '/partial/main/home/dashboard/create/create.html'
                resolve: CreateTopicCtrl.resolve
            )
            # Pages
            .state('page',
                url: "/page/:slug/"
                controller: PageCtrl
                # Allow a dynamic loading by setting the templateUrl within controller
                template: "<div ng-include src='templateUrl'></div>"
            )
            # User-related url
            .state('user',
                url: "/:username/"
                template: '<ui-view/>'
                controller: ['Auth', 'User', '$state', '$stateParams', (Auth, User, $state, $stateParams) =>
                    unless $state.includes("user.*")
                        if (do Auth.isAuthenticated) and User.username is $stateParams.username
                            $state.go 'user.me', { username: $stateParams.username }
                        else
                            $state.go 'user.notme', { username: $stateParams.username }
                ]
            )
            .state('user.notme',
                controller: UserProfileCtrl
                templateUrl: "/partial/main/user/user.html"
                default: 'user'
                resolve:
                    user: UserCtrl.resolve.user
                    userGroups: ['Group', '$q', 'user', (Group, $q, user)->
                        deferred = $q.defer()
                        UserProfileCtrl.loadGroups(Group, user, 1).then (results)->
                            deferred.resolve results
                        deferred.promise
                    ]
                    topics: [ 'userGroups', (userGroups)->
                        UserProfileCtrl.getTopics userGroups
                    ]
            )
            .state('user.me',
                auth: true
                controller: UserProfileCtrl
                templateUrl: "/partial/main/user/user.html"
                default: 'user'
                resolve:
                    user: UserCtrl.resolve.user
                    userGroups: ['Group', '$q', 'user', (Group, $q, user)->
                        deferred = $q.defer()
                        UserProfileCtrl.loadGroups(Group, user, 1).then (results)->
                            deferred.resolve results
                        deferred.promise
                    ]
                    topics: [ 'userGroups', (userGroups)->
                        UserProfileCtrl.getTopics userGroups
                    ]
            )
            .state('user.settings',
                auth: true
                controller: AccountSettingsCtrl
                url: 'settings/'
                templateUrl: '/partial/main/account/settings/settings.html'
                default: 'home'
            )
            # ------------------
            # Topic-related URLs
            # ------------------
            # Note:
            #   URL order matters. Like in django if we declare a pattern like
            #   `/user/:type/` before another pattern `/user/stuff/` the second
            #   pattern wont be accessible by its URL and we will never trigger
            #   the proper state.
            .state('user-topic-create.choose-ontology',
                templateUrl: '/partial/main/home/dashboard/create/choose-ontology/choose-ontology.html'
            )
            .state('user-topic-create.customize-ontology',
                controller: EditTopicOntologyCtrl
                templateUrl: '/partial/main/home/dashboard/create/customize-ontology/customize-ontology.html'
            )
            .state('user-topic-create.describe',
                templateUrl: '/partial/main/home/dashboard/create/describe/describe.html'
            )
            # check previous comment before changing URLs order.
            .state('user-topic',
                url: "/:username/:topic/"
                controller: ExploreCtrl
                resolve:
                    topic: UserTopicCtrl.resolve.topic
                # Allow a dynamic loading by setting the templateUrl within controller
                template: "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"
            )
            .state('user-topic.network',
                url: "network/"
                # Allow a dynamic loading by setting the templateUrl within controller
                template: "<div ng-include src='templateUrl' ng-if='templateUrl'></div>"
            )
            .state('user-topic-edit',
                url: "/:username/:topic/settings/"
                controller: EditTopicCtrl
                templateUrl: '/partial/main/user/topic/settings/settings.html'
                resolve:
                    topic: UserTopicCtrl.resolve.topic
                auth: true
                owner: true
            )
            .state('user-topic-delete',
                url: "/:username/:topic/delete/"
                controller: DeleteTopicCtrl
                templateUrl: '/partial/main/user/topic/delete/delete.html'
                resolve:
                    topic: UserTopicCtrl.resolve.topic
                auth: true
                owner: true
            )
            .state('user-topic-invite',
                url: "/:username/:topic/invite/"
                controller: AddCollaboratorsCtrl
                templateUrl: '/partial/main/user/topic/invite/invite.html'
                resolve:
                    topic: UserTopicCtrl.resolve.topic
                    collaborators: AddCollaboratorsCtrl.resolve.collaborators
                    administrators: AddCollaboratorsCtrl.resolve.administrators
                auth: true
                admin: yes
            )
            .state('user-topic-search',
                url: '/:username/:topic/search/?q&page'
                controller: IndividualSearchCtrl
                templateUrl: "/partial/main/user/topic/type/type.html"
                reloadOnSearch: true
                resolve:
                    topic: UserTopicCtrl.resolve.topic
            )
             # Topic-related url
            .state('user-topic-article',
                url: '/:username/:topic/p/:slug/'
                controller: ArticleCtrl
                templateUrl: "/partial/main/user/topic/article/article.html"
                resolve:
                    topic: UserTopicCtrl.resolve.topic
            )
            .state('user-topic-contribute',
                url: '/:username/:topic/contribute/?id&type'
                controller: ContributeCtrl
                templateUrl: "/partial/main/user/topic/contribute/contribute.html"
                resolve:
                    forms: UserTopicCtrl.resolve.forms
                    topic: UserTopicCtrl.resolve.topic
                auth: true
            )
            .state('user-topic-contribute-upload',
                url: '/:username/:topic/contribute/upload/'
                controller: BulkUploadCtrl
                templateUrl: "/partial/main/user/topic/contribute/bulk-upload/bulk-upload.html"
                resolve:
                    topic: UserTopicCtrl.resolve.topic
                auth: true
            )
            .state('user-topic-list',
                url: '/:username/:topic/:type/?page'
                controller: IndividualListCtrl
                templateUrl: "/partial/main/user/topic/type/type.html"
                reloadOnSearch: true
                resolve:
                    topic: UserTopicCtrl.resolve.topic
            )
            .state('user-topic-detail',
                url: '/:username/:topic/:type/:id/'
                controller: IndividualSingleCtrl
                templateUrl: "/partial/main/user/topic/type/entity/entity.html"
                reloadOnSearch: true
                resolve:
                    topic: UserTopicCtrl.resolve.topic
                    forms: UserTopicCtrl.resolve.forms
                    individual: UserTopicCtrl.resolve.individual
            )
            .state('user-topic-detail.network',
                url: 'network/'
                templateUrl: "/partial/main/topic/type/entity/network/network.html"
            )
]