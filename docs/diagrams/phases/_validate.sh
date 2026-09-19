#!/bin/bash
# usage: _validate.sh <file.workflow.json>  — prints only diagnostic messages
export PATH="/c/Users/david/tools/node:$PATH"
cd /c/Users/david/projects/archify/archify
node bin/archify.mjs validate workflow "$1" --quality showcase --json 2>&1 | python -c "
import sys,json
d=json.load(sys.stdin)
print('ok:',d.get('ok'))
for x in d.get('diagnostics',[]): print('-',x.get('severity'),x.get('message')[:300])
"
