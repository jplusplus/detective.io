angular.module('detective').factory "Page", ->  
    title = "..."
    #
    #* To Title Case 2.0.1 – http://individed.com/code/to-title-case/
    #* Copyright © 2008–2012 David Gouch. Licensed under the MIT License.
    #
    toTitleCase = (str)->
        smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|vs?\.?|via)$/i
        str.replace /([^\W_]+[^\s-]*) */g, (match, p1, index, title) ->
            return match.toLowerCase()  if index > 0 and index + p1.length isnt title.length and p1.search(smallWords) > -1 and title.charAt(index - 2) isnt ":" and title.charAt(index - 1).search(/[^\s-]/) < 0
            return match  if p1.substr(1).search(/[A-Z]|\../) > -1
            match.charAt(0).toUpperCase() + match.substr(1)

    title   : ->title
    setTitle: (newTitle, titleCase=true)-> 
        title = if titleCase then toTitleCase(newTitle) else newTitle