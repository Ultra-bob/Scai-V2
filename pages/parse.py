from jinja2 import Environment, FileSystemLoader
from json import loads, dumps
import filters
environment = Environment(loader=FileSystemLoader("templates/"), lstrip_blocks=True, trim_blocks=True)

environment.filters.update({"fix_camelcase": filters.fix_camelcase, "commas": filters.numberFormat})

def parse(data, format_):
    if format_ == "component":
        format_ = f"components/{data['type'].lower()}"
    if format_ == "vehicle":
        return parse_ship(data)
    return environment.get_template(f"{format_}.jinja").render(data)


def parse_ship(data): #! M E G A    F U N C T I O N
    output = ""

    def oprint(text=""):
        nonlocal output
        output += text + "\n"

    for item in data.items():
        match item:
            case "name", type_:
                oprint(f"# Ship Stats: {type_}")
            case "cargo_capacity", capacity:
                oprint(f"Cargo capacity: {capacity} SCU")
            case "sizes", {"length": l, "beam": w, "height": h}:
                oprint(f"Dimensions: {l}m length, {w}m width, {h}m height")
            case "emission", emission:
                oprint(f"Emissions: IR: {emission['ir']}, EM Idle: {emission['em_idle']}, EM Max: {emission['em_max']}")
            case "mass", mass:
                oprint(f"Mass: {mass} kg")
            case "vehicle_inventory", vehicle_inventory:
                oprint(f"Vehicle Inventory: {vehicle_inventory}")
            case "personal_inventory", personal_inventory:
                oprint(f"Personal Inventory: {personal_inventory}")
            case "crew", crew:
                crew_info = f"Crew: Skeleton: {crew['min']}"
                if crew.get("max") is not None:
                    crew_info += f", Max: {crew['max']}"
                if crew.get('weapon') is not None:
                    crew_info += f", Combat: {crew['weapon']}"
                if crew.get('operation') is not None:
                    crew_info += f", Operation: {crew['operation']}"
                oprint(crew_info)
            case "health", health:
                oprint(f"Health: {health}")
            case "shield_hp", shield_hp:
                oprint(f"Shield HP: {shield_hp} (From shield generator)")
            case "speed", speed:
                oprint((f"Speed: SCM: {speed['scm']} m/s, Max: {speed['max']} m/s, "
                        f"0 to SCM: {speed['zero_to_scm']} s, 0 to Max: {speed['zero_to_max']} s, "
                        f"SCM to 0: {speed['scm_to_zero']} s, Max to 0: {speed['max_to_zero']} s"))
            case "fuel", fuel:
                oprint((f"Fuel: Capacity: {fuel['capacity']}L, Intake Rate: {fuel['intake_rate']}L/s, "
                        f"Usage: Main: {fuel['usage']['main']}L/s, Maneuvering: {fuel['usage']['maneuvering']}L/s, "
                        f"Retro: {fuel['usage']['retro']}L/s, VTOL: {fuel['usage']['vtol']}L/s"))
            case "quantum", quantum:
                oprint((f"Quantum: Speed: {quantum['quantum_speed']}km/s, Spool Time: {quantum['quantum_spool_time']} s, "
                        f"Fuel Capacity: {quantum['quantum_fuel_capacity']}L, Range: {quantum['quantum_range']} m"))
            case "agility", agility:
                oprint((f"Agility: Pitch: {agility['pitch']}°/s, Yaw: {agility['yaw']}°/s, Roll: {agility['roll']}°/s, "
                        f"Acceleration: Main: {agility['acceleration']['main']} m/s², "
                        f"Retro: {agility['acceleration']['retro']} m/s², "
                        f"VTOL: {agility['acceleration']['vtol']} m/s², "
                        f"Maneuvering: {agility['acceleration']['maneuvering']} m/s²"))
            case "armor", armor:
                oprint(f"Armor: IR: {armor['signal_infrared']}, EM: {armor['signal_electromagnetic']}, Cross Section: {armor['signal_cross_section']}")
            case "foci", [focus]:
                oprint(f"Focus: {focus}")
            case "foci", foci:
                oprint(f"Foci: {', '.join(foci)}")
            case "type", ship_type:
                oprint(f"Role: {ship_type}")
            case "description", description:
                oprint(f"Description: {description}")
            case "size_class", size_class:
                oprint(f"Size Number: {size_class}")
            case "manufacturer", manufacturer:
                oprint(f"Manufacturer: {manufacturer['name']} ({manufacturer['code']})")
            case "insurance", insurance:  
                oprint((f"Insurance: Claim Time: {filters.minutes_to_time(insurance['claim_time'])}m, Expedite Time: {filters.minutes_to_time(insurance['expedite_time'])}m, "
                        f"Expedite Cost: {insurance['expedite_cost']} aUEC"))
            case "updated_at", updated_at:
                oprint(f"Updated At: {updated_at}")
            case "version", version:
                oprint(f"Version: {version}")
            case "production_status", production_status:
                oprint(f"Production Status: {production_status.replace('-', ' ').title()}")
            case "production_note", production_note if production_note != "None":
                oprint(f"Production Note: {production_note}")
            case "size", size:
                oprint(f"Size: {size.title()}")
            case "msrp", msrp:
                oprint(f"MSRP: ${msrp} USD")
            case "loaner", loaner:
                oprint(f"Loaner Ships: {', '.join(map(lambda x: x['name'], loaner)) if loaner else 'None'}")
            case "hardpoints", components:
                oprint("\n## Components")
                complete_uuids = []
                uid = lambda x: hash(dumps(x.get("item", {}) | {"children": x.get("children", [])}))
                for component in components:
                    if "item" not in component:
                        continue
                    count = lambda search_hash: len([x for x in components if uid(x) == search_hash])
                    if uid(component) in complete_uuids:
                        continue
                    else:
                    #print("adding")
                        complete_uuids.append(uid(component))
                    match component["item"]:
                        case {"type": "MissileLauncher", "name": name, "max_missiles": num_missiles}:
                            qty = count(uid(component))
                            s = "s" if qty > 1 else ""
                            oprint(f"{qty}x {name}{s} carrying {num_missiles} {component['children'][0]['item']['name']}{s} each ({qty*num_missiles} total)")
                            complete_uuids.append(uuid)
                        case {"type": "WeaponGun", "name": name, "size": size}:
                            qty = count(uid(component))
                            s = "s" if qty > 1 else ""
                            oprint(f"{qty}x Size {size} {name}{s}")
                        case {"tags": tags} if "gimbalmount" in tags:
                            qty = count(uid(component))
                            s = "s" if qty > 1 else ""
                            wp = component["children"][0]["item"]
                            #print(wp)
                            oprint(f"{qty}x Gimballed Size {wp['size']} {wp['name']}{s}")
                        case {"name": name, "type": role, "size": size, "grade": grade, "class": class_, "description": description} if description:
                            qty = count(uid(component))
                            role = filters.fix_camelcase(role)
                            s = "s" if qty > 1 else ""
                            oprint(f"{qty}x Size {size} {name} {role}{s} ({class_} grade {grade})")
                            complete_uuids.append(uuid)
                        case {"type": turret_type, "name": name} if turret_type in ["TurretBase", "Turret"]:
                            qty = count(uid(component))
                            weapon = component["children"][0]["item"]
                            wp_s = "s" if qty > 1 else ""
                            s = "s" if qty > 1 else ""
                            weapon_qty = len(component["children"]) #! assumes the turret has all the same weapon (probably true)
                            oprint(f"{qty}x {filters.fix_camelcase(name)}{s} with {weapon_qty}x {weapon['name']}{wp_s}")
                        case edge:
                            ...
                            #print(edge)
                oprint()
            case "slug", slug:
                # Ignored as it seems unimportant to an end-user
                ...
            case "class_name", class_name:
                # Ignored as it seems unimportant to an end-user
                ...
            case "uuid", uuid:
                # Ignored as it seems unimportant to an end-user
                ...
            case "id", id:
                # Ignored as it seems unimportant to an end-user
                ...
            case "chassis_id", chassis_id:
                # Ignored as it seems unimportant to an end-user
                ...
            case "shops", shops:
                oprint("## Buyable at")
                for shop in shops:
                    oprint(f'{shop["name_raw"]} ({shop["items"][0]["price_calculated"]:,} aUEC)')
                oprint()
            case edge:
                pass
                #print(f"Unhandled item: {edge}")
    
    return output