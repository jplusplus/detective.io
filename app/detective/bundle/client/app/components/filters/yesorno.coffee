angular.module('detective').filter "yesorno", ->
    (input) ->
        if input? and input then 'yes' else 'no'
