from pathlib import Path
from typing import Dict, List
from typing import Optional
import os
import json
import yaml

OUT_PATH = "./parsed.json"
SOURCE_PATH = "/home/marius/blades/decompunityapk/ExportedProject"
QUESTDATA_GUID = "5cc072dcf7a2ad3459c439adc756d484"
LEVELDATA_PATH = "Assets/export/gameplaymetadata/LevelData.asset"

# from gpt-oss:20b
def find_all_case_insensitive(
    root: Path | str,
    rel_path: Path | str,
) -> Path:
    """
    Recursively search *root* for *rel_path* treating each component
    case‑insensitively.  Returns the first matching full path.
    Raises FileNotFoundError if no match is found.

    Parameters
    ----------
    root : Path or str
        Absolute path to the directory that will be searched.
    rel_path : Path or str
        Relative path (e.g. "Assets/BGS/Levels/Arena.asset").

    Returns
    -------
    Path
        The first full path that matches the case‑insensitive search.
    """
    root = Path(root).resolve()
    parts = Path(rel_path).parts

    def _recurse(current: Path, remaining: List[str]) -> List[Path]:
        if not remaining:
            return [current] if current.exists() else []

        part = remaining[0]
        # Find *all* children that match the current component ignoring case.
        candidates = [
            p for p in current.iterdir()
            if p.name.lower() == part.lower()
        ]

        results: List[Path] = []
        for cand in candidates:
            results.extend(_recurse(cand, remaining[1:]))
        return results

    matches = _recurse(root, list(parts))
    if not matches:
        raise FileNotFoundError(f"No file matching {rel_path!r} found under {root!r}")
    return matches[0]

class UnityAssetMeta:
    def __init__(self, meta, asset_path):
        self.guid = meta["guid"]
        self.path = asset_path

class UnityAssets:
    def __init__(self, folder):
        self.base_folder = folder
        self.guid_to_info: Dict[str, UnityAssetMeta] = {}
        for path, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".asset"):
                    file_path = os.path.join(path, file)
                    meta_path = file_path + ".meta"
                    try:
                        with open(meta_path, "r") as f:
                            meta_data = yaml.safe_load(f.read())
                    except FileNotFoundError:
                        continue
                    self.guid_to_info[meta_data["guid"]] = UnityAssetMeta(meta_data, file_path)



class Analyzer:
    def __init__(self, assets: UnityAssets):
        pass


def unity_tag_constructor(loader, tag_suffix, node):
    return loader.construct_mapping(node)

yaml.add_multi_constructor("tag:unity3d.com,2011:", unity_tag_constructor)
yaml.add_multi_constructor("tag:unity3d.com,2011:", unity_tag_constructor, Loader=yaml.SafeLoader)

if __name__ == "__main__":
    print("loading assets")
    assets = UnityAssets(SOURCE_PATH)
    to_export = {}
    print("loading quest data id mapping")
    quest_definition_uuid_to_guid = {}
    with open(assets.guid_to_info[QUESTDATA_GUID].path, "r") as f_leveldata:
        quest_data = yaml.safe_load(f_leveldata.read())
        for entry in quest_data["MonoBehaviour"]["_keyQuestList"]:
            quest_definition_uuid_to_guid[entry["Key"]] = entry["QuestValue"]["guid"]
    print("loading quest definition data themself")
    quest_definition_by_uuid = {}
    for quest_uuid, quest_guid in quest_definition_uuid_to_guid.items():
        with open(assets.guid_to_info[quest_guid].path, "r") as f_leveldata:
            quest_definition_data_container = yaml.safe_load(f_leveldata.read())
        quest_definition_data = json.loads(quest_definition_data_container["MonoBehaviour"]["_serializedJsonString"])
        quest_definition_by_uuid[quest_uuid] = quest_definition_data
    print("loading dungeon settings")
    dungeon_settings_by_uuid = {}
    with open(os.path.join(SOURCE_PATH, LEVELDATA_PATH), "r") as f_leveldata:
        level_data_list_file = yaml.safe_load(f_leveldata.read())
        for level_meta in level_data_list_file["MonoBehaviour"]["_levelList"]:
            level_uuid = level_meta["Id"]
            level_handle = level_meta["ResourceHandle"]
            level_path = level_meta["Path"]
            with open(find_all_case_insensitive(SOURCE_PATH, level_path), "r") as f_thislevel:
                raw_level_data = yaml.safe_load(f_thislevel.read())
                dungeon_settings_by_uuid[level_uuid] = {
                    "handle": level_handle,
                    "raw_data": raw_level_data
                }
    print("exporting...")
    with open(OUT_PATH, "w") as f:
        f.write(json.dumps({
            "quests": quest_definition_by_uuid,
            "dungeons": dungeon_settings_by_uuid
        }))
