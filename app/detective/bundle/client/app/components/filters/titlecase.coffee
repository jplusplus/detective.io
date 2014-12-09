angular.module('detective').filter "titlecase", ->
    (input="") ->
        smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|nor|of|on|or|per|the|to|vs?\.?|via)$/i
        input.replace /[A-Za-z0-9\u00C0-\u00FF]+[^\s-]*/g, (match, index, title) ->
            return match.toLowerCase()  if index > 0 and index + match.length isnt title.length and match.search(smallWords) > -1 and title.charAt(index - 2) isnt ":" and (title.charAt(index + match.length) isnt "-" or title.charAt(index - 1) is "-") and title.charAt(index - 1).search(/[^\s-]/) < 0
            return match  if match.substr(1).search(/[A-Z]|\../) > -1
            match.charAt(0).toUpperCase() + match.substr(1)

