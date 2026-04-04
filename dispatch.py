import urllib.parse
import os
from typing import Dict, Optional, Any
import json
import time

BASE_DATA_FOLDER = "./data"

class Response:
    def __init__(self, body: bytes, headers: Dict[str, str], status: int):
        self.body: bytes = body
        self.headers: Dict[str, str] = headers
        self.status: int = status

class Request:
    def __init__(self, url: str, body: Optional[str], headers: Dict[str, str], command: str):
        self.url: str = url
        self.body: Optional[str] = body
        self.headers: Dict[str, str] = headers
        self.command: str = command

class MainSession:
    def __init__(self):
        pass

    def read_character_file(self) -> Dict[str, Any]:
        try:
            result = None
            with open("./character.json", "r") as f:
                result = json.loads(f.read())
            if "town" not in result:
                with open("./default_town.json", "r") as f:
                    default_town = json.loads(f.read())
                    result["town"] = default_town
            return result
        except FileNotFoundError:
            return {
                "character": {}
            }

    def write_character_file(self, content):
        with open("./character.json.tmp", "w") as f:
            f.write(json.dumps(content, indent="\t"))
        os.rename("character.json.tmp", "character.json")

    def read_file_content(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def serve_folder(self, base: str, path: str) -> Optional[bytes]:
        #WARNING: that is vulnerable to path traversal
        built_path = os.path.join(base, path)
        try:
            return self.read_file_content(built_path)
        except FileNotFoundError:
            return None


    def process_request(self, r: Request) -> Response:
        parsed = urllib.parse.urlparse(r.url)
        domain = parsed.netloc
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]

        if domain == "bundles.blades.bgs.services":
            result = self.serve_folder(os.path.join(BASE_DATA_FOLDER, domain), path)
            if result is not None:
                return Response(result, {}, 200)
            else:
                print("Unhandled request to bundles site: " + path)
        elif domain == "blades.bgs.services":
            char_path = None
            if path.startswith("api/game/v1/public/characters/"):
                char_path = path[67:]
            # is that lack of s a typo? most use characters but inventories use character.
            elif path.startswith("api/game/v1/public/character/"):
                char_path = path[66:]

            if path == "api/analytics/v1/public/stats/client" or path == "api/analytics/v1/public/events":
                return Response("null".encode("utf-8"), {}, 200)
            elif path == "api/authentication/v1/public/auth/anon" or path == "api/authentication/v1/public/auth/refresh":
                # The game doesn’t usually call the refresh method.
                return Response(
                    json.dumps({
                        "session": {
                            "sessionId": "e6bc711f-fe3a-4e50-aa6e-7ba07a33c96b",
                            "userId": "ad05151f-324f-4a8e-b60e-a5743a799870",
                            "token": "1234",
                            "schema": "blade_v1",
                            "featureStatus": 7,
                            "linkedAccountsStatus": 4,
                            "tokenExpirationSeconds": int(time.time()) + 3600 * 24 * 3,
                            "deniedFeatures": {
                                "e3_signup_bonus": {
                                    "denyExpiredSecs": 0,
                                    "denyReasonCode": 1
                                }
                            }
                        }
                    }).encode("utf-8"),
                    {"Server-Request-Timestamp": str(int(time.time())), "Server-Timestamp": str(int(time.time()))},
                    200
                )
            elif path == "api/game/v1/public/sync":
                # should I keep track of amount of requests for this session?
                # Or maybe in the lifetime of the whole account?
                return Response(json.dumps({"requestIndex": 0}).encode("utf-8"), {}, 200)
            elif char_path == "":
                assert r.command == "GET"
                return Response(json.dumps({"character": self.read_character_file()["character"]}).encode("utf-8"), {}, 200)
            elif path == "api/game/v1/public/characters":
                if r.command == "GET":
                    return Response(json.dumps({
                        "characters": [
                            self.read_character_file()["character"]
                        ]
                    }).encode("utf-8"), {}, 200)
                elif r.command == "POST":
                    assert r.body is not None
                    character_creation_data = json.loads(r.body.decode("utf-8")) # ty: ignore[unresolved-attribute]
                    data_to_save = {
                        "character": {
                            "id": "3cc48684-1ea9-4241-a45d-132e870bb2ba",
                            "name": character_creation_data["name"],
                            "tagId": "1234",
                            "version": 1,
                            "level": 1,
                            "experience": 1,
                            "maximumAbyssLevelReached": 0,
                            "currentQuestDungeon": None,
                            "lastJobsResetTime": 0,
                            "inventoryLevel": 0,
                            "staminaAttributePoints": 0,
                            "magickaAttributePoints": 0,
                            "lastGuildExchangeRequestTime": 0,
                            "lastGuildExchangeDonationTime": 0,
                            "guildExchangeDonationCount": 0,
                            "pvpChestMeter": 0,
                            "pvpWinningStreak": 0,
                            "pvpExceptionEasierMatchRemaining": 0,
                            "pvpExceptionHarderMatchRemaining": 0,
                            "matchmakingPvpTrophies": 0,
                            "pvpTrophies": 0,
                            "highestArenaReached": 1,
                            "highestLevelArenaReached": 1,
                            "numberPvpMatchPlayed": 0,
                            "trophyCountModifier": 0,
                            "pvpSeasonId": "177b6c32-51d5-4b67-bdda-e46f46127811",
                            "jobDifficultyCycleIndex": 0,
                            "validationFlags": 1,
                            "treasuryLevel": 0,
                            "nameValidated": True,
                            "data": character_creation_data["data"]
                        },
                        "inventory": {
                            "backpackVersion": 1,
                            "loadout": {
                                "equippedItems": {
                                    "417e79de-c810-42f8-8273-f9759df6ae25": {
                                        "id": "2bc300ab-ed27-4ec7-83d3-142eaec3bfea",
                                        "itemTemplateId": "606c8bf6-9dc7-4c5f-b44b-36eb02306c96",
                                        "temperingLevel": 0,
                                        "durability": 75.0,
                                        "slot": "417e79de-c810-42f8-8273-f9759df6ae25"
                                    },
                                    "862605de-c67f-4bce-b527-4e5fb6f25162": {
                                        "id": "787edb6f-6daa-4c21-8a05-49047d77f02a",
                                        "itemTemplateId": "c6f7fab4-eadc-4e8c-bf7f-e0ea095a3acf",
                                        "temperingLevel": 0,
                                        "durability": 100.0,
                                        "slot": "862605de-c67f-4bce-b527-4e5fb6f25162"
                                    },
                                    "897a600c-91d6-4449-af09-173da88a907e": {
                                        "id": "4a439ee7-406d-4506-93f1-4e302f07570b",
                                        "itemTemplateId": "42b6fad8-5ac9-4215-aeff-133715c4c22e",
                                        "temperingLevel": 0,
                                        "durability": 0.0,
                                        "slot": "897a600c-91d6-4449-af09-173da88a907e"
                                    },
                                    "e273a4d7-fb87-4f7e-8f1e-398be59afbcb": {
                                        "id": "28f1c9ca-89b0-4faf-9098-802cad4b74ff",
                                        "itemTemplateId": "2571f818-6ae4-4355-b89a-4a6253089e6c",
                                        "temperingLevel": 0,
                                        "durability": 0.0,
                                        "slot": "e273a4d7-fb87-4f7e-8f1e-398be59afbcb"
                                    }
                                }
                            }
                        }
                    }
                    self.write_character_file(data_to_save)
                    return Response(json.dumps(data_to_save).encode("utf-8"), {}, 200)
            elif char_path == "data":
                assert r.command == "POST"
                character = self.read_character_file()
                assert r.body is not None
                new_data_to_set = json.loads(r.body)["data"]
                if "dialog" in new_data_to_set:
                    # apparently, the client just send the whole list of flag. Let’s trust it.
                    if "dialog" not in character["character"]["data"]:
                        character["character"]["data"]["dialog"] = {}
                    character["character"]["data"]["dialog"] = new_data_to_set["dialog"]
                if "new-flags" in new_data_to_set:
                    if "new-flags" not in character["character"]["data"]:
                        character["character"]["data"]["new-flags"] = {}
                    character["character"]["data"]["new-flags"] = new_data_to_set["new-flags"]
                self.write_character_file(character)
                return Response(b"null", {}, 200)
            elif char_path == "challenges":
                data = self.read_character_file()
                result = {
                    "character": {},
                    "challengeStatus": {}
                }
                for key in data["character"]:
                    if key != "data":
                        result["character"][key] = data["character"][key]
                result["character"]["challengeSeason"] = {
                    "currentSeasonId": "3d336fe7-be60-46a1-b88b-540f3ad5efa2",
                    "rank": 1,
                    "rankRewarded": 0,
                    "points": 0,
                    "seasonYear": 2026,
                    "premium": False
                }
                return Response(json.dumps(result).encode("utf-8"), {}, 200)
            elif path == "api/game/v1/public/catalogoverrides/globalshop":
                return Response(json.dumps({
                    "globalShopOverrides": {}
                }).encode("utf-8"), {}, 200)
            elif char_path == "wallets/current":
                assert r.command == "GET"
                character = self.read_character_file()
                result = {}
                if "wallet" in character:
                    result = {"wallet": character["wallet"]}
                return Response(json.dumps(result).encode("utf-8"), {}, 200)
            elif char_path == "inventories/current":
                assert r.command == "GET"
                character = self.read_character_file()
                return Response(json.dumps({"inventory": character["inventory"]}).encode("utf-8"), {}, 200)
            elif char_path == "abysses/current":
                assert r.command == "POST"
                assert r.body == b"null"
                return Response(json.dumps({}).encode("utf-8"), {}, 200)
            elif char_path == "dungeons":
                assert r.command == "GET"
                character = self.read_character_file()
                result = {}
                if "dungeons" in character:
                    result = {"dungeons": character["dungeons"]}
                return Response(json.dumps(result).encode("utf-8"), {}, 200)

            elif char_path == "towns/current":
                assert r.command == "GET"
                character = self.read_character_file()
                result = {}
                if "town" in character:
                    result = {"town": character["town"]}
                return Response(json.dumps(result).encode("utf-8"), {}, 200)
            elif char_path == "crafts":
                return Response(json.dumps({}).encode("utf-8"), {}, 200)
            elif char_path == "gameevents":
                # I think this is just empty for new account up to a certain point...
                return Response(json.dumps({}).encode("utf-8"), {}, 200)
            elif char_path == "quests":
                #TODO: this will likely break some stuff
                result = None
                with open("./initial_quests.json", "r") as f:
                    initial_quests = json.loads(f.read())
                    result = initial_quests
                result["character"] = self.read_character_file()["character"]
                return Response(json.dumps(result).encode("utf-8"), {}, 200)
            elif char_path == "globalshops/current":
                return Response(json.dumps({}).encode("utf-8"), {}, 200)
            elif char_path == "globalgifts":
                return Response(json.dumps({}).encode("utf-8"), {}, 200)
            elif path == "api/game/v1/public/catalogoverrides/iap":
                return Response(json.dumps({"fulfillmentOverrides": {}}).encode("utf-8"), {}, 200)
            elif char_path == "towns/current/rewards/current":
                return Response(json.dumps({
                    "dailyRewardStatus": {
                        "rewardUid": "eefb9db4-0632-49b9-ae35-1da398ca0003",
                        "until": int(time.time()) + 3600 * 24,
                        "dailyReward": {
                            "stackableItems": {
                                "42d91529-c88b-4c5b-815b-b55508b4e7ef": 2
                            }
                        },
                        "collected": False
                    }
                }).encode("utf-8"), {}, 200)
            elif char_path == "announcements":
                return Response(json.dumps({
                    "announcements": []
                }).encode("utf-8"), {}, 200)
        elif domain.endswith(".api.swrve.com"):
            # just ignore them. Some telemetry stuff. Does sometimes return error callback thought.
            return Response(bytes([]), {}, 200)
        elif domain.endswith(".content.swrve.com"):
            # idem
            return Response("{}".encode("utf-8"), {}, 200)
        elif domain.endswith(".identity.swrve.com"):
            return Response(json.dumps({
                "status": "new_external_id",
                "swrve_id": "a7ef5402-007e-4027-b9ef-efdfe7dddc4c"
            }).encode("utf-8"), {}, 200)
        elif domain == "announcements.blades.bgs.services" and path == "status/status.json":
            return Response(json.dumps({
                "ttl":300,
                "systems":[
                    {"name":"authentication","status":"online"},
                    {"name":"game","status":"online"},
                    {"name":"pvp","status":"online"},
                    {"name":"guilds","status":"online"},
                    {"name":"events","status":"online"},
                    {"name":"social","status":"online"},
                    {"name":"quests","status":"online"},
                    {"name":"challenges","status":"online"},
                    {"name":"shops","status":"online"}
                ]
            }).encode("utf-8"), {}, 200)
        return Response(bytes(0), {}, 401)
