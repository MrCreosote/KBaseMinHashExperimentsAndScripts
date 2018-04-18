#!/usr/bin/env python

from __future__ import print_function
from biokbase.workspace.client import Workspace as _Workspace
import time as _time
from collections import defaultdict as _defaultdict

# Q&D method to summarize KBase reference data workspaces.
# CSV of object id, name, md5 for assemblies. Last version only.

#_URL = 'https://ci.kbase.us/services/ws'
_URL = 'https://kbase.us/services/ws'
#_REF_WS = 15792
_REF_WS = 19217
_TYPE = 'KBaseGenomeAnnotations.Assembly'
_OUT_FILE = 'output.csv'

def main():
    ws = _Workspace(_URL)
    wsinfo = ws.get_workspace_info({'id': _REF_WS})
    ws_size = wsinfo[4]
    print('Processing workspace {} ({}) with {} objects'.format(wsinfo[1], _REF_WS, ws_size))
    print()
    types = _defaultdict(int)
    with open(_OUT_FILE, 'w') as output:
        for i in xrange(0, ws_size, 10000):
            print('Processing objects from {} to {}'.format(i, i + 9999))
            start = _time.time()
            objs = ws.list_objects({'ids': [_REF_WS], 'minObjectID': i, 'maxObjectID': i + 9999})
            end = _time.time()
            print('Got {} objects back in {} sec'.format(len(objs), end - start))
            for o in objs:
                type = o[2]
                types[type] += 1
                ref = str(o[6]) + '/' + str(o[0]) + '/' + str(o[4])
                if type.split('-')[0] != _TYPE:
                    print('Skipping {}, {}'.format(ref, type))
                else:
                    md5 = o[8]
                    name = o[1]
                    output.write('{} {} {} {}\n'.format(ref, name, md5, type))
            print()
    print('Saw types:')
    for type, count in types.items():
        print('{} {}'.format(type, count))

if __name__ == "__main__":
    main()