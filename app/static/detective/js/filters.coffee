angular
    .module('detectiveFilters', [])
    .filter("nl2br", ->
        return (str='')-> (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1<br />$2')
    ).filter("individualPreview", ->
    	# Provides a way to preview the value of the given individual
        return (i={}, alt=false)-> i.name or i.value or i.title or i.units or i.label or alt or ""
    # Return a unique color with the given string
    ).filter("strToColor", ->
    	return (str="", lum=-0.4) ->
	        # @src http://www.sitepoint.com/javascript-generate-lighter-darker-color/
	        colorLuminance = (hex, lum) ->
	            # validate hex string
	            hex = String(hex).replace(/[^0-9a-f]/g, "")
	            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2]  if hex.length < 6            
	            # convert to decimal and change luminosity
	            colour = "#"
	            for i in [0..2]
	                c = parseInt(hex.substr(i * 2, 2), 16)
	                c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16)
	                colour += ("00" + c).substr(c.length)                
	            colour

	        # @src http://stackoverflow.com/questions/3426404/create-a-hexadecimal-colour-based-on-a-string-with-jquery-javascript
	        generateColor = (str)->    
	            i = hash = 0
	            while i < str.length
	                # str to hash
	                hash = str.charCodeAt(i++) + ((hash << 5) - hash)

	            colour = "#"
	            for i in [0..2]
	                # int/hash to hex
	                colour += ("00" + ((hash >> i++ * 8) & 0xFF).toString(16)).slice(-2)                 
	            colour

	        # Combinate color generation and brightness
	        colorLuminance( generateColor( md5(str.toLowerCase()) ), lum)
    )