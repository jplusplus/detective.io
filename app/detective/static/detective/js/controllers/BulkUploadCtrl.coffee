class BulkUploadCtrl
    # Injects dependancies
    @$inject: ['$scope', '$http', '$stateParams', '$location', 'Page', 'Individual', '$timeout', 'Common', 'User']

    constructor: (@scope, @http, @stateParams, @location, @Page, @Individual, @timeout, @Common, @User)->
        @Page.title "Bulk Upload", no
        @Page.loading no
        # ──────────────────────────────────────────────────────────────────────
        # Scope methods
        # ──────────────────────────────────────────────────────────────────────
        @scope.addFileField   = @addFileField
        @scope.selectTopic    = @selectTopic
        @scope.submit         = @submit
        @scope.trackJob       = @trackJob
        @scope.onFileSelect   = @onFileSelect
        # ──────────────────────────────────────────────────────────────────────
        # Scope attributes
        # ──────────────────────────────────────────────────────────────────────
        # Get the current topic as default topic
        @scope.topic_selected = @stateParams.topic
        # start with one file field
        @scope.file_fields    = ["file1"]
        @scope.files          = {}
        @scope.files_number   = 0
        @scope.disableForm    = false
        @scope.trackedJob     = false
        @scope.feedback       = null
        @scope.job_status     = null
        @scope.isALongJob     = false

        # Redirect unauthorized user
        @scope.$watch (=> User), =>
            @location.url("/#{@scope.username}/#{@scope.topic}/") unless User.hasChangePermission(@topic)
        , true

        # CONFIG
        @delay = 1500

    # User submit the form
    submit: =>
        @scope.feedback       = null
        @scope.job_status     = null
        @scope.disableForm    = true
        @started_time         = new Date()
        @scope.isALongJob     = false
        @scope.trackedJob     = false
        # Parameters of your request (to build the url)
        params =
            topic: @scope.topic_selected
        # Send the data
        @scope.feedback = @Individual.bulk params, @scope.files
        # set an interval to provide job status
        @scope.feedback.$promise.then =>
            if @scope.feedback and @scope.feedback.status == "enqueued" and @scope.feedback.token
                params =
                    type : "jobs"
                    id   : @scope.feedback.token + "/"
                refresh_timeout = @timeout(refresh_status = =>
                    @Common.get params, (data) =>
                        # format data
                        if data.result?
                            data.result = JSON.parse(data.result)
                        if data.meta?
                            data.meta = JSON.parse(data.meta)
                            if data.meta.saving_progression?
                                data.meta.progress_title = "saving objects in database #{data.meta.saving_progression}/#{data.meta.objects_to_save}"
                                data.meta.progress = (data.meta.saving_progression/data.meta.objects_to_save) * 100
                            else if  data.meta.file_reading_progression?
                                data.meta.progress_title = "reading files (#{data.meta.file_reading})"
                                data.meta.progress = data.meta.file_reading_progression
                            else
                                data.meta.progress_title = "waiting... you are in queue."
                                data.meta.progress = 0
                        if data.exc_info?
                            data.exc_info = data.exc_info.replace(/</g, '&lt;').replace(/>/g, '&gt;')
                        @scope.job_status = data
                        # on queue and long job, trackJob
                        unless @scope.isALongJob or @scope.job_status.status == "queued"
                            if new Date() - @started_time > 10000
                                # if progression is under 20 %
                                if (data.meta.file_reading_progression) < 20
                                    @scope.isALongJob = true
                        if @scope.job_status.status == "queued" or @scope.isALongJob
                            @trackJob() unless @scope.trackedJob
                            @scope.trackedJob = true
                        # restart this function again
                        if not @scope.job_status? or @scope.job_status.status == "queued" or @scope.job_status.status == "started"
                            refresh_timeout = @timeout(refresh_status, @delay)
                        else
                            @scope.feedback = null
                            @scope.disableForm = false
                , @delay)
                # cancel the timeout if the view is destroyed
                @scope.$on '$destroy', =>
                    @timeout.cancel(refresh_timeout)
            else
                console.error("should be @scope.feedback and @scope.feedback.status == \"enqueued\" and @scope.feedback.token ::", @scope.feedback, @scope.feedback.status, @scope.feedback.token)

    # User choose a file
    onFileSelect: (files, field) =>
        # Queue the file
        @scope.files[field] = files
        @scope.files_number = _.size(@scope.files)

    # User ask for a new file field
    addFileField: =>
        field_name = "file" + (@scope.file_fields.length + 1)
        @scope.file_fields.push(field_name)

    # ask to the job to send an email at the end of the proccess
    trackJob: =>
        params =
            type : "jobs"
            id   : @scope.feedback.token + "/"
        @Common.put params, {"track":true}, (data) =>

angular.module('detective.controller').controller 'BulkUploadCtrl', BulkUploadCtrl

# EOF
