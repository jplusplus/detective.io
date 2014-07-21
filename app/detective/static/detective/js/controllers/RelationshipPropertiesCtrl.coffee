class RelationshipPropertiesCtrl
    # Injects dependancies
    @$inject: ['$scope', '$modalInstance', 'Individual', "properties", "relationship", "meta"]
    constructor: (@scope, @modalInstance, @Individual, @properties, @relationship, @meta)->
        # Cancel button just closes the modal
        @scope.cancel = @close
        @scope.save = @save
        @scope.isEditable = @isEditable
        # This relationship may not have properties yet
        @scope.individual = fields: @properties
        # Description of the relationship (source, target, through model)
        @scope.relationship = @relationship
        # Description of the model's fields
        @scope.meta = @meta

    close: (result=@properties)=> @modalInstance.close(result)
    save: =>
        params = id: @properties.id, type: do @relationship.through.toLowerCase
        # The method is not the same if you update or if you save the individual
        action = if params.id? then 'update' else 'save'
        # Save the individual
        promise = @Individual[action](params, @scope.individual.fields).$promise
        # Broadcast a signal when the individual is saved
        promise.then (data)=>
            ev = if action is "save" then "individual:created" else "individual:updated"
            @scope.$broadcast ev, data
        # Close the modal
        @close(promise)

    isEditable: (field)=>
        @isAllowedType(field.type) and
        # We must say explicitely if this field is not editable
        (!field.rules.is_editable? or field.rules.is_editable)

    # True if the given type is allowed
    isAllowedType: (type)=>
        [
            "CharField",
            "DateTimeField",
            "URLField",
            "IntegerField"
        ].indexOf(type) > -1




angular.module('detective.controller').controller 'RelationshipPropertiesCtrl', RelationshipPropertiesCtrl