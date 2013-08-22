angular
    .module('detectiveFilters', [])
    .filter("nl2br", ->
        return (str='')-> (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1<br />$2')
    ).filter("individualPreview", ->
    	# Provides a way to preview the value of the given individual
        return (i, alt=false)-> i.name or i.value or i.title or i.units or i.label or alt or ""
    )