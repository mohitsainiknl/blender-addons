# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import types
import pathlib

import bpy
import importlib
from types import ModuleType


bl_info = {
    "name": "CST Tools",
    "blender": (2, 80, 0),
    "category": "Tool",
    "description": "Addon for custom tools",
    "author": "MohitX",
    "version": (0, 0, 1),
    "location": "View3D > Tool > Custom Tools",
    "doc_url": "",
}


cst_path = ''
def load_pref_data():
    def get_cst_path():
        folder = 'custom_tools'
        path_high = bpy.utils.user_resource('SCRIPTS', path = "")
        path_list = path_high.split('\\')
        path_list.pop(-1)
        path_list.pop(-1)
        path_list.append(folder)
        path_main = '\\'.join(path_list)
        if not os.path.isdir(path_main):
            os.mkdir(path_main)
        return path_main
    global cst_path
    try:
        pref = bpy.context.preferences.addons[__name__].preferences
        cst_path = pref.path
    except Exception as e:
        print(e, '<---path')
        cst_path = get_cst_path()
    os.chdir(cst_path)
    if cst_path not in sys.path:
        sys.path.append(cst_path)
load_pref_data()

tool_list = []

def get_tool(module):
    if hasattr(module, 'register') and hasattr(module, 'unregister'):
        tool = module
        tool.is_registered = False
        # tool.cst_panel = 'CST_PT_main_custom_tools'
        return tool
    else:
        return None


def deep_reload(package):
    """Recursively reload modules."""
    def get_package_dependencies(package):
        assert(hasattr(package, "__package__"))
        fn = package.__file__
        if os.path.basename == '__init__.py':
            fn_dir = os.path.dirname(fn) + os.sep
        else:
            fn_dir = os.path.dirname(os.path.dirname(fn)) + os.sep
        node_set = {fn}  # set of module filenames
        node_depth_dict = {fn:0} # tracks the greatest depth that we've seen for each node
        node_pkg_dict = {fn:package} # mapping of module filenames to module objects
        link_set = set() # tuple of (parent module filename, child module filename)
        del fn

        def dependency_traversal_recursive(module, depth):
            for module_child in vars(module).values():

                # skip anything that isn't a module
                if not isinstance(module_child, types.ModuleType):
                    continue

                fn_child = getattr(module_child, "__file__", None)

                # skip anything without a filename or outside the package
                if (fn_child is None) or (not fn_child.startswith(fn_dir)):
                    continue

                # have we seen this module before? if not, add it to the database
                if not fn_child in node_set:
                    node_set.add(fn_child)
                    node_depth_dict[fn_child] = depth
                    node_pkg_dict[fn_child] = module_child
                    
                # set the depth to be the deepest depth we've encountered the node
                node_depth_dict[fn_child] = max(depth, node_depth_dict[fn_child])

                # have we visited this child module from this parent module before?
                if not ((module.__file__, fn_child) in link_set):
                    # print(fn_child)
                    link_set.add((module.__file__, fn_child))
                    dependency_traversal_recursive(module_child, depth+1)
                # else:
                #     raise ValueError("Cycle detected in dependency graph!", module.__file__, fn_child)

        dependency_traversal_recursive(package, 1)
        return (node_pkg_dict, node_depth_dict)
    node_pkg_dict, node_depth_dict = get_package_dependencies(package)
    for (d,v) in sorted([(d,v) for v,d in node_depth_dict.items()], reverse=True):
        print("Reloading %s" % pathlib.Path(v).name)
        importlib.reload(node_pkg_dict[v])

def load_tool_list():
    global tool_list
    new_list = []

    names = [(x[:-3] if x.endswith('.py') else x) for x in os.listdir(cst_path) if x.startswith('tool_') and x.find(' ') == -1]
    # print([mod for mod in sys.modules.keys() if type(mod) is ModuleType and mod.__name__.startswith('tool_')])
    for name in names:
        module = importlib.import_module(name)
        # print(module.__file__)
        if module in tool_list:
            deep_reload(module)

        tool = get_tool(module)
        if tool is not None:
            new_list.append(tool)
    tool_list = new_list
