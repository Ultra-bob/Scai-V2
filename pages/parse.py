def parse_food(food):
    effects = ", ".join(food["food"]["effects"])
    locations = "\n".join([shop["name_raw"] for shop in food["shops"]])

    return """Food: {name}
            {description}

            ### Nutrition Facts
            NDR: {nutritional_density_rating}/100 (Measure of how filling it is)
            HEI: {hydration_efficacy_index}/100 (Measure of how hydrating it is)
            Effects: [EFFECTS]
                
            ### Purchase Locations
            [PURCHASE]
            """.format(**(food | food["food"])).replace("[EFFECTS]", effects).replace("[PURCHASE]", locations).replace("\t", "").strip()

def parse_weapon(weapon):
    