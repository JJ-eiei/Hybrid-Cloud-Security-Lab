#!/usr/bin/env python3

import sys,json,requests

from datetime import datetime

a=json.load(open(sys.argv[1]))

l=a.get("rule",{}).get("level",0)

requests.post(sys.argv[3],json={"embeds":[
    {"title":f"Wazuh Alert Lv{l}",
     "description":a.get("rule",{}).get("description","N/A"),
     "color":0xFF0000 if l>=12 else 0xFF8C00 if l>=7 else 0xFFFF00,
     "fields":[{"name":"Agent","value":a.get("agent",{}).get("name","N/A"),"inline":True},
               {"name":"Rule","value":str(a.get("rule",{}).get("id","N/A")),"inline":True}]}
    ]})
