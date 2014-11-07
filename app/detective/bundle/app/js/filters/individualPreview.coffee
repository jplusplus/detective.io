# Provides a way to preview the value of the given individual
angular.module('detective.filter').filter("individualPreview", ->
    return (i={}, alt=false)-> i._transform or i.name or i.value or i.title or i.units or i.label or alt or ""
)