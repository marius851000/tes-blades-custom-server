def add_stackable_to_wallet_or_backpack(character_info: dict, item_template_id: str, amount: int, parsed_info: dict):
    item_template = parsed_info["items_template"][item_template_id]
    if item_template["type"] == 5: # in wallet
        if item_template_id in character_info["wallet"]:
            character_info["wallet"][item_template_id] += amount
        else:
            character_info["wallet"][item_template_id] = amount
        return
    elif item_template["type"] == 8: # in backpack
        stackables = character_info["inventory"]["backpack"]["stackableItems"]
        for entry in stackables:
            if entry["itemTemplateId"] == item_template_id:
                entry["count"] += amount
                return
        stackables.append({"itemTemplateId": item_template_id, "count": amount})
        return
    else:
        raise BaseException("Not implemented for type {item_template['type']}")

def increase_inventory_version(character_info: dict):
    character_info["backpack"]["backpackVersion"] += 1
