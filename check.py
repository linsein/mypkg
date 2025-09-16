#!/usr/bin/env python3

import os
import sys
import json
import shutil
import subprocess
from urllib import request

def notify(needs):
    ntfy_endpoint = os.getenv("NTFY_ENDPOINT")
    if ntfy_endpoint is None:
        raise ValueError("NTFY_ENDPOINT environment is not existed")
    ntfy_token = os.getenv("NTFY_TOKEN")
    
    title = "Pkgs need update: " + ', '.join([d.get("name") for d in needs])
    content = f"There are {len(needs)} packages updated:\n"
    for d in needs:
        content += f"+ {d.get('name')}:[{d.get('old_version')}->{d.get('version')}]: {d.get('url')}\n"
    headers = {"Title": title}
    if ntfy_token is not None:
        headers["Authorization"] = f"Bearer {ntfy_token}"
    req =  request.Request(ntfy_endpoint, data=content.encode('utf-8'), headers=headers)
    request.urlopen(req)

    print(title)
    print(content)

def main():
    cfg = sys.argv[1]
    p = subprocess.Popen(["nvchecker",
                          "-c", cfg,
                          "--logger", "json", "--logging", "info"], stdout=subprocess.PIPE)
    needs = []
    for line in p.stdout:
        if line.strip() == "":
            continue
        d = json.loads(line)
        if d.get("event") != "updated":
            continue
        needs.append(d)

    if len(needs) != 0:
        notify(needs)
        shutil.copy("new_ver.json", "old_ver.json")

if __name__ == '__main__':
    main()
