from typing import List

def parse_apparition_settings(settings: List[dict]) -> List[dict]:
    result = []
    for entry in settings:
        result.append({
            "interactable_uuid": entry["_clutterType"]["_uid"]["_id"],
            "weight": entry["_weightMultiplier"],
            "mandatory": entry["_mandatory"], # not sure what that represent, but it seems important
        })
    return result
