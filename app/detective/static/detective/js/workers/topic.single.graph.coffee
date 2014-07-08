class GraphWorker
    constructor : (@_) ->
        @_.addEventListener 'message', @on_message

        @d3_layout = d3.layout.force();

        @aggregation_type = '__aggregation_bubble'
        @aggregation_threshold = 3
        @aggregated_edges = []
        @aggregation_index = 0

    is_current : (id) =>
        @current_id is parseInt id

    sort_and_reindex : (array) ->
        array = _.sortBy array, (datum) -> -datum.weight
        _.each array, (datum, i) -> datum._index = i
        array

    can_aggregate : (leaf) ->
        (not @is_current leaf._id) and (leaf._type isnt @aggregation_type)


    aggregate : (leafs_to_aggregate) ->
        quick = no
        if not leafs_to_aggregate?
            leafs_to_aggregate = @leafs
            quick = yes

        do =>
            clean = (do =>
                for leaf in @leafs
                    continue if not (leaf in leafs_to_aggregate)
                    # Check if we need to delete a node
                    if leaf.weight > @aggregation_threshold
                        # If so, we're removing the first we encounter
                        for edge in @edges
                            if (edge.source._id is leaf._id) and @can_aggregate edge.target
                                @delete_leaf edge.target, leaf
                                do ((@d3_layout.nodes @leafs).links @edges).start
                                @leafs = @sort_and_reindex @leafs
                                # Aaaaand, we're going back to the top
                                return no
                            else if (edge.target._id is leaf._id) and @can_aggregate edge.source
                                @delete_leaf edge.source, leaf
                                do ((@d3_layout.nodes @leafs).links @edges).start
                                @leafs = @sort_and_reindex @leafs
                                # Aaaaand, we're going back to the top
                                return no
                    else if quick
                        # As leafs are sorted by weight
                        # if we encounter one leaf.weight <= threshold then we
                        # don't need to iterate to the next one
                        return yes
                return yes
            ) while not clean

    # Helper function deleting a leaf and all its edges
    delete_leaf : (leaf, source_leaf=null) ->
        # We delete the leaf and reindex the array
        @leafs.splice leaf._index, 1

        # If there's a sourceLeaf we need to move leaf in its aggregation bubble
        if source_leaf?
            if source_leaf._bubble
                source_leaf._bubble.leafs.push leaf
                source_leaf._bubble.name = "#{source_leaf._bubble.leafs.length} more entities"
            else
                source_leaf._bubble =
                    leafs : [leaf]
                    _id : --@aggregation_index
                    _type : @aggregation_type
                    name : '1 more entity'
                @edges.push
                    source : source_leaf
                    target : source_leaf._bubble
                    _type : 'is_related_to+'
                @leafs.push source_leaf._bubble

        do ((@d3_layout.nodes @leafs).links @edges).start
        @leafs = @sort_and_reindex @leafs

        # If there is no edge to delete, we can return
        return unless leaf.weight > 0

        # Clean edges, one at a time
        do =>
            clean = (do =>
                for index, edge of @edges
                    # Is this edge concerning our leaf?
                    is_concerned = [edge.source._id, edge.target._id].indexOf leaf._id
                    if is_concerned >= 0
                        leaf_to_check = if is_concerned is 0 then edge.target else edge.source
                        @aggregated_edges.push (@edges.splice index, 1)[0]
                        do ((@d3_layout.nodes @leafs).links @edges).start
                        # If we deleted the last edge of a leaf, we have to delete that leaf
                        (@delete_leaf leaf_to_check) if leaf_to_check.weight <= 0
                        # Aaaaand, we're going back to the top
                        return no
                # We're done!
                return yes
            ) while not clean

    load_leafs : (leafs_to_load) =>
        if not leafs_to_load.length?
            leafs_to_load = [leafs_to_load]

        loaded = _.clone leafs_to_load

        for leaf in leafs_to_load
            clean = no

            @leafs.push leaf
            do ((@d3_layout.nodes @leafs).links @edges).start
            @leafs = @sort_and_reindex @leafs

            clean = (do =>
                for edge, i in @aggregated_edges
                    is_concerned = [edge.source._id, edge.target._id].indexOf leaf._id
                    if is_concerned >= 0
                        [_edge] = @aggregated_edges.splice i, 1
                        @edges.push _edge

                        if (is_concerned is 0) and not (_.findWhere @leafs, { _id : edge.target._id })?
                            loaded = loaded.concat (@load_leafs edge.target)
                        else if not (_.findWhere @leafs, { _id : edge.source._id })?
                            loaded = loaded.concat (@load_leafs edge.source)

                        do ((@d3_layout.nodes @leafs).links @edges).start
                        return no
                return yes
            ) while not clean
        loaded

    load_from_leaf : (source_leaf) =>
        source_leaf = _.findWhere @leafs,
            _id : source_leaf._id
        leafs_to_load = (source_leaf.leafs.splice 0, 2)

        if (source_leaf.leafs.length > 0)
            source_leaf.name = "#{source_leaf.leafs.length} more entities"
            @log 'update aggregation leaf count ' + source_leaf.leafs.length
        else
            @delete_leaf source_leaf

        loaded = @load_leafs leafs_to_load
        @aggregate loaded

        # @leafs = @sort_and_reindex @leafs

        do @ask_update

    init : (data) =>
        @current_id = parseInt data.current_id
        @leafs = data.leafs
        @edges = data.edges
        do ((@d3_layout.nodes @leafs).links @edges).start
        @leafs = @sort_and_reindex @leafs
        do @aggregate
        do @ask_update

    on_message : (event) =>
        switch event.data.type
            when 'init' then @init event.data.data
            when 'get_from_leaf' then @load_from_leaf event.data.data
            else
                @log "Can't perform action <#{event.data.type}>."

    log : (message) =>
        @post_message
            type : 'log'
            data : message

    ask_update : =>
        @post_message
            type : 'update'
            data :
                leafs : @leafs
                edges : @edges

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
    importScripts '/proxy/custom_d3/d3.js'
    importScripts '/proxy/components/underscore/underscore-min.js'

    # Create our Worker instance
    worker = new GraphWorker(self)