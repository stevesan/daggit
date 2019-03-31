import md5

VARS = [
    "teamColor", "hatMaterial"
]

NODES = [
    {
        "onChange": ["teamColor", "hatMaterial"],
        "code": "if(hatMaterial != null) hatMaterial.color = teamColor;"
    },
    {
        'onChange': ['teamColor'],
        'code': 'shirtColor.color = teamColor;'
    },
    {
        'onChange': ['teamColor'],
        'code': 'pantsColor.color = teamColor;'
    }
]

SETTERS = [
    ["teamColor"],
    ["hatMaterial"],
    ["teamColor", "hatMaterial"]
]


def node_func_name(node):
    return 'on_' + '_or_'.join(node['onChange']) + '_change_' + md5.new(node['code']).hexdigest()[0:8]


def gen():
    for var in VARS:
        print "let " + var + ";"

    print ''

    dep2nodes = {}

    for i, node in enumerate(NODES):
        func_name = node_func_name(node)
        print 'function ' + func_name + '() {'
        print '  ' + node['code']
        print '}'
        print ''

        for dep in node['onChange']:
            if dep not in dep2nodes:
                dep2nodes[dep] = []

            dep2nodes[dep].append(i)

    print ''

    for setter in SETTERS:
        possibly_affected_nodes = set()
        just_one = len(setter) == 1

        for var in setter:
            for node_id in dep2nodes[var]:
                possibly_affected_nodes.add(node_id)

        print 'function set_' + \
            '_and_'.join(setter) + \
            '(' + ', '.join(['new_' + v for v in setter]) + ') {'

        if not just_one:
            for node_id in possibly_affected_nodes:
                node = NODES[node_id]
                print ' let call_' + node_func_name(node) + ' = false;'

        for var in setter:
            print '  if(' + var + ' != new_' + var + ') {'
            print '    ' + var + ' = new_' + var + ';'

            if not just_one:
                # Mark all affected nodes as need-to-call
                for node_id in dep2nodes[var]:
                    node = NODES[node_id]
                    print '    call_' + node_func_name(node) + ' = true;'

            else:
              # Call all
                for node_id in dep2nodes[var]:
                    node = NODES[node_id]
                    print '    ' + node_func_name(node) + '();'

            print '  }'

        if not just_one:
            print ''
            for node_id in list(possibly_affected_nodes):
                node = NODES[node_id]
                print '  if(call_' + node_func_name(node) + ') {'
                print '    ' + node_func_name(node) + '();'
                print '  }'
        print '}'
        print ''


gen()
