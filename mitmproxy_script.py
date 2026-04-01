from mitmproxy import http
from mitmproxy import version

def request(flow):
    flow.request.url = "http://localhost:8000/" + flow.request.pretty_url
