from typing import Any, Dict
from mitmproxy.io import FlowReader
from mitmproxy.http import HTTPFlow
import mitmproxy
import urllib.parse
import os
import json

BASE_PATH = "/home/marius/blades/logs/"

for file in os.listdir(BASE_PATH):
    log_path = os.path.join(BASE_PATH, file)
    if os.path.isfile(log_path):
        with open(log_path, "rb") as f:
            reader = FlowReader(f)
            for flow in reader.stream():
                if isinstance(flow, HTTPFlow):
                    url = urllib.parse.urlparse(flow.request.pretty_url)
                    if url.hostname == "blades.bgs.services" and url.path.endswith("accept"):
                        request: Dict[str, Any] = json.loads(flow.response.content.decode("utf-8"))
                        assert(request["quest"]["type"] == "NORMAL")
