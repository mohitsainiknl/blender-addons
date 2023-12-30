import bpy

# print(__file__, __name__)
# import os
# print(os.path.dirname(os.path.dirname(__file__)))
# print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# print(os.path.abspath(__file__))

def display_collection_id(uid, vars):
    id = f"coll_{uid}"
    for var in vars.keys():
        if var.startswith("i_"):
            id += f"_{var}_{vars[var]}"
    return id


def register_all(classes):
    from bpy.utils import register_class
    for cls in classes:
        try: register_class(cls)
        except Exception as e:
            print(f"Error Registering {str(cls)} :", e)

def unregister_all(classes):
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        try: unregister_class(cls)
        except Exception as e:
            print(f"Error UnRegistering {str(cls)} :", e)



_item_map = dict()
def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]

def get_enum_items(items):
    if items:
        if isinstance(items[0], str):
            enum_items = [(str(item), str(item), '', 0, i) for i, item in enumerate(items)]
        elif isinstance(items[0], list) or  isinstance(items[0], tuple):
            if len(items[0]) == 1:
                enum_items = [(str(item), str(item), '', 0, i) for i, item in enumerate(items)]
            elif len(items[0]) == 2:
                enum_items = [(str(item[0]), str(item[1]), '', 0, i) for i, item in enumerate(items)]
            elif len(items[0]) == 3:
                enum_items = [(str(item[0]), str(item[1]), str(item[2]), 0, i) for i, item in enumerate(items)]
            else:
                enum_items = [(str(item[0]), str(item[1]), str(item[2]), int(item[3]), i) for i, item in enumerate(items)]

        return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]
    return []
