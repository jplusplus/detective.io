angular.module('detective').filter("nl2br", ->
    return (str='')-> (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1<br />$2')
)