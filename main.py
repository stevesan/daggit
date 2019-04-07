import md5

VARS = [
    "teamColor", "hatMaterial"
]

NODES = {
    "hatColor": {
        "deps": ["teamColor", "hatMaterial"],
        "code": "if(hatMaterial != null) hatMaterial.color = teamColor;"
    },
    "shirtColor": {
        'deps': ['teamColor'],
        'code': 'shirtMaterial.color = teamColor;'
    },
    "pantsColor": {
        'deps': ['teamColor'],
        'code': 'pantsMaterial.color = teamColor;'
    },
    "billboard": {
        'deps': ['hatColor', 'shirtColor', 'pantsColor'],
        'code': 'regenBillboard();'
    }
}

SETTERS = [
    ["teamColor"],
    ["hatMaterial"],
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


def merge_sorted(a, b):
    if len(a) == 0:
        return b
    if len(b) == 0:
        return a
    c = []
    i = 0
    j = 0
    while True:
        if i < len(a):
            if len(c) == 0 or a[i] != c[-1]:
                c.append(a[i])
            i += 1
        if j < len(b):
            if b[j] != c[-1]:
                c.append(b[j])
            j += 1

        if i >= len(a) and j >= len(b):
            break
    return c


assert merge_sorted([1], [2]) == [1, 2]
assert merge_sorted([1], [1, 2]) == [1, 2]
assert merge_sorted([1, 2], [1, 2]) == [1, 2]
assert merge_sorted([1, 2], [1]) == [1, 2]
assert merge_sorted([1, 2], [2]) == [1, 2]


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
    var2topsorted = {}
    for var in VARS:
        var2topsorted[var] = topsort(var)[1:]

    for var, ts in var2topsorted.items():
        print var
        print ts

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
