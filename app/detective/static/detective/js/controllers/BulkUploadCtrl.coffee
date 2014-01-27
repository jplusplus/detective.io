class BulkUploadCtrl
    # Injects dependancies
    @$inject: ['$scope', '$http', '$routeParams', 'Page', 'Individual', '$timeout','Common']

    constructor: (@scope, @http, @routeParams, @Page, @Individual, @timeout, @Common)->
        @Page.title "Bulk Upload", no
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.addFileField   = @addFileField
        @scope.selectTopic    = @selectTopic
        @scope.submit         = @submit
        @scope.onFileSelect   = @onFileSelect
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Get the current topic as default topic
        @scope.topic_selected = @routeParams.topic
        # start with one file field
        @scope.file_fields    = ["file1"]
        @scope.files          = {}

        # CONFIG
        @delay = 3000

    # User submit the form
    submit: =>
        @scope.feedback   = null
        @scope.job_status = null
        # Parameters of your request (to build the url)
        params =
            topic: @scope.topic_selected
        # Send the data
        @scope.feedback = @Individual.bulk params, @scope.files
        # set an interval to provide job status

        @timeout( =>
            if @scope.feedback and @scope.feedback.status == "enqueued" and @scope.feedback.token
                params = { 
                    type: "jobs"
                    id  : @scope.feedback.token
                }
                cancel_refresh = @timeout(refresh_status = =>
                    @Common.get params, (data) =>
                        if data.result?
                            result = JSON.parse(data.result)
                            data.result = result
                        @scope.job_status = data
                        # restart this function again
                        if not @scope.job_status? or @scope.job_status.status == "queued" or @scope.job_status.status == "started"
                            cancel_refresh = @timeout(refresh_status, @delay)
                        else
                            @scope.feedback = null
                , @delay)
                # cancel the timeout if the view is destroyed
                @scope.$on '$destroy', =>
                    @timeout.cancel(cancel_refresh)
        , 1000) # first call

    # User choose a file
    onFileSelect: (files, field) =>
        # Queue the file
        @scope.files[field] = files

    # User ask for a new file field
    addFileField: =>
        field_name = "file" + (@scope.file_fields.length + 1)
        @scope.file_fields.push(field_name)

angular.module('detective').controller 'BulkUploadCtrl', BulkUploadCtrl

# EOF
