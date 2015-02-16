class window.EditTopicBatchCtrl
    @$inject: ['$scope', 'Page', '$rootScope', 'TopicsFactory', '$modal', '$stateParams']
    constructor: (@scope, @Page, @rootScope,  @TopicsFactory, @modal, @stateParams)->
        # Parse the given CSV using header
        @csv = Papa.parse @stateParams.csv, header: yes, dynamicTyping: yes, skipEmptyLines: yes

        console.log @getModels(@csv)

    getModels: (csv)=>
        # Collects stat for every field
        stats = @getFieldsStats csv
        # Fields reconized as models
        models = []
        properties = []
        # Analyse every field
        for field in csv.meta.fields
            # The given field may be a model
            if @mayBeModel field, stats, csv
                # Add the field to the models list
                models.push name: field, properties: []
            else
                properties.push field
        # If we detect some models
        if models.length
            # Import every remaining properties into the first model
            models[0].properties = properties
        # Every model must be connected together by default
        for model in models
            for target in models
                # Avoid self-directed relationship
                if model.name isnt target.name
                    model.properties = model.properties.concat target.name
        models

    # Reconizes if a field is a model using the csv's statistics
    mayBeModel: (field, stats, csv)=>
        count = csv.data.length
        # Is mostly using string
        mostlyString = stats[field].numericValues/count < 0.2
        # Does not contain any empty value
        hasntEmpty = not stats[field].emptyValues
        # Is mostly value, NOT link
        mostlyValue = stats[field].httpValues/count < 0.2
        # Every condition have to be true
        mostlyString and hasntEmpty and mostlyValue

    # Fetch the CSV rows to extract per-field statistic
    getFieldsStats: (csv)=>
        # Prepare an object where every field is an attribute
        # that describes the statitis for this field
        stats = _.reduce csv.meta.fields, (result, field)->
            result[field] =
                numericValues: 0
                emptyValues  : 0
                httpValues   : 0
            result
        , {}
        # Fetch the csv value to make some statistics
        for row in @csv.data
            for field, value of row
                # test for empty value
                if value and value isnt ''
                    # Test for numeric value
                    stats[field].numericValues += not isNaN value
                    # test for http value
                    stats[field].httpValues += ('' + value).indexOf('http') is 0
                else
                    # Count emtpy values too
                    stats[field].emptyValues += 1
        # Returns stats object
        stats



angular.module('detective').controller 'editTopicBatchCtrl', EditTopicBatchCtrl
# EOF
