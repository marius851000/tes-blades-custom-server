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
                    if url.hostname == "blades.bgs.services" and url.path.startswith("/api/game/v1/public/characters/") and url.path.endswith("/data"):
                        request: Dict[str, Any] = json.loads(flow.request.content.decode("utf-8"))
                        assert "data" in request
                        assert len(request.keys()) == 1
                        # check that data does not contain unexpected keys
                        for key in request["data"].keys():
                            if key not in ["dialog", "new-flags"]:
                                raise ValueError(f"Unexpected key {key} in data")
                        if "dialog" in request["data"]:
                            dialog = request["data"]["dialog"]
                            assert "Flags" in dialog
                            assert len(dialog.keys()) == 1
                            flags = dialog["Flags"]
                            for entry in flags:
                                assert "NpcUid" in entry
                                assert "QuestUid" in entry
                                assert "FlagId" in entry
                                npc_set = entry["NpcUid"]["_v"] != ""
                                quest_set = entry["QuestUid"]["_v"] != ""
                                flag_set = entry["FlagId"]["_v"] != ""
                                # all combination of present/unpresent is valid for npcuid and questuid, but flagid is always defined
                                if npc_set and not quest_set and flag_set:
                                    pass
                                elif not npc_set and not quest_set and flag_set:
                                    pass
                                elif not npc_set and quest_set and flag_set:
                                    pass
                                elif npc_set and quest_set and flag_set:
                                    pass
                                else:
                                    print(npc_set, quest_set, flag_set)
                                    raise BaseException()
                                for a in entry.keys():
                                    assert a in ["NpcUid", "QuestUid", "FlagId", "Value"]
                                assert entry["Value"]["_t"] == "Int32"
                        # new-flags, as in, added post-release?
                        if "new-flags" in request["data"]:
                            new_flags = request["data"]["new-flags"]
                            print(new_flags)