load_tool_list()



_item_map = dict()
def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]

def settings_tool_enum_items(self, context):
    items = [('ALL', '--- ALL ---')] + [(tool.__name__, tool.__name__[5:].replace('_', ' ').title()) for tool in tool_list]
    enum_items = [(item[0], item[1], '', 0, i) for i, item in enumerate(items)]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]

class CST_PT_main_custom_tools(bpy.types.Panel):
    bl_label = 'Custom Tools'
    bl_idname = 'CST_PT_main_custom_tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return True


    def draw(self, context):
        cst = bpy.context.scene.cst
        def draw_box(layout, header_text, prop_name, parent_prop=cst):
            box = layout.box().column()
            row = box.row()
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.separator(factor=0.2)
            row.label(text=header_text)
            row.prop(parent_prop, prop_name, text='', icon_value=(254 if getattr(parent_prop, prop_name) else 253), emboss=False)
            return box

        layout = self.layout.column()
        addons = context.preferences.addons
        if not (__name__ in addons) or not (addons[__name__].preferences.is_show is not None) or addons[__name__].preferences.is_show:
            cst = context.scene.cst
            box = layout.box().column()
            row = box.row(align=True)
            row.scale_y = 1.2
            row.prop(cst, 'tool', text='', icon_value=0, emboss=True)
            row = row.row(align=True)
            row.scale_x = 0.7

            tool = None
            for t in tool_list:
                if t.__name__ == cst.tool:
                    tool = t
                    break
            row2 = row.row(align=True)
            row2.enabled = (tool is not None)
            text = ('Unregister' if tool is not None and tool.is_registered else 'Register')
            op = row2.operator('cst.tool_operations', text=text, icon_value=0, emboss=True, depress=False)
            op.filter = 'NAME'
            op.name = cst.tool
            op.type = text.upper()

            row2 = row.row(align=True)
            op = row2.operator('cst.tool_operations', text='Reload', icon_value=692, emboss=True, depress=False)
            op.filter = 'NAME'
            op.name = cst.tool
            op.type = 'RELOAD'

        box_main = draw_box(layout, 'Main Tools', 'is_main_open')
        # box_other = draw_box(layout, 'Other Tools', 'cst_is_other_open')

        if not freeze_tool_draw:
            for tool in tool_list:
                if tool.is_registered and hasattr(tool, 'draw'):
                    try:
                        tool.draw(self, locals().copy())
                    except Exception as e:
                        print(f'Draw Error {tool.__name__}:', e)


