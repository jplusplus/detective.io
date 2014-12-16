# Return a unique color with the given string
angular.module('detective').filter("strToColor", ->
    return (str="", lum=-0.3) ->
        # @src http://stackoverflow.com/questions/3426404/create-a-hexadecimal-colour-based-on-a-string-with-jquery-javascript
        generateColor = (str)->
            i = hash = 0
            while i < str.length
                # str to hash
                hash = str.charCodeAt(i++) + ((hash << 5) - hash)

            colour = "#"
            for i in [0..2]
                part = (hash >> i++ * 8) & 0xFF
                part = Math.max( Math.min(part, 200), 50)
                # int/hash to hex
                colour += ("00" + part.toString(16) ).slice(-2)
            colour

        if str.toLowerCase?
            # Combinate color generation and brightness
            generateColor( md5( str.toLowerCase() ) )
)