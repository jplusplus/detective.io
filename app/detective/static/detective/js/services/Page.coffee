angular.module('detective.service').factory "Page", ["ngProgressLite", "$rootScope", (ngProgressLite, $rootScope)->
    new class Page
        # ──────────────────────────────────────────────────────────────────────────
        # Private attributes and methods
        # ──────────────────────────────────────────────────────────────────────────
        title   = "..."
        loading = false
        # To Title Case 2.0.1 – http://individed.com/code/to-title-case/
        # Copyright © 2008–2012 David Gouch. Licensed under the MIT License.
        toTitleCase = (str)->
            smallWords = /^(a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|vs?\.?|via)$/i
            str.replace /([^\W_]+[^\s-]*) */g, (match, p1, index, title) ->
                return match.toLowerCase()  if index > 0 and index + p1.length isnt title.length and p1.search(smallWords) > -1 and title.charAt(index - 2) isnt ":" and title.charAt(index - 1).search(/[^\s-]/) < 0
                return match  if p1.substr(1).search(/[A-Z]|\../) > -1
                match.charAt(0).toUpperCase() + match.substr(1)
        # ──────────────────────────────────────────────────────────────────────────
        # Public attributes and methods
        # ──────────────────────────────────────────────────────────────────────────
        constructor: ->
            # Hide sidebar when route change
            $rootScope.$on "$routeChangeStart", =>
                @showAside = no
        # Show or not the main aside menu
        showAside: no
        # Page title
        title: (newTitle, titleCase=true)->
            if newTitle?
                title = if titleCase then toTitleCase( "" + newTitle ) else newTitle
            # Always return the title
            if loading then "Loading..." else title
        # Set a new loading state if newLoading is set. Return the loading value
        loading: (newLoading)->
            if newLoading?
                loading = newLoading
                do ngProgressLite[if loading then "start" else "done"]
            # Always return the loading value
            loading
]