class CST_OT_tool_operations(bpy.types.Operator):
    bl_idname = "cst.tool_operations"
    bl_label = "Tool Operations"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    filter: bpy.props.StringProperty(name='Operation Filter', description='', default='', options={'HIDDEN'}, subtype='NONE', maxlen=0)
    type: bpy.props.StringProperty(name='Operation Type', description='', default='', options={'HIDDEN'}, subtype='NONE', maxlen=0)
    name: bpy.props.StringProperty(name='Operation Name', description='', default='', options={'HIDDEN'}, subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        tool_operations(self.filter, self.type, self.name)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CST_OT_reset_properties(bpy.types.Operator):
    bl_idname = "cst.reset_properties"
    bl_label = "Reset Properties"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    data: bpy.props.StringProperty(name='Data Property', default='', options={'HIDDEN'}, subtype='NONE', maxlen=0)

    def execute(self, context):
        if self.data:
            try:
                data = eval(self.data)
            except Exception as e:
                self.report({'ERROR'}, message=e)
            if data is not None and hasattr(data, 'property_unset'):
                props = [n for n in dir(data) if not n.startswith('_') and not n.startswith('bl_') and not callable(getattr(data, n))]
                defectives = []
                for p in props:
                    try:
                        data.property_unset(p)
                    except:
                        defectives.append(p)
                if defectives:
                    d = ', '.join(defectives)
                    self.report({'WARNING'}, message=f'Error in reseting ({d})')
                return {"FINISHED"}
        self.report({'ERROR'}, message='Data Property not found')
        return {"FINISHED"}


class CST_ADDON_Preference_Interface(bpy.types.AddonPreferences):
    bl_idname = __name__

    path: bpy.props.StringProperty(name='CST Tools Folder Path', description='', default='', options={'HIDDEN'}, subtype='DIR_PATH', maxlen=0)
    is_show: bpy.props.BoolProperty(name='Show Settings', description='', options={'HIDDEN'}, default=True)
 
    def draw(self, context):
        layout = self.layout.column()
        layout.prop(self, 'path', text='Tools Path', icon_value=0, emboss=True)
        layout.prop(self, 'is_show', text='Show Settings', icon_value=0, emboss=True)


def tool_operations(filter, type, name=''):
    def operate_tool(idx, tool, type):
        global tool_list
        if type == 'REGISTER':
            try:
                tool.register()
                tool.is_registered = True
            except Exception as e:
                print(f'Register Error {tool.__name__}:', e)
        elif type == 'UNREGISTER':
            try:
                tool.unregister()
                tool.is_registered = False
            except Exception as e:
                print(f'UnRegister Error {tool.__name__}:', e)
        elif type == 'RELOAD':
            print('reloading tool....')
            operate_tool(idx, tool, 'UNREGISTER')
            deep_reload(tool)
            tool = get_tool(tool)
            operate_tool(idx, tool, 'REGISTER')

    if (filter == 'ALL' or name == 'ALL') and type == 'RELOAD':
        print('reloading all tools....')
        freeze_tool_draw = True
        tool_operations('ALL', 'UNREGISTER')
        load_pref_data()
        load_tool_list()
        tool_operations('ALL', 'REGISTER')
        freeze_tool_draw = False
    else:
        for idx, tool in enumerate(tool_list):
            if filter == 'ALL':
                operate_tool(idx, tool, type)
            elif filter == 'DRAWABLE':
                if hasattr(tool, 'draw'):
                    operate_tool(idx, tool, type)
            elif filter == 'NONE_DRAWABLE':
                if not hasattr(tool, 'draw'):
                    operate_tool(idx, tool, type)
            elif filter == 'NAME':
                if tool.__name__ == name:
                    operate_tool(idx, tool, type)

class CST_GROUP(bpy.types.PropertyGroup):
    tool: bpy.props.EnumProperty(name='Tools', description='', options={'HIDDEN'}, items=settings_tool_enum_items)
    is_main_open: bpy.props.BoolProperty(name='Is Main Open', description='', options={'HIDDEN'}, default=False)

group_classes = [
    CST_GROUP,
]

classes = [
    CST_ADDON_Preference_Interface,
    CST_OT_tool_operations,
    CST_OT_reset_properties,
    CST_PT_main_custom_tools,
]

freeze_tool_draw = True
def register():
    global freeze_tool_draw
    from bpy.utils import register_class

    for cls in group_classes:
        register_class(cls)

    bpy.types.Scene.cst = bpy.props.PointerProperty(name='CST Properties', description='', type=CST_GROUP)

    for cls in classes:
        register_class(cls)

    tool_operations('ALL', 'REGISTER')
    freeze_tool_draw = False

        

def unregister():
    global freeze_tool_draw
    from bpy.utils import unregister_class

    freeze_tool_draw = True
    tool_operations('ALL', 'UNREGISTER')

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.cst

    for cls in reversed(group_classes):
        unregister_class(cls)

if __name__ == '__main__':
    try: bpy.context.scene.mx.addon_unregister.append(unregister)
    except: pass
    register()





