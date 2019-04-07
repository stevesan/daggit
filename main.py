import md5

# Example: a simple character customization screen where you can change your 1) team color or 2) your hat material (like..different logos on the hat maybe). Nothing else.
VARS = [
    "teamColor", "hatMaterial"
]

NODES = {
    # Whatever the current hat material is, make sure to keep it updated with the team color.
    "hatColor": {
        "deps": ["teamColor", "hatMaterial"],
        "code": "if(hatMaterial != null) hatMaterial.color = teamColor;"
    },
    # Make sure the team color is on the shirt. (Note: we don't allow changing the shirt material)
    "shirtColor": {
        'deps': ['teamColor'],
        'code': 'shirtMaterial.color = teamColor;'
    },
    # The low LOD billboard for the character, that should be updated when any visual option changes.
    "billboard": {
        'deps': ['hatMaterial', 'hatColor', 'shirtColor'],
        'code': 'regenBillboard();'
    }
}

# TODO: what if, for example, the billboard quantizes the team color, so not every change to team color necessarily needs to cause a billboard regen?
# Should we have another node, like "billboardColor", that relies on team color, but doesn't fire its downstreams if it doesn't change?
# I guess we do need the general notion of, intermediates may not necessarily change, thus don't call FURTHER downstreams..
# Well, i think even at this point, this is still useful.

SETTERS = [
    ["teamColor"],
    ["hatMaterial"],
    # Optimization: If there's a way to change both at the same time, such as presets, avoid some redundant calls.
    ["teamColor", "hatMaterial"]
]


def cap(s):
    return s[0].capitalize() + s[1:]


def update_func_name(node_name):
    return 'update' + cap(node_name)


def dependents(u):
    return [v for v, info in NODES.items() if u in info['deps']]


def topsort(u, visited=None, topsorted=None):
    if topsorted is None:
        topsorted = []
    if visited is None:
        visited = set()
    visited.add(u)
    for v in dependents(u):
        if v not in visited:
            topsort(v, visited, topsorted)
    topsorted.insert(0, u)
    return topsorted


def gen():
    for var in VARS:
        print "let " + var + ";"

    print ''

    # Emit function defs for internal nodes
    for name, node in NODES.items():
        func_name = update_func_name(name)
        print 'function ' + func_name + '() {'
        print '  ' + node['code']
        print '}'
        print ''

    # Perform topological sort, as well as tracking which nodes are affected by which vars.
    # Top-order actually doesn't matter here - this is only used to figure out the affected nodes to mark dirty.
    var2topsorted = {}
    for var in VARS:
        var2topsorted[var] = topsort(var)[1:]

    # TODO we should verify that for each consecutive pair u,v in any list, v shows up after u in all other lists

    for setter in SETTERS:
        # Do a topological sort of all nodes affected by all the vars of this setter.
        # Keep state between individual topsort calls to accomplish this.
        sorted_affected_nodes = []
        visited = set()
        for var in setter:
            topsort(var, visited, sorted_affected_nodes)
        # Shave off the variables themselves from the top sort
        sorted_affected_nodes = sorted_affected_nodes[len(setter):]

        print 'function set_' + \
            '_and_'.join(setter) + \
            '(' + ', '.join(['new_' + v for v in setter]) + ') {'

        for node_name in sorted_affected_nodes:
            print '  let call_' + update_func_name(node_name) + ' = false;'
        print ''

        for var in setter:
            print '  if(' + var + ' != new_' + var + ') {'
            print '    ' + var + ' = new_' + var + ';'

            # Mark all affected nodes as need-to-call
            for node_name in var2topsorted[var]:
                print '    call_' + update_func_name(node_name) + ' = true;'

            print '  }'
            print ''

        for node_name in list(sorted_affected_nodes):
            print '  if(call_' + update_func_name(node_name) + ') {'
            print '    ' + update_func_name(node_name) + '();'
            print '  }'
            print ''
        print '}'
        print ''


gen()
