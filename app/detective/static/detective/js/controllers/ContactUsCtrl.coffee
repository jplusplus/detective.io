class ContactUsCtrl
    # Injects dependancies
    @$inject: ['$scope', '$stateParams', 'Page', 'Individual']

    constructor: (@scope,  @stateParams, @Page, @Individual)->
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @Page.title "Contact us", no

        @scope.records_sizes = [
            [0, "Less than 200"],
            [200, "Between 200 and 1000"],
            [1000, "Between 1000 and 10k"],
            [10000, "More than 10k"],
            [-1, "I don't know yet"],
        ]

        @scope.users_sizes = [
            [1, "1"],
            [5, "1-5"],
            [0, "More than 5"],
            [-1, "I don't know yet"],
        ]

        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        @scope.submit = @submit

    submit: =>
        if @scope.form.$valid
            # Switches to loading mode
            @scope.loading = yes
            # Create the quoteRequest object
            quoteRequest = new @Individual(@scope.qr)
            quoteRequest.$save type: 'quoterequest', =>
                # Ends the loading mode
                @scope.requestSucceed = yes
                @scope.loading = no
            # Handles error
            , (response)=>
                data = response.data
                # Loading mode off
                @scope.loading = no
                # Add an error message
                @scope.error = data.error if data.error_message?



angular.module('detective.controller').controller 'contactUsCtrl', ContactUsCtrl