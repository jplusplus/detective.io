
class GraphWorker
    constructor : (@_) ->
        @_.addEventListener 'message', @on_message

    on_message : (event) =>

    post_message : (data) =>
        @_.postMessage data

# Do not run code if we have a window object (means we're not in a Worker)
if not window? then do ->
    # Hack some default vars to make d3 import possible
    noop = ->
        new Function

    self.window = do noop
    self.window.CSSStyleDeclaration = do noop
    self.window.setProperty = do noop

    self.window.Element = do noop
    self.window.Element.setAttribute = do noop
    self.window.Element.setAttributeNS = do noop

    self.window.navigator = do noop

    self.document = do noop
    self.document.documentElement = do noop
    self.document.documentElement.style = do noop

    # Import d3
    importScripts '{{STATIC_URL}}components/custom_d3/d3.js'

    # Create our Worker instance
    worker = new GraphWorker(self)