def generate_dungeon_data(quest_uuid: str, parsed_info: dict) -> dict:
    dungeon_settings_uuid = parsed_info["quests"][quest_uuid]["dungeon_info"]["dungeon_uuid"]
    dungeon_settings = parsed_info["dungeons"][dungeon_settings_uuid]

    # enemy
    enemy_generated_data = {}
    for enemy_group_uuid, enemy_spawn_data in dungeon_settings["spawn_info"]["enemySpawnGroups"].items():
        local_enemy_list = []
        for _ in range(enemy_spawn_data["quantity"]):
            local_enemy_list.append({
                "enemyLevel": 1,
                "givenXp": 1000,
                "spawnGroupLoot": {},
                "lootTableLoot": {
                    # this seems more complicated... Will this not crash?
                    #TODO: tests show this will indeed do an infinite loop
                }
            })
            enemy_generated_data[enemy_group_uuid] = local_enemy_list

    item_generated_data = {}
    for item_uuid, item_data in dungeon_settings["spawn_info"]["item"].items():
        item_generated_data[item_uuid] = {
            "lootTableLoot": {
                # maybe more complicated too. See same entry in enemy
            }
        }

    chest_generated_data = {}
    for chest_uuid, chest_data in dungeon_settings["spawn_info"]["chest"].items():
        chest_generated_data[chest_uuid] = [
            {
                "tier": 1
            }
        ]

    return {
        "questId": quest_uuid,
        "enemyGeneratedData": enemy_generated_data,
        "itemGeneratedData": item_generated_data,
        "chestGeneratedData": chest_generated_data,
        "algorithmVersion": 1,
        "version": 0
    }

def generate_quest_info(quest_uuid: str, parsed_info: dict) -> dict:
    quest_info = parsed_info["quests"][quest_uuid]

    objectives = {}
    for objective_uuid, objective in quest_info["dungeon_info"]["objectives"].items():
        objectives[objective_uuid] = {
            "status": "Active",
            "progress": 0.0,
            "completed": False
        }


    #TODO: manage non-dungeon quest
    return {
        "questId": quest_uuid,
        "version": quest_info["dungeon_info"]["version"],
        "type": "NORMAL",
        "objectiveStatuses": objectives,
        "difficultyLevel": -1,
        "seed": 12345678,
        "gldQuestId": quest_uuid,
        "completed": False
    }

def clear_expired_generated_data(character_info: dict):
    valid_quests = set()
    for quest in character_info["quests"]:
        valid_quests.add(quest["questId"])
    for job in character_info["jobs"]:
        valid_quests.add(job["questId"])
    # Remove dungeonGeneratedDataList entries whose questId is not in valid_quests
    if "dungeonGeneratedDataList" in character_info:
        character_info["dungeonGeneratedDataList"] = [
            entry for entry in character_info["dungeonGeneratedDataList"]
            if entry.get("questId") in valid_quests
        ]
