import itertools

from PyPoE.poe.constants import CraftingBenchCustomActions
from RePoE.parser import Parser_Module
from RePoE.parser.util import write_json, call_with_default_args


class crafting_bench_options(Parser_Module):
    @staticmethod
    def _get_actions(row):
        actions = {}
        if row["AddMod"]:
            actions["add_explicit_mod"] = row["AddMod"]["Id"]
        if row["AddEnchantment"]:
            actions["add_enchant_mod"] = row["AddEnchantment"]["Id"]
        if row["Links"]:
            actions["link_sockets"] = row["Links"]
        if row["SocketColours"]:
            actions["color_sockets"] = row["SocketColours"]
        if row["Sockets"]:
            actions["change_socket_count"] = row["Sockets"]
        if row["CraftingBenchCustomAction"] == CraftingBenchCustomActions.REMOVE_CRAFTED_MODS:
            actions["remove_crafted_mods"] = True
        if row["CraftingBenchCustomAction"] == CraftingBenchCustomActions.REMOVE_ENCHANT_MODS:
            actions["remove_enchantments"] = True
        if len(actions) == 0:
            raise NotImplementedError(f"Crafting option {row['Name']} has an unknown action")
        return actions

    @staticmethod
    def write(file_system, data_path, relational_reader, translation_file_cache, ot_file_cache):
        root = []
        for row in relational_reader["CraftingBenchOptions.dat64"]:
            if row["RequiredLevel"] > 100 or row["IsDisabled"]:
                continue
            item_class_row_lists = [categories["ItemClasses"] for categories in row["CraftingItemClassCategories"]]
            item_class_rows = itertools.chain.from_iterable(item_class_row_lists)
            item_classes = [item_class["Id"] for item_class in item_class_rows]
            root.append(
                {
                    "master": row["HideoutNPCsKey"]["Hideout_NPCsKey"]["Name"],
                    "bench_tier": row["Tier"],
                    "item_classes": item_classes,
                    "cost": {base_item["Id"]: value for base_item, value in row["Cost"]},
                    "actions": crafting_bench_options._get_actions(row),
                }
            )
        write_json(root, data_path, "crafting_bench_options")


if __name__ == "__main__":
    call_with_default_args(crafting_bench_options.write)
