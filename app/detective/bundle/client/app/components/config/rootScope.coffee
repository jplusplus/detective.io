# NOTE : this is a transition file that is NOT part of the config module.
# In the future it most of its method should be delegates to ui-router's states.
angular.module('detective').run(['$rootScope', '$state', 'User', 'Page', '$modal', '$cookies'
    ($rootScope, $state, user, Page, $modal, $cookies)->
        # Services available within templates
        $rootScope.$state = $state
        $rootScope.user   = user
        $rootScope.Page   = Page

        # Only show the message once
        unless $cookies.gotMessage or navigator.userAgent.toLowerCase().indexOf("prerender") > -1
          $modal.open
            controller: [
              '$modalInstance', '$scope', ($modalInstance, $scope)->
                $scope.close = ->
                  # To avoid showing the message again
                  $cookies.gotMessage = 1
                  do $modalInstance.close
            ]
            template: '<button ng-click="close()" class="close">&times;</button>
            <div class="modal-body">
              <p>Hey there,</p>
              <p class="top30">
                In the past 18 months, we worked hard to provide a great tool for network analysis.
                For a wide variety of reasons, we did not succeed.
                <strong>We will retire Detective.io on 20 August 2015.</strong>
                If you have data stored on the platform, please download it before this date.
                It will not be available thereafter.
              </p>
              <p>
                Fortunately, our competitors created fantastic tools,
                such as <a href="http://kumu.io/" target="_blank">Kumu</a> or
                <a href="http://granoproject.org/" target="_blank">Grano Project</a>. Check them out.
              </p>
              <p class="top30"><em>The Detective.io team</em></p>
            </div>
            <div class="modal-footer text-right">
              <button class="btn btn-primary" ng-click="close()">
                Got it
              </button>
            </div>'
  ])
