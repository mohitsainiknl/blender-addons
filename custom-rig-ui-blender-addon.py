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

import bpy

bl_info = {
    "name": "CUI Addon",
    "author": "MohitX",
    "version": (0, 1, 1, 1),
    "blender": (3, 4, 0)    
}

def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0

class CUI_OT_DUMMY_BUTTON_OPERATOR(bpy.types.Operator):
    bl_idname = "cui.dummy_button_operator"
    bl_label = "Dummy Button"
    bl_description = "no operator attached to this button"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_SET_ICON(bpy.types.Operator):
    bl_idname = "cui.set_icon"
    bl_label = "Set Icon"
    bl_description = "Sets this icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    icon_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    prop_name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"}, default="icon")
    icon: bpy.props.IntProperty(options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def description(self, context, properties):
        icon_num = properties.icon
        icon_name = 'Name not found'
        for icon in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items:
            if icon.value == icon_num:
                break
        return (
            f"Number : {icon_num}\n"
            f"Name : {icon.name.replace('_', ' ').title()}"
        )

    def execute(self, context):
        has_error = False
        try:
            data = eval(self.icon_data_path)
        except:
            print('Error : icon_data_path is not correct')
            has_error = True
        if not has_error:
            setattr(data, self.prop_name, self.icon)
            context.area.tag_redraw()
        return {"FINISHED"}

class CUI_OT_SELECT_ICON(bpy.types.Operator):
    bl_idname = "cui.select_icon"
    bl_label = "Select Icon"
    bl_description = "Shows you a selection of all blender icons"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    bl_property = "icon_search"
    
    icon_data_path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    prop_name: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"}, default="icon")
    icon_search: bpy.props.StringProperty(name="Search", options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self, width=800)

    def draw(self,context):
        layout = self.layout
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items

        has_error = False        
        try:
            data = eval(self.icon_data_path)
        except:
            print('Error: icon_data_path is not correct')
            has_error = True
        if not has_error:
            prop = getattr(data, self.prop_name)

            row = layout.row()
            row.prop(self,"icon_search",text="",icon="VIEWZOOM")

            grid = layout.grid_flow(align=True,even_columns=True, even_rows=True)
            for icon in icons:
                # NOTE filtering out icon 806 because it throws an error for some reason
                if icon.value != 806 and (self.icon_search.lower() in icon.name.lower() or not self.icon_search):
                    op = grid.operator("cui.set_icon",text="", icon_value=icon.value, emboss=prop==icon.value)
                    op.icon_data_path = self.icon_data_path
                    op.prop_name = self.prop_name
                    op.icon = icon.value

def get_path_prop_idx(full_path):
    full_path = full_path.strip()
    path, prop, idx = None, None, None
    if full_path.endswith("]"):
        if full_path.endswith("']") or full_path.endswith('"]'):
            path_list = full_path.split('[')
            prop = "[" + path_list.pop(-1).replace(']', '') + "]"
            path = '['.join(path_list)
        else:
            path_list = full_path.split('[')
            idx = int(path_list.pop(-1).replace(']', ''))
            full_path = '['.join(path_list)
            if full_path.endswith("]"):
                prop = "[" + path_list.pop(-1).replace(']', '') + "]"
                path = '['.join(path_list)
            else:
                path_list = full_path.split('.')
                prop = path_list.pop(-1)
                path = '.'.join(path_list)
    else:
        path_list = full_path.split('.')
        prop = path_list.pop(-1)
        path = '.'.join(path_list)
    return (path, prop, idx)

def get_path_type(data_path):
    path_tuple = get_path_prop_idx(data_path)
    if path_tuple is not None and path_tuple[0] is not None and path_tuple[1] is not None:
        (path, prop_name, idx) = path_tuple
        if idx is not None or prop_name.find('[') >= 0:
            try:
                value = eval(data_path)
                return (type(value).__name__).upper()
            except: pass
        else:
            try:
                data = eval(path)
                if prop_name in data.bl_rna.properties.keys():
                    return data.bl_rna.properties[prop_name].type
            except: pass
    return None


def get_bones(context, selected):
    armature = context.object.data
    if context.mode == 'EDIT_ARMATURE':
        if selected:
            bones = [b for b in armature.edit_bones if b.select is True]
        else:
            bones = armature.edit_bones
    elif context.mode == 'OBJECT':
        if selected:
            bones = []
        else:
            bones = armature.bones
    elif context.mode == 'POSE':
        if selected:
            bones = [pbone.bone for pbone in context.selected_pose_bones_from_active_object]
        else:
            bones = armature.bones
    return bones

def is_used_layer(context, layer_index):
    bones = get_bones(context, False)
    is_use = 0
    for bone in bones:
        if bone.layers[layer_index]:
            is_use = 1
            break
    return is_use

def is_active_layer(context, layer_index):
    armature = context.object.data
    if context.mode == 'EDIT_ARMATURE':
        bone = context.active_bone
    elif context.mode == 'OBJECT':
        bone = armature.bones.active
    elif context.mode == 'POSE':
        bone = armature.bones.active
    is_active = 0
    if bone is not None and bone.layers[layer_index]:
        is_active = 2
    return is_active

pre_code_list = []
class_code_list = []
post_code_list = []

group_classes = []
register_props = []
operator_classes = []
panel_classes = []

def reset_global_code_lists():
    global pre_code_list, class_code_list, post_code_list
    pre_code_list = []
    class_code_list = []
    post_code_list = []

    global group_classes, register_props, operator_classes, panel_classes
    group_classes = []
    register_props = []
    operator_classes = []
    panel_classes = []

def generate_code():
    def get_footer_code():
        def get_class_code(name, class_list):
            code = ''
            if len(class_list) > 0:
                code = f"{name} = (\n"
                for cls in class_list:
                    code += f"    {cls},\n"
                code += ")\n"
            return code

        def get_class_loop(name, class_list, is_unregister=False):
            code = ''
            if len(class_list) > 0:
                if not is_unregister:
                    code = f"for cls in {name}:\n"
                    code += f"    try: register_class(cls)\n"
                else:
                    code = f"for cls in reversed({name}):\n"
                    code += f"    try: unregister_class(cls)\n"
                code += f"    except:pass\n"
            return code
        
        def get_prop_code():
            global register_props
            reg_code = ''
            unreg_code = ''
            for idx, prop_tuple in enumerate(register_props):
                (reg, unreg) = prop_tuple
                reg_code += f"try: {reg}\n"
                reg_code += f"except: need_unregister[{idx}] = False\n"

                unreg_code += f"if need_unregister[{idx}]: {unreg}\n"
            return (reg_code, unreg_code)

        global register_props
        global group_classes, operator_classes, panel_classes
        g_name, g_class_list = 'group_classes', group_classes
        o_name, o_class_list = 'operator_classes', operator_classes
        p_name, p_class_list = 'panel_classes', panel_classes

        before_reg = f"need_unregister = [True] * {len(register_props)}\n"
        before_reg += get_class_code(g_name, g_class_list)
        before_reg += get_class_code(o_name, o_class_list)
        before_reg += get_class_code(p_name, p_class_list)

        (prop_reg_code, prop_unreg_code) = get_prop_code()

        reg_code = "def register():\n"
        reg_code += f"from bpy.utils import register_class\n"
        reg_code += get_class_loop(g_name, g_class_list, False)
        reg_code += prop_reg_code
        reg_code += get_class_loop(o_name, o_class_list, False)
        reg_code += get_class_loop(p_name, p_class_list, False)
        reg_code = reg_code.replace('\n', '\n    ') + '\n'

        unreg_code = "def unregister():\n"
        unreg_code += f"from bpy.utils import unregister_class\n"
        unreg_code += get_class_loop(p_name, p_class_list, True)
        unreg_code += get_class_loop(o_name, o_class_list, True)
        unreg_code += prop_unreg_code
        unreg_code += get_class_loop(g_name, g_class_list, True)
        unreg_code = unreg_code.replace('\n', '\n    ') + '\n'

        footer_code = before_reg + reg_code + unreg_code + 'register()\n'
        return footer_code

    global pre_code_list, class_code_list, post_code_list
    header_code = 'import bpy\n'
    main_code = str('\n'.join(pre_code_list + class_code_list + post_code_list))
    return header_code + main_code + get_footer_code()

def append_panel(name, type, parent, order, draw_code, poll_code):
    panel_name = (type.replace(' ', '_').upper() + '_PT_' + name.replace(' ', '_').upper())
    parent_id = (f"bl_parent_id = '{parent}'" if parent != '' else '')
    poll_code = poll_code.replace('\n', '\n        ')
    draw_code = draw_code.replace('\n', '\n        ')

    panel_code = f'''
class {panel_name}(bpy.types.Panel):
    bl_label = '{name}'
    bl_idname = '{panel_name}'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = {order}
    {parent_id}
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        poll = True
        {poll_code}
        return poll

    def draw_header(self, context):
        layout = self.layout.column()

    def draw(self, context):
        layout = self.layout
        {draw_code}
'''
    global class_code_list, panel_classes
    class_code_list.append(panel_code)
    panel_classes.append(panel_name)

def get_operator(oper_name, oper_class, oper_id, oper_disc, oper_keys, oper_code):
    oper_code = oper_code.replace('\n', '\n        ')
    init_code = ''
    invoke_code = ''
    for key in oper_keys:
        key_found = None
        if key.lower().find('shift') >= 0:
            key_found = 'shift'
        elif key.lower().find('alt') >= 0:
            key_found = 'alt'
        elif key.lower().find('ctrl') >= 0:
            key_found = 'ctrl'
        elif key.lower().find('oskey') >= 0:
            key_found = 'oskey'
        if key_found is not None:
            init_code += f"self.{key_found} = False\n"
            invoke_code += f"self.{key_found} = event.{key_found}\n"
    invoke_code = invoke_code.replace('\n', '\n        ')
    if init_code != '':
        init_code = init_code.replace('\n', '\n        ')
        init_code = f'''
    def __init__(self):
        {init_code}'''

    return f'''
class {oper_class}(bpy.types.Operator):
    bl_idname = "{oper_id}"
    bl_label = "{oper_name}"
    bl_description = "{oper_disc}"
    bl_options = {{"REGISTER", "UNDO"}}

    @classmethod
    def poll(cls, context):
        return True
    {init_code}
    def invoke(self, context, event):
        {invoke_code}return self.execute(context)

    def execute(self, context):
        {oper_code}
        return {{"FINISHED"}}

'''



# TODO : cui_lyr_header
def cui_lyr_header(armature, layout, is_collect=False):
    if is_collect:
        common_code = f"layout = layout.column()\n"
        common_code += f"armature = bpy.context.object.data"
        parent_code = '''
is_pose = False
bone = None
if (bpy.context.mode=='EDIT_ARMATURE' and (armature.edit_bones.active != None)):
    bone = armature.edit_bones.active
elif (bpy.context.mode=='POSE' and (bpy.context.active_pose_bone != None)):
    bone = bpy.context.active_pose_bone
    is_pose = True
row = layout.row(align=True)
if bone is not None:
    row.enabled = (bone.parent != None)
    if (bone.parent != None):
        select_bone = (bone.parent.bone if is_pose else bone.parent)
        row.prop(select_bone, 'select', text='Parent : ' + (bone.parent.name if (bone.parent != None) else 'NONE'), icon_value=256, emboss=True, toggle=True)
    else:
        row.operator('cui.dummy_button_operator', text='Parent : ' + (bone.parent.name if (bone.parent != None) else 'NONE'), icon_value=256, emboss=True, depress=False)
else:
    row.enabled = False
    row.operator('cui.dummy_button_operator', text='No Bone Selected', icon_value=0, emboss=True, depress=False)
'''
        motion_code = '''
if bpy.context.mode=='POSE' and bpy.context.active_pose_bone != None:
    row = layout.row(align=True)
    row.operator('pose.paths_calculate', text='Motion Path', icon_value=433, emboss=True, depress=False)
    row2 = row.row(align=True)
    row2.scale_x = 0.72
    op = row2.operator('pose.paths_clear', text='Clear', icon_value=0, emboss=True, depress=False)
    op.only_selected = True
'''
        view_code = '''
row = layout.row(align=True)
row.prop(bpy.context.object, 'show_in_front', text='Front', icon_value=0, emboss=True, toggle=True)
row.prop(armature, 'show_names', text='Names', icon_value=0, emboss=True, toggle=True)
row.prop(armature, 'show_axes', text='Axes', icon_value=0, emboss=True, toggle=True)
'''
        use_parent = armature.cui_prop_use_parent_buttons
        use_motion = armature.cui_prop_use_display_buttons
        use_view = armature.cui_prop_use_view_buttons
        header_code = (parent_code if use_parent else '') + (motion_code if use_motion else '') + (view_code if use_view else '')
        if header_code != '':
            header_code = common_code + header_code
        return header_code

    else:
        layout = layout.column()

        # if armature.cui_prop_edit_mode or armature.cui_prop_use_parent_buttons:
        #     is_pose = False
        #     bone = None
        #     if (bpy.context.mode=='EDIT_ARMATURE' and (armature.edit_bones.active != None)):
        #         bone = armature.edit_bones.active
        #     elif (bpy.context.mode=='POSE' and (bpy.context.active_pose_bone != None)):
        #         bone = bpy.context.active_pose_bone
        #         is_pose = True
        #     row = layout.row(align=True)
        #     if armature.cui_prop_edit_mode:
        #         row.prop(armature, 'cui_prop_use_parent_buttons', text='', icon_value=0, emboss=True)
        #         row = row.row()
        #         row.active = armature.cui_prop_use_parent_buttons
        #     if bone is not None:
        #         row.enabled = (bone.parent != None)
        #         if (bone.parent != None):
        #             select_bone = (bone.parent.bone if is_pose else bone.parent)
        #             row.prop(select_bone, 'select', text=(bone.parent.name if (bone.parent != None) else 'NONE'), icon_value=904, emboss=True, toggle=True)
        #         else:
        #             row.operator('cui.dummy_button_operator', text=(bone.parent.name if (bone.parent != None) else 'NONE'), icon_value=904, emboss=True, depress=False)
        #     else:
        #         row.enabled = False
        #         row.operator('cui.dummy_button_operator', text='No Bone Selected', icon_value=0, emboss=True, depress=False)

# EDIT_MESH
# EDIT_CURVE
# EDIT_CURVES
# EDIT_SURFACE
# EDIT_TEXT
# EDIT_ARMATURE
# EDIT_METABALL
# EDIT_LATTICE
# POSE
# SCULPT
# PAINT_WEIGHT
# PAINT_VERTEX
# PAINT_TEXTURE
# PARTICLE
# OBJECT
# PAINT_GPENCIL
# EDIT_GPENCIL
# SCULPT_GPENCIL
# WEIGHT_GPENCIL
# VERTEX_GPENCIL
# SCULPT_CURVES
        if armature.cui_prop_edit_mode or armature.cui_prop_use_parent_buttons:
            if bpy.context.mode == 'EDIT_ARMATURE' or bpy.context.mode == 'POSE':
                row = layout.row(align=True)
                if armature.cui_prop_edit_mode:
                    row.prop(armature, 'cui_prop_use_parent_buttons', text='', icon_value=0, emboss=True)
                    row = row.row(align=True)
                    row.active = armature.cui_prop_use_parent_buttons
                active = armature.edit_bones.active if bpy.context.mode == 'EDIT_ARMATURE' else armature.bones.active
                if active != None:
                    # Display Parent
                    if active.parent != None:
                        row.prop(active.parent, 'select', text=active.parent.name, icon_value=904, emboss=True, toggle=True)
                    else:
                        row2 = row.row(align=True)
                        row2.enabled = False
                        row2.operator('cui.dummy_button_operator', text='NONE', icon_value=904, emboss=True, depress=False)
                    # Display Children
                    if len(active.children) > 1:
                        op = row.operator('cui.children_selection', text=(str(len(active.children)) + ' Children'), icon_value=891, emboss=True, depress=False)
                    elif len(active.children) == 1:
                        row.prop(active.children[0], 'select', text=active.children[0].name, icon_value=891, emboss=True, toggle=True)
                    else:
                        row2 = row.row(align=True)
                        row2.enabled = False
                        row2.operator('cui.dummy_button_operator', text='NONE', icon_value=891, emboss=True, depress=False)
                else:
                    row.enabled = False
                    row.operator('cui.dummy_button_operator', text='No Bone Selected', icon_value=0, emboss=True, depress=False)

        if armature.cui_prop_edit_mode or armature.cui_prop_use_parent_buttons:
            row = layout.row(align=True)
            if armature.cui_prop_edit_mode:
                row.prop(armature, 'cui_prop_use_display_buttons', text='', icon_value=0, emboss=True)
                row = row.row(align=True)
                row.active = armature.cui_prop_use_display_buttons
            row2 = row.row(align=True)
            row2.scale_x = 1.51
            row2.prop(armature, 'display_type', text='', icon_value=0, emboss=True, toggle=True)
            row2 = row.row(align=True)
            row2.prop(armature, 'show_bone_custom_shapes', text='Shapes', icon_value=0, emboss=True, toggle=True, invert_checkbox=True)
            row2.prop(armature, 'show_group_colors', text='', icon_value=252, emboss=True, toggle=True, invert_checkbox=True)
        

        if armature.cui_prop_edit_mode or armature.cui_prop_use_parent_buttons:
            row = layout.row(align=True)
            if armature.cui_prop_edit_mode:
                row.prop(armature, 'cui_prop_use_view_buttons', text='', icon_value=0, emboss=True)
                row = row.row(align=True)
                row.active = armature.cui_prop_use_view_buttons
            row.prop(armature, 'show_names', text='Names', icon_value=0, emboss=True, toggle=True)
            row.prop(armature, 'show_axes', text='Axes', icon_value=0, emboss=True, toggle=True)
            row.prop(bpy.context.object, 'show_in_front', text='Front', icon_value=0, emboss=True, toggle=True)
        return ''

class CUI_OT_CHILDREN_SELECTION(bpy.types.Operator):
    """"""
    bl_idname = "cui.children_selection"
    bl_label = "Children Selection"
    bl_description = "Display List of children and their selection"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.label(text='Children Selection')
        col = layout.column()
        if bpy.context.mode == 'EDIT_ARMATURE' or bpy.context.mode == 'POSE':
            active = bpy.context.object.data.edit_bones.active if bpy.context.mode == 'EDIT_ARMATURE' else bpy.context.object.data.bones.active
            if len(active.children) > 0:
                for child in active.children:
                    col.prop(child, 'select', text=child.name, icon_value=891, emboss=True, toggle=True)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_popup(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        return {'FINISHED'}

# TODO : Settings
class CUI_OT_CUI_SETTINGS(bpy.types.Operator):
    """"""
    bl_idname = "cui.settings"
    bl_label = "CUI Settings"
    bl_description = "CUI editor settings"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.label(text='Settings')
        col = layout.column()
        col.prop(context.object, 'cui_prop_let_inheritance', text='Let Inheritance', icon_value=0, emboss=True)
        col.prop(context.object, 'cui_prop_show_inherited', text='Show Inherited', icon_value=0, emboss=True)
        row = col.row(align=True)
        row.active = context.object.cui_prop_show_inherited
        row.prop(context.object, 'cui_prop_show_inherited_as_drop_down', text='Show Inherited As Drop Down', icon_value=0, emboss=True)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_popup(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        return {'FINISHED'}

# TODO : is_error_in_path
def is_error_in_path(path, use_bool = True):
    if path != '':
        path_type = get_path_type(path)
        if path_type is not None:
            if use_bool or (path_type == 'BOOL' or path_type == 'BOOLEAN'):
                return (False, '')
            else:
                return (True, f"Error : '{path_type}' is not supported")
        else:
            try:
                exec(path)
            except Exception as e:
                return (True, 'Error : ' + str(e))
    else:
        return (True, 'Error : path is empty')
    return (True, 'Error : unknown')

def processed_name(name, is_upper=False):
    new_name = ''.join(e for e in name if e.isalnum() or e == ' ' or e == '_').strip().replace(' ', '_')
    if is_upper:
        return new_name
    else:
        return new_name.casefold()

# oper_name: bpy.props.StringProperty(name='Operator Name', description='', default='', subtype='NONE', maxlen=0, update=cui_update_oper_custom)
# oper_disc: bpy.props.StringProperty(name='Operator Discription', description='', default='', subtype='NONE', maxlen=0, update=cui_update_oper_custom)
# oper_code: bpy.props.StringProperty(name='Operator Code', description='', default='', subtype='NONE', maxlen=0, update=cui_update_oper_custom)
# oper_id: bpy.props.StringProperty(name='Operator ID', description='', default='', subtype='NONE', maxlen=0)
# oper_keys: bpy.props.EnumProperty(name='Layer Template', description='', options={'ENUM_FLAG'}, items=[
#     ('SHIFT', 'self.shift', 'this is my work', 0, 1),
#     ('CTRL', 'self.ctrl', '', 0, 2),
#     ('ALT', 'self.alt', '', 0, 4),
# ], update=cui_update_oper_custom)

def custom_operator(button, cui_id, is_collect):
    if button.oper_id != '':
        try: exec(f"bpy.utils.unregister_class(bpy.ops.{button.oper_class})")
        except: pass

    oper_id = f"cui.{processed_name(button.oper_name)}_{cui_id.lower()}"
    oper_class = f"CUI_OT_{processed_name(button.oper_name).upper()}_{cui_id}"

    oper_code = get_operator(button.oper_name, oper_class, oper_id, button.oper_disc, button.oper_keys, button.oper_code)
    oper_code += f"bpy.utils.register_class({oper_class})\n"
    full_code = oper_code
    if not is_collect:
        try:
            exec(full_code)
            button.oper_id = oper_id
            button.oper_class = oper_class
            button.error = ''
        except Exception as e:
            button.error = str(e)
            button.oper_id = ''
            button.oper_class = ''
            print(full_code)
            print('Error :', e)
    else:
        print(full_code)
    return (oper_id)

# def add_indent(s):
#     raw_str = repr(s)[1:-1]
#     print(raw_str)
#     raw_str = raw_str.replace(r'\n', r'    \n')
#     print(raw_str)
#     new_string = raw_str.decode('unicode_escape')
#     return new_string

def get_fn_from_code(fn_name, prop_name, fn_code, item='item'):
    fn_code = fn_code.replace('#end#', '    \n')
    return f'''
def {fn_name}(self, context):
    {item} = self.{prop_name}
    {fn_code}

'''
# TODO bool
def custom_bool_property(button, cui_id, is_collect):
    if button.bool_id != '':
        try: exec(f"del bpy.types.Scene.{button.bool_id}")
        except: pass

    prop_name = f"cui_{processed_name(button.bool_name)}_{cui_id}"
    update_fn_name = f"cui_update_{prop_name}"

    prop_code = f"bpy.types.Scene.{prop_name} = bpy.props.BoolProperty(name='{button.bool_name}', description='{button.bool_disc}', options={{'ANIMATABLE'}}, default={button.bool_default}, update={update_fn_name})"
    pre_code = get_fn_from_code(update_fn_name, prop_name, button.bool_update_code, 'value')
    full_code = pre_code + prop_code
    if not is_collect:
        try:
            exec(full_code)
            button.bool_id = prop_name
            button.error = ''
        except Exception as e:
            button.error = str(e)
            button.bool_id = ''
            print(full_code)
            print('Error :', e)
    else:
        print(full_code)
    return (prop_name)

def custom_enum_property(button, cui_id, is_collect):
    if button.enum_id != '':
        try: exec(f"del bpy.types.Scene.{button.enum_id}")
        except: pass

    def get_enum_items():
        item_list = [item.name for item in button.enum_items]
        return str([(name, name, '', 0, idx) for idx, name in enumerate(item_list)])

    prop_name = f"cui_{processed_name(button.enum_name)}_{cui_id}"
    items_fn_name = f"{prop_name}_enum_items"
    update_fn_name = f"cui_update_{prop_name}"
    items = (get_enum_items() if not button.use_dynamic_items else items_fn_name)
    prop_code = f"bpy.types.Scene.{prop_name} = bpy.props.EnumProperty(name='{button.enum_name}', description='{button.enum_disc}', options={{'ANIMATABLE'}}, update={update_fn_name}, items={items})"
    pre_code = get_fn_from_code(update_fn_name, prop_name, button.enum_update_code)
    if button.use_dynamic_items:
        pre_code += get_fn_from_code(items_fn_name, prop_name, button.item_list_code)
    full_code = pre_code + prop_code
    if not is_collect:
        try:
            exec(full_code)
            button.enum_id = prop_name
            button.error = ''
        except Exception as e:
            button.error = str(e)
            button.enum_id = ''
            print(full_code)
            print('Error :', e)
    else:
        print(full_code)
    return (prop_name)


# TODO : cui_lyr_editor
def cui_lyr_editor(armature, mode, layout, is_collect=False, use_select_add=False, postfix=''):
    pre_code = ''
    if is_collect and use_select_add:
        pre_code += f'''
def get_bones(context, selected):
    armature = context.object.data
    if context.mode == 'EDIT_ARMATURE':
        if selected:
            bones = [b for b in armature.edit_bones if b.select is True]
        else:
            bones = armature.edit_bones
    elif context.mode == 'OBJECT':
        if selected:
            bones = []
        else:
            bones = armature.bones
    elif context.mode == 'POSE':
        if selected:
            bones = [pbone.bone for pbone in context.selected_pose_bones_from_active_object]
        else:
            bones = armature.bones
    return bones

def is_used_layer(context, layer_index):
    bones = get_bones(context, False)
    is_use = 0
    for bone in bones:
        if bone.layers[layer_index]:
            is_use = 1
            break
    return is_use

def is_active_layer(context, layer_index):
    armature = context.object.data
    if context.mode == 'EDIT_ARMATURE':
        bone = context.active_bone
    elif context.mode == 'OBJECT':
        bone = armature.bones.active
    elif context.mode == 'POSE':
        bone = armature.bones.active
    is_active = 0
    if bone is not None and bone.layers[layer_index]:
        is_active = 2
    return is_active

def add_select_buttons(row, layer_index):
    if bpy.context.scene.cui_prop_add_mode{postfix}:
        is_active = is_active_layer(bpy.context, layer_index)
        icon_idx = is_active
        if not is_active:
            is_used = is_used_layer(bpy.context, layer_index)
            icon_idx = is_used
        op = row.operator('cui.add_to_layer', text='', icon_value=(101, 643, 644)[icon_idx], emboss=True, depress=False)
        op.index = layer_index
    if bpy.context.scene.cui_prop_select_mode{postfix}:
        op = row.operator('cui.select_layer_bones', text='', icon_value=256, emboss=True, depress=False)
        op.index = layer_index

'''
    code = ''
    if is_collect:
        code += f"armature = bpy.context.active_object.data\n"
    col_collection = armature.cui_prop_col_collection
    is_edit_mode = (armature.cui_prop_edit_mode if not is_collect else False)
    is_edit_mode = (is_edit_mode if bpy.context.object.data == armature else False)
    if not is_collect:
        row_main = layout.row(align=True)
        col_main = row_main.column()
        col_main = col_main.column(align=True)
    first_name = ''
    if len(col_collection) > 0:
        first = col_collection[0]
        first_name = (first.header.strip() if first.split else '')
    c_col_main = 'layout'
    if first_name != '':
        if not is_collect:
            col_main.label(text=first_name + ' :')
        else:
            c_col_main = 'col_main'
            code += f"{c_col_main} = layout.column(align=True)\n"
            code += f"{c_col_main}.label(text=\'{first_name + ' :'}\')\n"
    c_col = 'col'
    if c_col_main == 'layout':
        c_col_main = 'col_main'
        code += f"{c_col_main} = layout.column(align=True)\n"

    if is_edit_mode or armature.cui_prop_use_box:
        if not is_collect:
            box = col_main.box()
            col = box.column()
        else:
            code += f"box = {c_col_main}.box()\n"
            code += f"{c_col} = box.column()\n"
    else:
        if not is_collect:
            col = col_main.column()
        else:
            code += f"{c_col} = {c_col_main}.column()\n"
    for col_idx in range(len(col_collection)):
        col_item = col_collection[col_idx]
        if col_item.split and col_idx != 0:
            if col_item.split_box and armature.cui_prop_use_box:
                if col_item.header != '':
                    if not is_collect:
                        col_main.separator(factor=1.0)
                        col_main.label(text=col_item.header + ' :')
                    else:
                        code += f"{c_col_main}.separator(factor=1.0)\n"
                        code += f"{c_col_main}.label(text=\'{col_item.header + ' :'}\')\n"
                else:
                    if not is_collect:
                        col_main.separator(factor=1.6)
                    else:
                        code += f"{c_col_main}.separator(factor=1.6)\n"
                if not is_collect:
                    box = col_main.box()
                    col = box.column()
                else:
                    code += f"box = {c_col_main}.box()\n"
                    code += f"{c_col} = box.column()\n"
            else:
                if not is_collect:
                    col.separator(factor=1.0)
                else:
                    code += f"{c_col}.separator(factor=1.0)\n"
                if col_item.header != '':
                    if not is_collect:
                        col.label(text=col_item.header + ' :')
                    else:
                        code += f"{c_col}.label(text=\'{col_item.header + ' :'}\')\n"

        row_collection = col_item.row_collection
        if not is_collect:
            row = col.row(align=True)
        else:
            c_row = 'row'
            code += f"{c_row} = {c_col}.row(align=True)\n"
        for row_idx in range(len(row_collection)):
            button = row_collection[row_idx]

            row_size = row.row(align=True)
            is_hide = False
            if button.hide:
                has_error = False
                try:
                    hide = eval(button.hide)
                except:
                    print('Error : hide condition is not correct, Button : ' + button.name)
                    has_error = True
                if not has_error:
                    is_hide = (hide if isinstance(hide, bool) else False)
            row_size.active = not is_hide

            if is_edit_mode:
                has_error = True
                if button.type == 'Layer':
                    has_error = False
                else:
                    (has_error, _) = is_error_in_path(button.path, False)

                op = row_size.operator('cui.set_button_active', text=button.name, icon_value=(button.icon if not has_error else 2), emboss=True, depress=((armature.cui_prop_active_col_index == col_idx) and (armature.cui_prop_active_row_index == row_idx)))
                op.mode = mode
                op.col_index = col_idx
                op.row_index = row_idx
            elif not is_hide:
                if button.type == 'Layer':
                    if not is_collect:
                        row.prop(armature, 'layers', index=button.layer_index, text=button.name, icon_value=button.icon, toggle=True)
                    else:
                        code += f"{c_row}.prop(armature, 'layers', index={button.layer_index}, text='{button.name}', icon_value={button.icon}, toggle=True)\n"
                else:
                    is_done = False
                    if button.path != '':
                        typ = get_path_type(button.path)
                        if typ == 'BOOL' or typ == 'BOOLEAN':
                            path_tuple = get_path_prop_idx(button.path)
                            if isinstance(path_tuple, tuple) and path_tuple[0] is not None and path_tuple[1] is not None and path_tuple[0] != '' and path_tuple[1] != '':
                                (path, prop, idx) = path_tuple
                                if not is_collect:
                                    index = (f', index={idx}' if idx is not None else '')
                                    path = path.replace("'", "\"")
                                    prop = prop.replace("'", "\"")
                                    code_prop = (f"row.prop({path}, '{prop}' {index}, text='{button.name}', icon_value={button.icon}, toggle=True)")
                                    try:
                                        exec(code_prop)
                                        is_done = True
                                    except: pass
                                else:
                                    index = (f", index={idx}" if idx is not None else '')
                                    code += f"try:\n"
                                    code += f"    {c_row}.prop({path}, '{prop}' {index}, text='{button.name}', icon_value={button.icon}, toggle=True)\n"
                                    code += f"except: pass\n"
                    if not is_collect and not is_done:
                        op = row.operator('cui.dummy_button_operator', text=button.name, icon_value=2, emboss=True)
            if button.type == 'Layer':
                if not is_collect:
                    if bpy.context.scene.cui_prop_add_mode:
                        is_active = is_active_layer(bpy.context, button.layer_index)
                        icon_idx = is_active
                        if not is_active:
                            is_used = is_used_layer(bpy.context, button.layer_index)
                            icon_idx = is_used
                        op = row.operator('cui.add_to_layer', text='', icon_value=(101, 643, 644)[icon_idx], emboss=True, depress=False)
                        op.index = button.layer_index
                    if bpy.context.scene.cui_prop_select_mode:
                        op = row.operator('cui.select_layer_bones', text='', icon_value=256, emboss=True, depress=False)
                        op.index = button.layer_index
                elif use_select_add:
                    code += f"add_select_buttons({c_row}, {button.layer_index})\n"
            if (int(len(row_collection.values()) - 1) > row_idx):
                if not armature.cui_prop_align_rows:
                    if not is_collect:
                        row.separator(factor=0.20)
                    else:
                        code += f"{c_row}.separator(factor=0.20)\n"
                else:
                    if not is_collect:
                        if bpy.context.scene.cui_prop_add_mode or bpy.context.scene.cui_prop_select_mode:
                            row.separator(factor=0.20)
                    else:
                        if use_select_add:
                            code += f"if bpy.context.scene.cui_prop_add_mode{postfix} or bpy.context.scene.cui_prop_select_mode{postfix}:\n"
                            code += f"    {c_row}.separator(factor=0.20)\n"
        if is_edit_mode:
            row.separator(factor=0.20)
            op = row.operator('cui.add_row_button', text='', icon_value=9, emboss=False, depress=False)
            op.mode = mode
            op.col_index = col_idx
    if is_edit_mode:
        length = len(col_collection)
        if length == 0:
            op = col.operator('cui.add_column_button', text='Add Button', icon_value=31, emboss=True, depress=False)
            op.mode = mode
        else:
            row = col.row(align=True)
            row.alignment = 'CENTER'
            op = row.operator('cui.add_column_button', text='', icon_value=9, emboss=False, depress=False)
            op.mode = mode
            row.label(text='', icon_value=101)
        if length < 4:
            col = col.column(align=True)
            col.scale_y = 4 - length
            col.label(text=' ')
    if is_edit_mode:
        row_main.separator(factor=1.0)
        col = row_main.column(align=True)
        op = col.operator('cui.remove_button', text='', icon_value=21, emboss=True, depress=False)
        op.mode = mode
        col.separator(factor=0.5)
        op = col.operator('cui.move_button', text='', icon_value=7, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Up'
        op = col.operator('cui.move_button', text='', icon_value=5, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Down'
        col.separator(factor=0.5)
        op = col.operator('cui.move_button', text='', icon_value=6, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Left'
        op = col.operator('cui.move_button', text='', icon_value=4, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Right'
    if is_collect:
        return (pre_code, code)

def get_lyr_poll():
    return '''object = bpy.context.object
if object is not None and object.type == 'ARMATURE':
    poll = True
else:
    poll = False'''

# TODO : cui_lyr_interface
def cui_lyr_interface(armature, layout, is_collect=False, use_select_add=False, postfix = ''):
    code = ''
    if bpy.context.object.data == armature:
        code += cui_lyr_header(armature, layout, is_collect)
        if not is_collect:
            layout.separator(factor=0.5)
            row = layout.row(align=True)
            row.scale_x = 1.10
            row.scale_y = 1.10
            row.alignment = 'RIGHT'
        else:
            if use_select_add:
                if code != '':
                    code += f"layout.separator(factor=0.5)\n"
                code += '''
row = layout.row(align=True)
row.scale_x = 1.10
row.scale_y = 1.10
row.alignment = 'RIGHT'
'''
        if not is_collect:
            if armature.cui_prop_edit_mode and len(armature.cui_prop_col_collection) > armature.cui_prop_active_col_index:
                column = armature.cui_prop_col_collection[armature.cui_prop_active_col_index]
                row.prop(column, 'split', text='', icon_value=590, emboss=True, toggle=True)
                row.separator(factor=0.4)
            row.prop(bpy.context.scene, 'cui_prop_add_mode', text='', icon_value=344, emboss=True)
            row.prop(bpy.context.scene, 'cui_prop_select_mode', text='', icon_value=256, emboss=True)
            row.separator(factor=0.2)
            row.prop(armature, 'cui_prop_align_rows', text='', icon_value=370, emboss=True)
            row.prop(armature, 'cui_prop_use_box', text='', icon_value=573, emboss=True)
        else:
            if use_select_add:
                code += f'''
row.prop(bpy.context.scene, 'cui_prop_add_mode{postfix}', text='', icon_value=344, emboss=True)
row.prop(bpy.context.scene, 'cui_prop_select_mode{postfix}', text='', icon_value=256, emboss=True)
'''
            else:
                if code != '':
                    code += f"layout.separator(factor=1.2)\n"
        header_code = code
        start_code = ''
        if not is_collect:
            layout.separator(factor=0.5)
        else:
            if use_select_add:
                start_code = f"layout.separator(factor=0.5)\n"
    code_tuple = cui_lyr_editor(armature, 'LAYER', layout, is_collect, use_select_add, postfix)
    if is_collect and code_tuple is not None:
        (pre_code, layer_code) = code_tuple
        layer_code = start_code + layer_code + start_code
        full_code = header_code + layer_code
        return (pre_code, full_code)


def get_layer_code(armature, parent_id):
    if armature is None:
        return ('', '', '')
    main_layout = get_layer_main_layout(armature)
    code = header + ('''
This is Layer Code
''')
    reg = '''
This is Layer Code
'''
    unreg = '''
This is Layer Code
'''
    return (code, reg, unreg)

def get_bone_code(parent_id):
    code = '''
This is Bone Code
'''
    reg = '''
This is Bone Code
'''
    unreg = '''
This is Bone Code
'''
    return (code, reg, unreg)

def get_object_code(parent_id):
    code = '''
This is Object Code
'''
    reg = '''
This is Object Code
'''
    unreg = '''
This is Object Code
'''
    return (code, reg, unreg)

def get_common_code():
    code = '''
# dummy
This is Common Code
'''
    reg = '''
This is Common Code
'''
    unreg = '''
This is Common Code
'''
    return (code, reg, unreg)

def get_full_code():
    armature = None
    if bpy.context.object is not None:
        armature = bpy.context.object.data
    parent_panel_code = append_panel('CUI Properties', 'CUI', '', 5, '')
    parent_id = f'CUI_PT_CUI_PROPERTIES'
    (common_code, common_reg, common_unreg) = get_common_code()
    (layer_code, layer_reg, layer_unreg) = get_layer_code(armature, parent_id)
    (bone_code, bone_reg, bone_unreg) = get_bone_code(parent_id)
    (object_code, object_reg, object_unreg) = get_object_code(parent_id)

    reg_code = (common_reg + layer_reg + bone_reg + object_reg).replace('\n', '\n   ')
    unreg_code = (object_unreg + bone_unreg + layer_unreg + common_unreg).replace('\n', '\n   ')
    return f'''
{parent_panel_code}

# Common Interface Code
{common_code}

# Layer Interface Code
{layer_code}

# Bone Properties Code
{bone_code}

# Object Properties Code
{object_code}

def register():
    try: bpy.utils.register_class({parent_id})
    except: pass
    {reg_code}

def unregister():
    {unreg_code}
    try: bpy.utils.unregister_class({parent_id})
    except: pass

register()
'''

import subprocess
def copy_to_clip(txt):
    cmd='echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)

class CUI_OT_COPY_LAYER_CODE(bpy.types.Operator):
    bl_idname = "cui.copy_layer_code"
    bl_label = "Copy Layer Code"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        def get_cui_code():
            global pre_code_list, register_props, class_code_list
            armature = context.object.data
            reset_global_code_lists()
            postfix = f"_{armature.cui_id}"
            code_tuple = cui_lyr_interface(armature, '', True, armature.cui_prop_use_select_add, postfix)
            (pre_code, layer_code) = code_tuple
            pre_code_list.append(pre_code)
            append_panel('Rig Interface', 'CUI', '', 4, layer_code, get_lyr_poll())

            select_mode = f"bpy.types.Scene.cui_prop_select_mode{postfix} = bpy.props.BoolProperty(name='Select Mode', description='', default=False)"
            add_mode = f"bpy.types.Scene.cui_prop_add_mode{postfix} = bpy.props.BoolProperty(name='Add Mode', description='', default=False)"
            register_props.append((select_mode, f"del bpy.types.Scene.cui_prop_select_mode{postfix}"))
            register_props.append((add_mode, f"del bpy.types.Scene.cui_prop_add_mode{postfix}"))

            oper_name = "CUI_OT_SELECT_LAYER_BONES"
            (pre_code, oper_code) = get_select_layer_bones()
            pre_code_list.append(pre_code)
            class_code_list.append(oper_code)
            register_props.insert(0, (f"bpy.utils.register_class({oper_name})", f"bpy.utils.unregister_class({oper_name})"))

            oper_name = "CUI_OT_ADD_TO_LAYER"
            (pre_code, oper_code) = get_add_to_layer()
            pre_code_list.append(pre_code)
            class_code_list.append(oper_code)
            register_props.insert(0, (f"bpy.utils.register_class({oper_name})", f"bpy.utils.unregister_class({oper_name})"))

            return generate_code()

        code = get_cui_code()
        if code is not None and code != '':
            print('<---------->')
            print(code)
            print('<---------->')
            copy_to_clip(code)
            self.report({'INFO'}, 'Copied')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# TODO : get_selection
def get_selection():
    def get_selected(text):
        select_text = ''
        if text is not None:
            fschar = text.current_character
            fsline = text.current_line_index
            fechar = text.select_end_character
            feline = text.select_end_line_index

            # The end and start lines and characters can be switched
            # depending on the direction in which the text was selected
            schar = min(fschar,fechar)
            echar = max(fschar,fechar)
            sline = min(fsline,feline)
            eline = max(fsline,feline)

            original_text = text.as_string()
            lines = original_text.split("\n")

            select_list = []
            for line in range(sline, eline + 1):
                cur_line = lines[line]
                
                start_char = 0
                end_char = len(cur_line)
                
                if line == sline:
                    start_char = schar
                    
                if line == eline:
                    end_char = echar
                
                # the selected part of this
                select = cur_line[start_char:end_char]
                if select != '':
                    select_list.append(cur_line)
            select_text = '\n'.join(select_list)
        return select_text
    editors = []
    txt = ''
    for area in bpy.context.screen.areas:
        if area.type == "TEXT_EDITOR":
            editors.append(area)
    if len(editors) > 0:
        main_editor = None
        main_area = 0
        for editor in editors:
            area = editor.height * editor.width
            if main_area < area:
                main_area = area
                main_editor = editor
        text = main_editor.spaces[0].text
        txt = get_selected(text)
        if txt == '':
            txt = text.as_string()
    return txt

class CUI_OT_Set_Selection(bpy.types.Operator):
    bl_idname = "cui.set_selection"
    bl_label = "Set Selection"
    bl_description = "set the selected text from active editor"
    bl_options = {"REGISTER", "UNDO"}

    prop: bpy.props.StringProperty(name='Property', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.prop != '':
            txt = get_selection()
            txt = txt.replace("\n", "#end#")
            code = f"{self.prop} = '''{txt}'''"
            try:
                exec(code)
            except Exception as e:
                print(code)
                print(e)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# FIXME : <---------
# >>> class Dispatch(object):
# ...     def funcA(self, *args):
# ...         print('funcA%r' % (args,))
# ...     def funcB(self, *args):
# ...         print('funcB%r' % (args,))
# ...     def __getitem__(self, name):
# ...         return getattr(self, name)
# ... 
# >>> d = Dispatch()
# >>> 
# >>> d['funcA'](1, 2, 3)
# funcA(1, 2, 3)

# use repr() and self.id_data

bone_g_class = "BoneLayoutGroup" # bone_layout_group
bone_group_list = []

def loop_buttons(col_collection, col, col_main, mode, parent, is_grouped, code, is_edit_mode, c_col, c_col_main, is_collect):
    is_scene_mode = (mode.upper() == 'SCENE')
    is_bone_mode = (mode.upper() == 'BONE')

    group_name = ''
    for col_idx in range(len(col_collection)):
        col_item = col_collection[col_idx]

        if not col_item.align:
            group_name = col_item.group.strip()

        if not is_grouped and col_idx != 0:
            if col_item.split:
                if col_item.split_box and parent.cui_prop_use_box:
                    if col_item.header != '':
                        if not is_collect:
                            col_main.separator(factor=1.0)
                            col_main.label(text=col_item.header + ' :')
                        else:
                            code += f"{c_col_main}.separator(factor=1.0)\n"
                            code += f"{c_col_main}.label(text=\'{col_item.header + ' :'}\')\n"
                    else:
                        if not is_collect:
                            col_main.separator(factor=1.6)
                        else:
                            code += f"{c_col_main}.separator(factor=1.6)\n"
                    if not is_collect:
                        box = col_main.box()
                        col = box.column(align=True)
                    else:
                        code += f"box = {c_col_main}.box()\n"
                        code += f"{c_col} = box.column(align=True)\n"
                else:
                    if col_item.header != '':
                        if not is_collect:
                            col.separator(factor=1.0)
                            col.label(text=col_item.header + ' :')
                        else:
                            code += f"{c_col}.separator(factor=1.0)"
                            code += f"{c_col}.label(text=\'{col_item.header + ' :'}\')\n"
                    else:
                        if not is_collect:
                            col.separator(factor=2.4)
                        else:
                            code += f"{c_col}.separator(factor=2.4)"
            elif not col_item.align and col_idx != 0:
                if not is_collect:
                    col.separator(factor=1.0)
                else:
                    code += f"{c_col}.separator(factor=1.0)"

        row_collection = col_item.row_collection
        row = col.row(align=True)
        group_list = []
        for row_idx in range(len(row_collection)):
            button = row_collection[row_idx]
            has_error = False
            row_size = row.row(align=True)
            row_size.enabled = (not is_grouped if is_edit_mode else True)
            row_size.scale_x = button.scale
            row_size.use_property_split = button.is_split
            is_button_grouped = False
            if button.type == 'Group':
                group_list.append((button.group_parent, button.group))
                is_button_grouped = True
            if is_edit_mode and not is_grouped:
                if button.type == "Property":
                    (has_error, _) = is_error_in_path(button.path_prop)
                elif button.type == "Operator":
                    (oper_name, _) = get_operator_data(button.path_oper)
                    has_error = not has_operator(oper_name)
                elif button.type.find('Custom') >= 0:
                    has_error = (button.error != '')
                btn_icon = button.icon
                if button.use_icon_code:
                    if is_edit_mode: btn_icon = 385
                    i = None
                    try:
                        i = eval(button.icon_code)
                    except: pass
                    if isinstance(i, int):
                        btn_icon = i
                op = row_size.operator('cui.set_button_active', text=button.name, icon_value=(btn_icon if not has_error else 2), emboss=True, depress=((parent.cui_prop_active_col_index == col_idx) and (parent.cui_prop_active_row_index == row_idx)))
                op.mode = mode
                op.col_index = col_idx
                op.row_index = row_idx
            else:
                btn_name = (button.name if button.use_name else '')
                if not is_button_grouped:
                    is_done = False
                    if button.type == 'Property':
                        if button.path_prop != '':
                            eval_value = None
                            try:
                                eval_value = eval(button.path_prop)
                            except: pass
                            if eval_value is not None:
                                emboss = (button.is_emboss if isinstance(eval_value, bool) else True)
                                path_tuple = get_path_prop_idx(button.path_prop)
                                # print(button.path, path_tuple)
                                if isinstance(path_tuple, tuple) and path_tuple[0] is not None and path_tuple[1] is not None and path_tuple[0] != '' and path_tuple[1] != '':
                                    (path, prop, idx) = path_tuple
                                    index = (f', index={idx}' if idx is not None else '')
                                    if button.label != '':
                                        row = row_size.row(align=True)
                                        row.scale_x = button.label_scale
                                        row.label(text=button.label)
                                    code_prop = (f'row_size.prop({path}, "{prop}" {index}, text="{btn_name}", icon_value={button.icon}, emboss={emboss}, expand={button.is_expand}, slider={button.is_slider}, toggle={button.is_toggle}, invert_checkbox={button.is_invert})')
                                    try:
                                        exec(code_prop)
                                        is_done = True
                                    except: pass
                    elif button.type == 'Operator':
                        if button.path_oper != '':
                            (oper_name, arg_list) = get_operator_data(button.path_oper)
                            if has_operator(oper_name):
                                op = row_size.operator(oper_name, text=btn_name, icon_value=button.icon)
                                if arg_list:
                                    for arg in arg_list:
                                        arg = arg.strip()
                                        if arg != '':
                                            try:
                                                exec(f"op.{arg}")
                                            except Exception as e:
                                                break
                                is_done = True
                    elif button.type == 'Bool Custom':
                        try:
                            if button.bool_id != '' and hasattr(bpy.context.scene, button.bool_id):
                                row_size.prop(bpy.context.scene, button.bool_id, text=btn_name, icon_value=button.icon, emboss=button.is_emboss, expand=button.is_expand, slider=button.is_slider, toggle=button.is_toggle, invert_checkbox=button.is_invert)
                                is_done = True
                        except: is_done = False
                    elif button.type == 'Enum Custom':
                        try:
                            if button.enum_id != '' and hasattr(bpy.context.scene, button.enum_id):
                                row_size.prop(bpy.context.scene, button.enum_id, text=btn_name, icon_value=button.icon, expand=button.is_expand, slider=button.is_slider, toggle=button.is_toggle, invert_checkbox=button.is_invert)
                                is_done = True
                        except: is_done = False
                    elif button.type == 'Operator Custom':
                        if button.oper_id != '' and has_operator(button.oper_id):
                            try:
                                op = row_size.operator(button.oper_id, text=btn_name, icon_value=button.icon, emboss=True)
                                is_done = True
                            except: is_done = False
                    if not is_done:
                        op = row_size.operator('cui.dummy_button_operator', text=button.name, icon_value=2, emboss=True)
        if is_edit_mode:
            row.separator(factor=0.20)
            if not is_grouped:
                op = row.operator('cui.add_row_button', text='', icon_value=9, emboss=False, depress=False)
                op.mode = mode
                op.col_index = col_idx
            else:
                row.label(icon_value=101)
        if group_list:
            for group in group_list:
                (group_parent, g_group) = group
                g_col_list = get_group_col(group_parent, g_group)
                if g_col_list:
                    is_cyclic = False
                    for g_col_item in g_col_list:
                        for row_item in g_col_item.row_collection:
                            if row_item.type == 'Group' and row_item.group_parent == parent.name and row_item.group == col_item.group:
                                is_cyclic = True
                                print(f'Warn : Cyclic group detected, in {parent.name} and {col_item.group}')
                                break
                    if not is_cyclic:
                        (col, col_main) = self.loop_buttons(g_col_list, col, col_main, mode, parent, True)
    return (col, col_main)


# TODO : cui_prop_editor
def cui_prop_editor2(mode, parent, code, layout, is_collect=False):
    if parent is None: return

    # mode = bpy.context.scene.cui_editor_mode
    # parent = get_parent(mode)
    is_scene_mode = (mode.upper() == 'SCENE')
    is_bone_mode = (mode.upper() == 'BONE')

    # code = ''
    # if is_collect:
    #     code += f"armature = bpy.context.active_object.data\n"

    col_collection = parent.cui_prop_col_collection
    is_edit_mode = (parent.cui_prop_edit_mode if not is_collect else False)
    if not is_collect:
        row_main = layout.row(align=True)
        col_main = row_main.column()
        col_main = col_main.column(align=True)
    first_name = ''
    if len(col_collection) > 0:
        first = col_collection[0]
        first_name = (first.header.strip() if first.split else '')
    c_col_main = 'layout'
    if first_name != '':
        if not is_collect:
            col_main.label(text=first_name + ' :')
        else:
            c_col_main = 'col_main'
            code += f"{c_col_main} = layout.column(align=True)\n"
            code += f"{c_col_main}.label(text=\'{first_name + ' :'}\')\n"
    c_col = 'col'
    if c_col_main == 'layout':
        c_col_main = 'col_main'
        code += f"{c_col_main} = layout.column(align=True)\n"
    if is_edit_mode or parent.cui_prop_use_box:
        if not is_collect:
            box = col_main.box()
            col = box.column(align=True)
        else:
            code += f"box = {c_col_main}.box()\n"
            code += f"{c_col} = box.column(align=True)\n"
    else:
        if not is_collect:
            col = col_main.column(align=True)
        else:
            code += f"{c_col} = {c_col_main}.column(align=True)\n"

    (col, col_main) = self.loop_buttons(col_collection, col, col_main, mode, parent, False, code, is_edit_mode, c_col, c_col_main, is_collect)
    if is_edit_mode:
        length = len(col_collection)
        if length == 0:
            op = col.operator('cui.add_column_button', text='Add Button', icon_value=31, emboss=True, depress=False)
            op.mode = mode
        else:
            col.separator(factor=0.4)
            row = col.row(align=True)
            row.alignment = 'CENTER'
            op = row.operator('cui.add_column_button', text='', icon_value=9, emboss=False, depress=False)
            op.mode = mode
            row.label(text='', icon_value=101)
        if length < 4:
            col = col.column(align=True)
            col.scale_y = 4 - length
            col.label(text=' ')
    if is_edit_mode:
        row_main.separator(factor=1.0)
        col = row_main.column(align=True)
        # if first_name != '':
        #     col.label(text='', icon_value=101)
        op = col.operator('cui.remove_button', text='', icon_value=21, emboss=True, depress=False)
        op.mode = mode
        col.separator(factor=0.5)
        op = col.operator('cui.move_button', text='', icon_value=7, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Up'
        op = col.operator('cui.move_button', text='', icon_value=5, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Down'
        col.separator(factor=0.5)
        op = col.operator('cui.move_button', text='', icon_value=6, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Left'
        op = col.operator('cui.move_button', text='', icon_value=4, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Right'




def get_operator_data(oper):
    oper_name, arg_list = '', []
    import re
    regex = "(?:bpy\.ops\.)?(.+)\((.*)\)$|(?:bpy\.ops\.)?(.+)$"
    match = re.search(regex, oper)
    if match is not None:
        if match.group(2) is not None:
            oper_name = match.group(1)
            arg_list = match.group(2).split(',')
        else:
            oper_name = match.group(3)
    return (oper_name, arg_list)

def has_operator(oper):
    value = False
    try:
        value = eval(f"hasattr(bpy.types, bpy.ops.{oper}.idname())")
    except: pass
    return value


class CUI_UL_DISPLAY_COLLECTION_ENUM_ITEMS(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index_27C2A):
        row = layout
        # layout.separator(factor=0.5)
        # layout.label(text=item.name, icon_value=0)
        layout.prop(item, 'name', text='', icon_value=0, emboss=False)

def get_parents(mode):
    parents = None
    if mode.upper() == 'BONE':
        if bpy.context.mode == 'POSE' and bpy.context.pose_object is not None and bpy.context.active_pose_bone is not None:
            parents = bpy.context.object.pose.bones
    elif mode.upper() == 'OBJECT':
        if bpy.context.object is not None:
            parents = bpy.context.scene.objects
    elif mode.upper() == 'SCENE':
        if bpy.context.scene is not None:
            parents = bpy.data.scenes
    return parents

def get_group_col(parent_name, group_name):
    group_col_list = []
    parents = get_parents('BONE')
    if parent_name in parents:
        parent = parents[parent_name]
        col_collection = parent.cui_prop_col_collection
        is_found = False
        for col_item in col_collection:
            if is_found and (col_item.split or not col_item.align):
                break
            if col_item.group == group_name:
                is_found = True
            if is_found:
                group_col_list.append(col_item)
    return group_col_list

def generate_id():
    import random
    def generate(id_list):
        id = str(random.randint(1010, 9989))
        if id in id_list:
            return generate(id_list)
        else:
            return id
    id_list = []
    parents = get_parents('BONE')
    if parents is not None:
        id_list = [parent.cui_id for parent in parents if parent.cui_id is not None and parent.cui_id != '']
    return generate(id_list)

class CUI_PT_EDITOR_PANEL(bpy.types.Panel):
    bl_label = 'CUI Editor'
    bl_idname = 'CUI_PT_EDITOR_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 2
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator('cui.dummy_button_operator', text='', icon_value=707, emboss=True, depress=False)
        row.operator('cui.settings', text='', icon_value=117, emboss=True, depress=False)
    
    # cui_prop_let_inheritance
    # cui_prop_show_inherited
    # cui_prop_show_inherited_as_drop_down

    # TODO : main draw
    def draw(self, context):
        layout = self.layout.column()
        if context.object is None:
            layout.label(text='No Object Selected', icon_value=1)
        elif context.object.cui_prop_show_inherited and len(get_inherit_list()) > 1:
                row = layout.row()
                row.scale_y = 1.1
                expand = not bpy.context.object.cui_prop_show_inherited_as_drop_down
                row.prop(bpy.context.object, 'cui_editor_object', text=(' ' if expand else ''), icon_value=0, emboss=True, expand=expand)

        # layout.separator(factor=0.5)
        # mode = context.scene.cui_editor_mode
        # mode_info = ''
        # if mode.upper() == 'LAYER':
        #     if context.object is not None and context.object.type == 'ARMATURE': pass
        #     else: mode_info = 'Select Armature to use "Layers"'
        # elif mode.upper() == 'BONE':
        #     if context.mode == 'POSE' and context.pose_object is not None and context.active_pose_bone is not None: pass
        #     else: mode_info = 'Select Pose Bone to use "Bone Properties"'
        # elif mode.upper() == 'OBJECT':
        #     if context.object is not None: pass
        #     else: mode_info = 'Select Object to use "Object Properties"'
        # elif mode.upper() == 'SCENE':
        #     if context.scene is not None: pass
        #     else: mode_info = 'Select Scene to use "Scene Properties"'

        # if mode_info == '':
        #     if mode.upper() == 'LAYER':
        #         self.cui_lyr_manager(layout)
        #     else:
        #         self.cui_prop_interface(layout)
        # else:
        #     layout.separator(factor=0.5)
        #     layout.label(text=mode_info, icon_value=110)




class CUI_PT_BONE_PANEL(bpy.types.Panel):
    bl_label = 'Bone Properties'
    bl_idname = 'CUI_PT_BONE_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 0
    bl_parent_id = 'CUI_PT_EDITOR_PANEL'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        if context.mode == 'POSE':
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout

    # TODO : draw
    def draw(self, context):
        layout = self.layout.column()
        is_editable = True
        cui_prop_interface((context.active_pose_bone, is_editable), 'BONE', layout)

class CUI_PT_LAYER_PANEL(bpy.types.Panel):
    bl_label = 'Layers'
    bl_idname = 'CUI_PT_LAYER_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 1
    bl_parent_id = 'CUI_PT_EDITOR_PANEL'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        obj = None
        obj_name = context.object.cui_editor_object
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
        if obj is not None and obj.type == 'ARMATURE':
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout

    # TODO : draw
    def draw(self, context):
        layout = self.layout.column()
        obj = bpy.data.objects[context.object.cui_editor_object]
        armature = obj.data
        cui_layer_manager(layout, armature)

class CUI_PT_OBJECT_PANEL(bpy.types.Panel):
    bl_label = 'Object Properties'
    bl_idname = 'CUI_PT_OBJECT_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 2
    bl_parent_id = 'CUI_PT_EDITOR_PANEL'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        obj = None
        obj_name = context.object.cui_editor_object
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
        if obj is not None:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout

    # TODO : draw
    def draw(self, context):
        layout = self.layout.column()
        obj = bpy.data.objects[context.object.cui_editor_object]
        is_editable = (context.object.name == obj.name)
        cui_prop_interface((obj, is_editable), 'OBJECT', layout)

class CUI_PT_SCENE_PANEL(bpy.types.Panel):
    bl_label = 'Scene Properties'
    bl_idname = 'CUI_PT_SCENE_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 3
    bl_parent_id = 'CUI_PT_EDITOR_PANEL'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        if context.scene is not None:
            return True
        else:
            return False

    def draw_header(self, context):
        layout = self.layout

    # TODO : draw
    def draw(self, context):
        layout = self.layout.column()
        cui_prop_interface((context.scene, True), 'SCENE', layout)


# TODO : cui_layer_manager
def cui_layer_manager(layout, armature):
    is_collect = False
    use_select_add = False
    if bpy.context.object.data == armature:
        row = layout.row(align=True)
        row.scale_x = 1.10
        row.scale_y = 1.10
        row.alignment = 'RIGHT'
        row.prop(armature, 'cui_prop_test_mode', text='', icon_value=181, emboss=True)
        row2 = row.row(align=True)
        row2.enabled = armature.cui_prop_test_mode
        row2.prop(armature, 'cui_prop_use_select_add', text='', icon_value=404, emboss=True)
        row.separator(factor=0.2)
        row.operator('cui.copy_layer_code', text='', icon_value=598, emboss=True, depress=False)
        row.prop(armature, 'cui_prop_edit_mode', text='', icon_value=197, emboss=True)

        is_collect = armature.cui_prop_test_mode
        use_select_add = armature.cui_prop_use_select_add

        if not is_collect and armature.cui_prop_edit_mode:
            layout.separator(factor=0.5)
            row = layout.row(align=True)
            row.prop(bpy.context.scene, 'cui_prop_template', text='', icon_value=0, emboss=True, expand=False)
            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.operator('cui.dummy_button_operator', text='Load', icon_value=0, emboss=True, depress=False)
            row.separator(factor=0.2)
            row.operator('cui.dummy_button_operator', text='', icon_value=69, emboss=True, depress=False)

        layout.separator(factor=0.5)
    code_tuple = cui_lyr_interface(armature, layout, is_collect, use_select_add)
    if bpy.context.object.data == armature:
        if code_tuple is not None:
            (pre_code, layer_code) = code_tuple
            full_code = pre_code + layer_code
            # print(full_code)
            exec(pre_code + full_code)
        if not is_collect:
            layout.separator(factor=0.5)
            if not armature.cui_prop_test_mode:
                cui_lyr_options(armature, layout)


# TODO : cui_lyr_options
def cui_lyr_options(armature, layout):
    col_collection = armature.cui_prop_col_collection
    active_col_index = armature.cui_prop_active_col_index
    if len(col_collection) == 0: return
    column = col_collection[active_col_index]
    row_collection = col_collection[active_col_index].row_collection
    active_row_index = armature.cui_prop_active_row_index
    button = row_collection[active_row_index]
    button_path = 'bpy.context.object.data.cui_prop_col_collection[bpy.context.object.data.cui_prop_active_col_index].row_collection[bpy.context.object.data.cui_prop_active_row_index]'

    def display_layers(layout):
        def layer_button(layout, index):
            op = layout.operator('cui.set_layer_index', text='', icon_value=0, emboss=True, depress=(index == button.layer_index))
            op.index = index

        col = layout.column(align=True)
        col.scale_y = 0.7
        row = col.row(align=True)
        for idx in range(8):
            layer_button(row, idx)
        row.separator(factor=1.0)
        for idx in range(8):
            layer_button(row, idx + 8)
        row = col.row(align=True)
        for idx in range(8):
            layer_button(row, idx + 16)
        row.separator(factor=1.0)
        for idx in range(8):
            layer_button(row, idx + 24)

    if armature.cui_prop_edit_mode:
        # layout.separator(factor=1.0)
        layout.use_property_split = True
        layout.use_property_decorate = False
        if column.split:
            row = layout.row(align=True)
            row.prop(column, 'header', text='Header', icon_value=0, emboss=True)
            row.prop(column, 'split_box', text='', icon_value=590, emboss=True)

        layout.prop(button, 'type', text='Type', icon_value=0, emboss=True)
        layout.prop(button, 'name', text='Name', icon_value=0, emboss=True)
        row = layout.row(align=True)
        row.prop(button, 'icon', text='Icon', icon_value=0, emboss=True)
        op = row.operator('cui.select_icon', text='Choose', icon_value=button.icon, emboss=True, depress=False)
        op.icon_data_path = button_path
        op.prop_name = 'icon'

        row = layout.row(align=True)
        row.prop(button, 'hide', text='Hide If', icon_value=0, emboss=True)

        if button.type == "Layer":
            box = layout.box()
            col = box.column(align=True)
            col.label(text='Layer :')
            display_layers(col)
        elif button.type == "Bool Path":
            (has_error, err) = is_error_in_path(button.path, False)
            box = layout.box()
            col = box.column(align=True)
            col.label(text='Full Path :')
            row = col.row()
            row.alert = has_error
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'path', text='', icon_value=0, emboss=True)
            if has_error:
                col.label(text=err, icon_value=3)


# TODO : cui_prop_interface
def cui_prop_interface(data, mode, layout):
    (parent, is_editable) = data
    if is_editable:
        row = layout.row(align=True)
        row.scale_x = 1.10
        row.scale_y = 1.10
        row.alignment = 'RIGHT'
        # row.prop(armature, 'cui_prop_test_mode', text='', icon_value=181, emboss=True)
        row.operator('cui.dummy_button_operator', text='', icon_value=181, emboss=True, depress=False)
        row.operator('cui.dummy_button_operator', text='', icon_value=598, emboss=True, depress=False)
        if mode == 'BONE' and bpy.context.object is not None:
            row.prop(bpy.context.object, 'cui_prop_edit_mode', text='', icon_value=197, emboss=True)
            is_edit_mode = (is_editable and bpy.context.object.cui_prop_edit_mode)
        else:
            row.prop(parent, 'cui_prop_edit_mode', text='', icon_value=197, emboss=True)
            is_edit_mode = (is_editable and parent.cui_prop_edit_mode)
        data = (parent, is_edit_mode)

        if is_edit_mode:
            layout.separator(factor=0.5)
            row = layout.row(align=True)
            row.prop(bpy.context.scene, 'cui_prop_template', text='', icon_value=0, emboss=True, expand=False)
            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.operator('cui.dummy_button_operator', text='Load', icon_value=0, emboss=True, depress=False)
            row.separator(factor=0.2)
            row.operator('cui.dummy_button_operator', text='', icon_value=69, emboss=True, depress=False)

        col_collection = parent.cui_prop_col_collection
        if is_edit_mode:
            layout.separator(factor=0.5)
            row = layout.row(align=True)
            row.scale_x = 1.10
            row.scale_y = 1.10

            row.alignment = 'RIGHT'
            global register_done_list
            if parent.cui_id != '' and (f"{mode}_{parent.cui_id}") not in register_done_list:
                if need_register_custom_buttons(mode):
                    row.operator('cui.register_custom_buttons', text='Register', icon_value=0, emboss=True, depress=True)
                    row.separator(factor=0.4)
            if len(col_collection) > 0 and len(col_collection) > parent.cui_prop_active_col_index:
                column = col_collection[parent.cui_prop_active_col_index]
                row.prop(column, 'split', text='', icon_value=590, emboss=True, toggle=True)
                row.prop(column, 'align', text='', icon_value=369, emboss=True, toggle=True)
            row.prop(parent, 'cui_prop_use_box', text='', icon_value=573, emboss=True)

        layout.separator(factor=0.5)
    cui_prop_editor(data, mode, layout)
    if is_editable:
        layout.separator(factor=0.5)
        cui_prop_options(data, mode, layout)


def loop_buttons(data, mode, is_edit_mode, col_collection, col, col_main, is_grouped):
    (parent, is_editable) = data
    for col_idx in range(len(col_collection)):
        col_item = col_collection[col_idx]
        
        if not is_grouped and col_idx != 0:
            if col_item.split:
                if col_item.split_box and parent.cui_prop_use_box:
                    if col_item.header != '':
                        col_main.separator(factor=1.0)
                        col_main.label(text=col_item.header + ' :')
                    else:
                        col_main.separator(factor=1.6)
                    box = col_main.box()
                    col = box.column(align=True)
                else:
                    if col_item.header != '':
                        col.separator(factor=1.0)
                        col.label(text=col_item.header + ' :')
                    else:
                        col.separator(factor=2.4)
            elif not col_item.align and col_idx != 0:
                col.separator(factor=1.0)

        row_collection = col_item.row_collection
        row = col.row(align=True)
        group_list = []
        for row_idx in range(len(row_collection)):
            button = row_collection[row_idx]
            has_error = False

            row_size = row.row(align=True)
            row_size.enabled = (not is_grouped if is_edit_mode else True)
            row_size.scale_x = button.scale
            row_size.use_property_split = button.is_split
            is_button_grouped = False
            if button.type == 'Group':
                group_list.append((button.group_parent, button.group))
                is_button_grouped = True

            is_hide = False
            if button.hide:
                has_error = False
                try:
                    hide = eval(button.hide)
                except:
                    print('Error : hide condition is not correct, Button : ' + button.name)
                    has_error = True
                if not has_error:
                    is_hide = (hide if isinstance(hide, bool) else False)
            row_size.active = not is_hide
            if is_edit_mode and not is_grouped:
                if button.type == "Property":
                    (has_error, _) = is_error_in_path(button.path_prop)
                elif button.type == "Operator":
                    (oper_name, _) = get_operator_data(button.path_oper)
                    has_error = not has_operator(oper_name)
                elif button.type.find('Custom') >= 0:
                    has_error = (button.error != '')
                btn_icon = button.icon
                if button.use_icon_code:
                    if is_edit_mode: btn_icon = 385
                    i = None
                    try:
                        i = eval(button.icon_code)
                    except: pass
                    if isinstance(i, int):
                        btn_icon = i
                op = row_size.operator('cui.set_button_active', text=button.name, icon_value=(btn_icon if not has_error else 2), emboss=True, depress=((parent.cui_prop_active_col_index == col_idx) and (parent.cui_prop_active_row_index == row_idx)))
                op.mode = mode
                op.col_index = col_idx
                op.row_index = row_idx
            else:
                btn_name = (button.name if button.use_name else '')
                if not is_hide and not is_button_grouped:
                    is_done = False
                    if button.type == 'Property':
                        if button.path_prop != '':
                            eval_value = None
                            try:
                                eval_value = eval(button.path_prop)
                            except: pass
                            if eval_value is not None:
                                emboss = (button.is_emboss if isinstance(eval_value, bool) else True)
                                path_tuple = get_path_prop_idx(button.path_prop)
                                # print(button.path, path_tuple)
                                if isinstance(path_tuple, tuple) and path_tuple[0] is not None and path_tuple[1] is not None and path_tuple[0] != '' and path_tuple[1] != '':
                                    (path, prop, idx) = path_tuple
                                    index = (f', index={idx}' if idx is not None else '')
                                    if button.label != '':
                                        row = row_size.row(align=True)
                                        row.scale_x = button.label_scale
                                        row.label(text=button.label)
                                    path = path.replace("'", "\"")
                                    prop = prop.replace("'", "\"")
                                    code_prop = (f"row_size.prop({path}, '{prop}' {index}, text='{btn_name}', icon_value={button.icon}, emboss={emboss}, expand={button.is_expand}, slider={button.is_slider}, toggle={button.is_toggle}, invert_checkbox={button.is_invert})")
                                    try:
                                        exec(code_prop)
                                        is_done = True
                                    except: pass
                    elif button.type == 'Operator':
                        if button.path_oper != '':
                            (oper_name, arg_list) = get_operator_data(button.path_oper)
                            if has_operator(oper_name):
                                op = row_size.operator(oper_name, text=btn_name, icon_value=button.icon)
                                if arg_list:
                                    for arg in arg_list:
                                        arg = arg.strip()
                                        if arg != '':
                                            try:
                                                exec(f"op.{arg}")
                                            except Exception as e:
                                                break
                                is_done = True
                    elif button.type == 'Bool Custom':
                        try:
                            if button.bool_id != '' and hasattr(bpy.context.scene, button.bool_id):
                                row_size.prop(bpy.context.scene, button.bool_id, text=btn_name, icon_value=button.icon, emboss=button.is_emboss, expand=button.is_expand, slider=button.is_slider, toggle=button.is_toggle, invert_checkbox=button.is_invert)
                                is_done = True
                        except: is_done = False
                    elif button.type == 'Enum Custom':
                        try:
                            if button.enum_id != '' and hasattr(bpy.context.scene, button.enum_id):
                                row_size.prop(bpy.context.scene, button.enum_id, text=btn_name, icon_value=button.icon, expand=button.is_expand, slider=button.is_slider, toggle=button.is_toggle, invert_checkbox=button.is_invert)
                                is_done = True
                        except: is_done = False
                    elif button.type == 'Operator Custom':
                        if button.oper_id != '' and has_operator(button.oper_id):
                            try:
                                op = row_size.operator(button.oper_id, text=btn_name, icon_value=button.icon, emboss=True)
                                is_done = True
                            except: is_done = False
                    if not is_done:
                        op = row_size.operator('cui.dummy_button_operator', text=button.name, icon_value=2, emboss=True)
        if is_edit_mode:
            row.separator(factor=0.20)
            if not is_grouped:
                op = row.operator('cui.add_row_button', text='', icon_value=9, emboss=False, depress=False)
                op.mode = mode
                op.col_index = col_idx
            else:
                row.label(icon_value=101)
        if group_list and mode.upper() == 'BONE':
            for group in group_list:
                (group_parent, g_group) = group
                g_col_list = get_group_col(group_parent, g_group)
                if g_col_list:
                    is_cyclic = False
                    for g_col_item in g_col_list:
                        for row_item in g_col_item.row_collection:
                            if row_item.type == 'Group' and row_item.group_parent == parent.name and row_item.group == col_item.group:
                                is_cyclic = True
                                print(f'Warn : Cyclic group detected, in {parent.name} and {col_item.group}')
                                break
                    if not is_cyclic:
                        (col, col_main) = loop_buttons(data, mode, is_edit_mode, g_col_list, col, col_main, True)
    return (col, col_main)


# TODO : cui_prop_editor
def cui_prop_editor(data, mode, layout):
    (parent, is_edit_mode) = data
    col_collection = parent.cui_prop_col_collection
    row_main = layout.row(align=True)
    col_main = row_main.column()
    col_main = col_main.column(align=True)
    first_name = ''
    if len(col_collection) > 0:
        first = col_collection[0]
        first_name = (first.header.strip() if first.split else '')
    if first_name != '':
        row = col_main.row(align=True)
        row.label(text=first_name + ' :')
    if is_edit_mode or parent.cui_prop_use_box:
        box = col_main.box()
        col = box.column(align=True)
    else:
        col = col_main.column(align=True)

    (col, col_main) = loop_buttons(data, mode, is_edit_mode, col_collection, col, col_main, False)
    if is_edit_mode:
        length = len(col_collection)
        if length == 0:
            op = col.operator('cui.add_column_button', text='Add Button', icon_value=31, emboss=True, depress=False)
            op.mode = mode
        else:
            col.separator(factor=0.4)
            row = col.row(align=True)
            row.alignment = 'CENTER'
            op = row.operator('cui.add_column_button', text='', icon_value=9, emboss=False, depress=False)
            op.mode = mode
            row.label(text='', icon_value=101)
        if length < 4:
            col = col.column(align=True)
            col.scale_y = 4 - length
            col.label(text=' ')
    if is_edit_mode:
        row_main.separator(factor=1.0)
        col = row_main.column(align=True)
        # if first_name != '':
        #     col.label(text='', icon_value=101)
        op = col.operator('cui.remove_button', text='', icon_value=21, emboss=True, depress=False)
        op.mode = mode
        col.separator(factor=0.5)
        op = col.operator('cui.move_button', text='', icon_value=7, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Up'
        op = col.operator('cui.move_button', text='', icon_value=5, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Down'
        col.separator(factor=0.5)
        op = col.operator('cui.move_button', text='', icon_value=6, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Left'
        op = col.operator('cui.move_button', text='', icon_value=4, emboss=True, depress=False)
        op.mode = mode
        op.direction = 'Right'



# TODO : cui_prop_options
def cui_prop_options(data, mode, layout):
    (parent, is_edit_mode) = data
    if mode.upper() == 'BONE':
        parent_path = 'bpy.context.active_pose_bone'
    elif mode.upper() == 'OBJECT':
        parent_path = 'bpy.context.object'
    else:
        parent_path = 'bpy.context.scene'
    col_collection = parent.cui_prop_col_collection
    active_col_index = parent.cui_prop_active_col_index
    if len(col_collection) == 0: return
    column = col_collection[active_col_index]
    row_collection = col_collection[active_col_index].row_collection
    active_row_index = parent.cui_prop_active_row_index
    button = row_collection[active_row_index]
    button_path = f'{parent_path}.cui_prop_col_collection[{parent_path}.cui_prop_active_col_index].row_collection[{parent_path}.cui_prop_active_row_index]'
    # use repr() and self.id_data

    if is_edit_mode:
        # layout.separator(factor=1.0)
        layout.use_property_split = True
        layout.use_property_decorate = False
        if column.split:
            row = layout.row(align=True)
            row.prop(column, 'header', text='Header', icon_value=0, emboss=True)
            row.prop(column, 'split_box', text='', icon_value=590, emboss=True)

        if mode.upper() == 'BONE':
            row = layout.row(align=True)
            row.active = not column.align
            row.prop(column, 'group', text='Group', icon_value=0, emboss=True)

        layout.prop(button, 'type', text='Type', icon_value=0, emboss=True)
        row = layout.row(align=True)
        row.prop(button, 'name', text='Name', icon_value=0, emboss=True)
        row.separator(factor=0.2)
        row.prop(button, 'use_name', text='', icon_value=(254 if button.use_name else 253), emboss=False)
        layout.prop(button, 'scale', text='Scale', icon_value=0, emboss=True)

        if button.type != "Group":
            row = layout.row(align=True)
            if button.use_icon_code:
                row.prop(button, 'icon_code', text='Icon', icon_value=0, emboss=True)
            else:
                row.prop(button, 'icon', text='Icon', icon_value=0, emboss=True)
                op = row.operator('cui.select_icon', text='Choose', icon_value=button.icon, emboss=True, depress=False)
                op.icon_data_path = button_path
                op.prop_name = 'icon'
            row.separator(factor=0.2)
            row.prop(button, 'use_icon_code', text='', icon_value=(746 if not button.use_icon_code else 328), emboss=False, toggle=True)

            row = layout.row(align=True)
            row.prop(button, 'hide', text='Hide If', icon_value=0, emboss=True)

            layout.separator(factor=0.5)
            box = layout.box()
            col_box = box.column(align=True)

        show_interface_options = False
        is_bool = False
        if button.type == "Property":
            show_interface_options = True
            (has_error, err) = is_error_in_path(button.path_prop)
            col = col_box
            col.label(text='Full Path :')
            row = col.row()
            row.alert = has_error
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'path_prop', text='', icon_value=0, emboss=True)
            if has_error:
                col.label(text=err, icon_value=3)
            eval_value = None
            try:
                eval_value = eval(button.path_prop)
            except: pass
            if isinstance(eval_value, bool):
                is_bool = True

        elif button.type == "Operator":
            (oper_name, _) = get_operator_data(button.path_oper)
            has_error = not has_operator(oper_name)
            col = col_box
            col.label(text='Full Path :')
            row = col.row()
            row.alert = has_error
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'path_oper', text='', icon_value=0, emboss=True)
            if has_error:
                col.label(text="Error : Operator Not Exists", icon_value=3)
            if True:
                col.label(text="Unable to detect ERROR in args", icon_value=1)

        elif button.type == "Operator Custom":
            layout.separator(factor=0.5)
            col = col_box

            col.label(text='Name :')
            row = col.row()
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'oper_name', text='', icon_value=0, emboss=True)

            col.separator(factor=0.5)
            col.label(text='Discription :')
            row = col.row()
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'oper_disc', text='', icon_value=0, emboss=True)

            col.separator(factor=1.5)
            row = col.row()
            row.use_property_split = False
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'oper_keys', text='keys', icon_value=0, emboss=True, expand=True)

            col.separator(factor=0.5)
            col.label(text='Code :')
            row = col.row(align=True)
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'oper_code', text='', icon_value=0, emboss=True)
            full_path = f"{button_path}.oper_code"
            op = row.operator('cui.set_selection', text='', icon_value=35, emboss=True)
            op.prop = full_path
            if button.error != '':
                col.label(text=f"Error : {button.error}", icon_value=3)

        elif button.type == "Bool Custom":
            show_interface_options = True
            col = col_box

            col.label(text='Name :')
            row = col.row()
            row.scale_x = 2
            row.scale_y = 1.11
            row.prop(button, 'bool_name', text='', icon_value=0, emboss=True)
            row = row.row()
            row.scale_x = 1
            row.use_property_split = False
            row.prop(button, 'bool_default', text='Default', icon_value=0, emboss=True)
            
            col.separator(factor=0.5)
            col.label(text='Discription :')
            row = col.row()
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'bool_disc', text='', icon_value=0, emboss=True)

            col.separator(factor=0.5)
            col.label(text='Update Code :')
            row = col.row(align=True)
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'bool_update_code', text='', icon_value=0, emboss=True)
            full_path = f"{button_path}.bool_update_code"
            op = row.operator('cui.set_selection', text='', icon_value=35, emboss=True)
            op.prop = full_path
            if button.error != '':
                col.label(text=f"Error : {button.error}", icon_value=3)
            is_bool = True

        elif button.type == "Enum Custom":
            show_interface_options = True

            # col_box.separator(factor=1)
            col_box.label(text='Name :')
            row = col_box.row()
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'enum_name', text='', icon_value=0, emboss=True)

            col_box.separator(factor=0.5)
            col_box.label(text='Discription :')
            row = col_box.row()
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'enum_disc', text='', icon_value=0, emboss=True)

            col_box.separator(factor=0.5)
            col_box.use_property_split = False
            col_box.prop(button, 'use_dynamic_items', text='Use Dynamic Items', icon_value=0, emboss=True)

            col_box.separator(factor=0.5)
            if button.use_dynamic_items:
                col_box.label(text='List Code :')
                row = col_box.row(align=True)
                row.scale_x = 1.11
                row.scale_y = 1.11
                row.prop(button, 'item_list_code', text='', icon_value=0, emboss=True)
                full_path = f"{button_path}.item_list_code"
                op = row.operator('cui.set_selection', text='', icon_value=35, emboss=True)
                op.prop = full_path
            else:
                row = col_box.row(align=True)
                row.use_property_split = False
                col = row.column(align=False)
                col.use_property_split = False
                #TODO : Display Collection
                col.template_list('CUI_UL_DISPLAY_COLLECTION_ENUM_ITEMS', "", button, 'enum_items', button, 'enum_active_index', rows=0)
                row.separator(factor=1.0)
                col = row.column(align=True)
                col.use_property_split = False
                col.scale_x = 1.1
                col.scale_y = 1.1
                op = col.operator('cui.add_custom_enum_item', text='', icon_value=31, emboss=True, depress=False)
                op.mode = mode
                op = col.operator('cui.remove_custom_enum_item', text='', icon_value=32, emboss=True, depress=False)
                op.mode = mode

                col.separator(factor=1.0)
                op = col.operator('cui.move_custom_enum_item', text='', icon_value=7, emboss=True, depress=False)
                op.mode = mode
                op.is_up = True
                op = col.operator('cui.move_custom_enum_item', text='', icon_value=5, emboss=True, depress=False)
                op.mode = mode
                op.is_up = False

            col_box.separator(factor=0.5)
            col_box.label(text="Main Code :")
            row = col_box.row(align=True)
            row.scale_x = 1.11
            row.scale_y = 1.11
            row.prop(button, 'enum_update_code', text='', icon_value=0, emboss=True)
            full_path = f"{button_path}.enum_update_code"
            op = row.operator('cui.set_selection', text='', icon_value=35, emboss=True)
            op.prop = full_path
            if button.error != '':
                col_box.label(text=f"Error : {button.error}", icon_value=3)

        elif button.type == "Group":
            layout.prop(bpy.context.scene, 'cui_prop_group_parent', text='Group Object', icon_value=0, emboss=True)
            layout.prop(bpy.context.scene, 'cui_prop_group', text='Group', icon_value=0, emboss=True)

            # row = layout.row(align=True)
            # row.prop(button, 'group_parent', text='Internal', icon_value=0, emboss=False)
            # row.prop(button, 'group', text='', icon_value=0, emboss=False)

        if show_interface_options:
            col_box.separator(factor=1.5)
            row = col_box.row(align=True)
            row.use_property_split = False
            row.use_property_decorate = False
            row.alignment = 'EXPAND'
            row.prop(button, 'is_expand', text='Expand', icon_value=0, emboss=True, toggle=True)
            row.prop(button, 'is_slider', text='Slider', icon_value=0, emboss=True, toggle=True)
            row.prop(button, 'is_toggle', text='Toggle', icon_value=0, emboss=True, toggle=True)
            row.prop(button, 'is_invert', text='Invert', icon_value=0, emboss=True, toggle=True)
            row.prop(button, 'is_split', text='Split', icon_value=0, emboss=True, toggle=True)
            col_box.separator(factor=0.5)
            col = col_box.column(align=True)
            col.use_property_split = True
            col.prop(button, 'label', text='Label', icon_value=0, emboss=True)
            col.separator(factor=0.5)
            col.prop(button, 'label_scale', text='Label Scale', icon_value=0, emboss=True)
            if is_bool:
                col.prop(button, 'is_emboss', text='emboss', icon_value=0, emboss=True)




def get_select_layer_bones():
    pre_code = ''
    oper_code = '''
class CUI_OT_SELECT_LAYER_BONES(bpy.types.Operator):
    bl_idname = "cui.select_layer_bones"
    bl_label = "Select Layer Bones"
    bl_description = "(Click = Select bones, Shift = Preserve other selection, Alt = Unselect Layer Bones)"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty(name='Layer Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False
    
    def __init__(self):
        self.shift = False
        self.alt = False

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        is_select_layer = (False if self.alt else True)
        is_deselect_select = (not self.shift and not self.alt)
        selected_bones = get_bones(context, True)

        armature = context.object.data
        if context.mode != 'EDIT_ARMATURE':
            bones = [bone for bone in armature.bones if bone.layers[self.index]]
            if len(bones) > 0:
                if is_deselect_select:
                    active = armature.bones.active
                    if active not in bones:
                        armature.bones.active = bones[0]
                    for bone in selected_bones:
                        bone.select_tail = False
                        bone.select_head = False
                        bone.select = False
                for bone in bones:
                    bone.select_head = is_select_layer
                    bone.select_tail = is_select_layer
                    bone.select = is_select_layer
        else:
            bones = [bone for bone in armature.edit_bones if bone.layers[self.index]]
            if len(bones) > 0:
                if is_deselect_select:
                    active = context.active_bone
                    if active not in bones:
                        armature.edit_bones.active = bones[0]
                    for bone in selected_bones:
                        bone.select_tail = False
                        bone.select_head = False
                        bone.select = False
                for bone in bones:
                    bone.select_head = is_select_layer
                    bone.select_tail = is_select_layer
                    bone.select = is_select_layer

        return {"FINISHED"}
'''
    return (pre_code, oper_code)

class CUI_OT_SELECT_LAYER_BONES(bpy.types.Operator):
    bl_idname = "cui.select_layer_bones"
    bl_label = "Select Layer Bones"
    bl_description = "(Click = Select bones, Shift = Preserve other selection, Alt = Unselect Layer Bones)"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty(name='Layer Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False
    
    def __init__(self):
        self.shift = False
        self.alt = False

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt
        return self.execute(context)

    def execute(self, context):
        is_select_layer = (False if self.alt else True)
        is_deselect_select = (not self.shift and not self.alt)
        selected_bones = get_bones(context, True)

        armature = context.object.data
        if context.mode != 'EDIT_ARMATURE':
            bones = [bone for bone in armature.bones if bone.layers[self.index]]
            if len(bones) > 0:
                if is_deselect_select:
                    active = armature.bones.active
                    if active not in bones:
                        armature.bones.active = bones[0]
                    for bone in selected_bones:
                        bone.select_tail = False
                        bone.select_head = False
                        bone.select = False
                for bone in bones:
                    bone.select_head = is_select_layer
                    bone.select_tail = is_select_layer
                    bone.select = is_select_layer
        else:
            bones = [bone for bone in armature.edit_bones if bone.layers[self.index]]
            if len(bones) > 0:
                if is_deselect_select:
                    active = context.active_bone
                    if active not in bones:
                        armature.edit_bones.active = bones[0]
                    for bone in selected_bones:
                        bone.select_tail = False
                        bone.select_head = False
                        bone.select = False
                for bone in bones:
                    bone.select_head = is_select_layer
                    bone.select_tail = is_select_layer
                    bone.select = is_select_layer

        return {"FINISHED"}

def get_add_to_layer():
    pre_code = ''
    oper_code = '''
class CUI_OT_ADD_TO_LAYER(bpy.types.Operator):
    bl_idname = "cui.add_to_layer"
    bl_label = "Add to Layer"
    bl_description = "(Click = Add Selected bones to layer, Shift = Add with preserve other layers, Alt = Clear Layer)"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty(name='Layer Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')
    clear_move: bpy.props.IntProperty(name='Clear Move', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False
    
    def __init__(self):
        self.shift = False
        self.alt = False

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)

    def execute(self, context):
        if not self.alt:
            if bpy.context.mode=='EDIT_ARMATURE':
                bones = bpy.context.selected_editable_bones
                for bone in bones:
                    bone.layers[self.index] = True
                    if not self.shift:
                        for idx in range(len(bone.layers)):
                            if idx != self.index:
                                bone.layers[idx] = False
            elif bpy.context.mode=='POSE':
                bones = bpy.context.selected_pose_bones_from_active_object
                for pbone in bones:
                    pbone.bone.layers[self.index] = True
                    if not self.shift:
                        for idx in range(len(pbone.bone.layers)):
                            if idx != self.index:
                                pbone.bone.layers[idx] = False
        else:
            if self.index != self.clear_move:
                bones = bpy.context.object.data.bones
                for bone in bones:
                    if bone.layers[self.index]:
                        bone.layers[self.clear_move] = True
                        bone.layers[self.index] = False
        return {"FINISHED"}
'''
    return (pre_code, oper_code)

class CUI_OT_ADD_TO_LAYER(bpy.types.Operator):
    bl_idname = "cui.add_to_layer"
    bl_label = "Add to Layer"
    bl_description = "(Click = Add Selected bones to layer, Shift = Add with preserve other layers, Alt = Clear Layer)"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty(name='Layer Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')
    clear_move: bpy.props.IntProperty(name='Clear Move', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False
    
    def __init__(self):
        self.shift = False
        self.alt = False

    def invoke(self, context, event):
        self.shift = event.shift
        self.alt = event.alt

        return self.execute(context)

    def execute(self, context):
        if not self.alt:
            if bpy.context.mode=='EDIT_ARMATURE':
                bones = bpy.context.selected_editable_bones
                for bone in bones:
                    bone.layers[self.index] = True
                    if not self.shift:
                        for idx in range(len(bone.layers)):
                            if idx != self.index:
                                bone.layers[idx] = False
            elif bpy.context.mode=='POSE':
                bones = bpy.context.selected_pose_bones_from_active_object
                for pbone in bones:
                    pbone.bone.layers[self.index] = True
                    if not self.shift:
                        for idx in range(len(pbone.bone.layers)):
                            if idx != self.index:
                                pbone.bone.layers[idx] = False
        else:
            if self.index != self.clear_move:
                bones = bpy.context.object.data.bones
                for bone in bones:
                    if bone.layers[self.index]:
                        bone.layers[self.clear_move] = True
                        bone.layers[self.index] = False
        return {"FINISHED"}

# TODO : Enum Operator
class CUI_OT_ADD_CUSTOM_ENUM_ITEM(bpy.types.Operator):
    bl_idname = "cui.add_custom_enum_item"
    bl_label = "Add Custom Enum Item"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.mode.upper() == 'BONE' or self.mode.upper() == 'OBJECT':
            parent = get_parent(self.mode)

            col_collection = parent.cui_prop_col_collection
            active_col_index = parent.cui_prop_active_col_index
            row_collection = col_collection[active_col_index].row_collection
            active_row_index = parent.cui_prop_active_row_index
            button = row_collection[active_row_index]

            new_item = button.enum_items.add()
            button.enum_active_index = button.enum_items.values().index(new_item)
            cui_update_enum_custom(button, context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_REMOVE_CUSTOM_ENUM_ITEM(bpy.types.Operator):
    bl_idname = "cui.remove_custom_enum_item"
    bl_label = "Remove Custom Enum Item"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.mode.upper() == 'BONE' or self.mode.upper() == 'OBJECT':
            parent = get_parent(self.mode)

            col_collection = parent.cui_prop_col_collection
            active_col_index = parent.cui_prop_active_col_index
            row_collection = col_collection[active_col_index].row_collection
            active_row_index = parent.cui_prop_active_row_index
            button = row_collection[active_row_index]

            button.enum_items.remove(button.enum_active_index)
            if button.enum_items:
                button.enum_active_index -= 1
            cui_update_enum_custom(button, context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_MOVE_CUSTOM_ENUM_ITEM(bpy.types.Operator):
    bl_idname = "cui.move_custom_enum_item"
    bl_label = "Move Custom Enum Item"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    is_up: bpy.props.BoolProperty(name='Direction', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.mode.upper() == 'BONE' or self.mode.upper() == 'OBJECT':
            parent = get_parent(self.mode)

            col_collection = parent.cui_prop_col_collection
            active_col_index = parent.cui_prop_active_col_index
            row_collection = col_collection[active_col_index].row_collection
            active_row_index = parent.cui_prop_active_row_index
            button = row_collection[active_row_index]

            index = button.enum_active_index
            move_to = (index-1 if self.is_up else index+1)
            if 0 <= move_to and move_to < len(button.enum_items):
                button.enum_items.move(button.enum_active_index, move_to)
                button.enum_active_index = move_to
                cui_update_enum_custom(button, context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_SET_LAYER_INDEX(bpy.types.Operator):
    bl_idname = "cui.set_layer_index"
    bl_label = "Set Layer Index"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty(name='index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        parent = context.object.data

        col_collection = parent.cui_prop_col_collection
        active_col_index = parent.cui_prop_active_col_index
        row_collection = col_collection[active_col_index].row_collection
        active_row_index = parent.cui_prop_active_row_index

        button = row_collection[active_row_index]
        button.layer_index = self.index
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

def get_parent(mode):
    parent = None
    if mode.upper() == 'LAYER':
        if bpy.context.object is not None and bpy.context.object.type == 'ARMATURE':
            parent = bpy.context.object.data
    elif mode.upper() == 'BONE':
        if bpy.context.mode == 'POSE' and bpy.context.pose_object is not None and bpy.context.active_pose_bone is not None:
            parent = bpy.context.active_pose_bone
    elif mode.upper() == 'OBJECT':
        if bpy.context.object is not None:
            parent = bpy.context.object
    elif mode.upper() == 'SCENE':
        if bpy.context.scene is not None:
            parent = bpy.context.scene
    return parent


class CUI_OT_SET_BUTTON_ACTIVE(bpy.types.Operator):
    bl_idname = "cui.set_button_active"
    bl_label = "Set Button Active"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    col_index: bpy.props.IntProperty(name='col index', description='', options={'HIDDEN'}, default=0, subtype='NONE')
    row_index: bpy.props.IntProperty(name='row index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        parent = get_parent(self.mode)
        if parent is not None:
            parent.cui_prop_active_col_index = self.col_index
            parent.cui_prop_active_row_index = self.row_index
            # if self.mode.upper() == 'BONE':
            #     update_group_data(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_ADD_ROW_BUTTON(bpy.types.Operator):
    bl_idname = "cui.add_row_button"
    bl_label = "Add Row Button"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    col_index: bpy.props.IntProperty(name='col index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        parent = get_parent(self.mode)
        if parent is not None:
            new_row_item = parent.cui_prop_col_collection[self.col_index].row_collection.add()
            parent.cui_prop_active_row_index = parent.cui_prop_col_collection[self.col_index].row_collection.values().index(new_row_item)
            parent.cui_prop_active_col_index = self.col_index
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_ADD_COLUMN_BUTTON(bpy.types.Operator):
    bl_idname = "cui.add_column_button"
    bl_label = "Add Column Button"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        parent = get_parent(self.mode)
        print(self.mode, parent)
        if parent is not None:
            new_col_item = parent.cui_prop_col_collection.add()
            new_row_item = new_col_item.row_collection.add()
            new_col_index = parent.cui_prop_col_collection.values().index(new_col_item)
            to_col_index = new_col_index
            if parent.cui_prop_active_col_index < len(parent.cui_prop_col_collection) - 1:
                to_col_index = parent.cui_prop_active_col_index + 1
                parent.cui_prop_col_collection.move(new_col_index, to_col_index)
            parent.cui_prop_active_col_index = to_col_index
            parent.cui_prop_active_row_index = 0
            if parent.cui_id == '':
                parent.cui_id = generate_id()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CUI_OT_REMOVE_BUTTON(bpy.types.Operator):
    bl_idname = "cui.remove_button"
    bl_label = "Remove Button"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        parent = get_parent(self.mode)
        if parent is not None:
            col_collection = parent.cui_prop_col_collection
            active_col_index = parent.cui_prop_active_col_index
            row_collection = col_collection[active_col_index].row_collection
            active_row_index = parent.cui_prop_active_row_index

            def reset_active_index():
                if (len(col_collection.values()) <= parent.cui_prop_active_col_index):
                    parent.cui_prop_active_col_index = int(len(col_collection.values()) - 1)
                if len(col_collection) > 0:
                    active_col_len = len(col_collection[parent.cui_prop_active_col_index].row_collection.values())
                    if (active_col_len) <= parent.cui_prop_active_row_index:
                        parent.cui_prop_active_row_index = active_col_len - 1

            if len(row_collection) > active_row_index:
                row_collection.remove(active_row_index)
            if (len(row_collection.values()) == 0):
                if len(col_collection) > active_col_index:
                    col_collection.remove(active_col_index)
            reset_active_index()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

class CUI_OT_MOVE_BUTTON(bpy.types.Operator):
    bl_idname = "cui.move_button"
    bl_label = "Move Button"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.StringProperty(name='Mode', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    direction: bpy.props.EnumProperty(name='direction', description='', options={'HIDDEN'}, items=[('Up', 'Up', '', 0, 0), ('Down', 'Down', '', 0, 1), ('Left', 'Left', '', 0, 2), ('Right', 'Right', '', 0, 3)])

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        parent = get_parent(self.mode)
        if parent is not None:
            col_collection = parent.cui_prop_col_collection
            active_col_index = parent.cui_prop_active_col_index
            row_collection = col_collection[active_col_index].row_collection
            active_row_index = parent.cui_prop_active_row_index
            
            def copy_data(from_row, to_row):
                to_row.name = from_row.name
                to_row.type = from_row.type
                if self.mode.upper() == 'LAYER': # TODO: copy button props
                    to_row.layer_index = from_row.layer_index
                    to_row.path = from_row.path

            def move_column(to_index):
                new_row_item = col_collection[to_index].row_collection.add()
                row_coll = col_collection[parent.cui_prop_active_col_index].row_collection
                copy_data(row_coll[parent.cui_prop_active_row_index], new_row_item)
                if len(row_coll) > parent.cui_prop_active_row_index:
                    row_coll.remove(parent.cui_prop_active_row_index)
                if (len(col_collection[to_index].row_collection.values()) <= parent.cui_prop_active_row_index):
                    parent.cui_prop_active_row_index = int(len(col_collection[to_index].row_collection.values()) - 1)
                if (col_collection[to_index].row_collection.values().index(new_row_item) != parent.cui_prop_active_row_index):
                    col_collection[to_index].row_collection.move(col_collection[to_index].row_collection, parent.cui_prop_active_row_index)
                parent.cui_prop_active_col_index = to_index

                for (idx, col) in reversed(list(enumerate(col_collection))):
                    if len(col.row_collection) == 0:
                        col_collection.remove(idx)
                        if parent.cui_prop_active_col_index > idx:
                            parent.cui_prop_active_col_index -= 1

                if parent.cui_prop_active_col_index >= len(col_collection):
                    parent.cui_prop_active_col_index = len(col_collection) - 1

            if self.direction == "Up":
                if active_col_index == 0:
                    new_col_item = col_collection.add()
                    from_idx = col_collection.values().index(new_col_item)
                    col_collection.move(from_idx, 0)
                    active_col_index += 1
                    parent.cui_prop_active_col_index += 1
                    move_column(0)
                elif (0 <= int(active_col_index - 1)):
                    move_column(int(active_col_index - 1))
            elif self.direction == "Down":
                if active_col_index == len(col_collection.values())-1:
                    new_col_item = col_collection.add()
                    move_column(len(col_collection.values())-1)
                elif (len(col_collection.values()) > int(active_col_index + 1)):
                    move_column(int(active_col_index + 1))
            elif self.direction == "Left":
                if (0 <= int(active_row_index - 1)):
                    row_collection.move(active_row_index, int(active_row_index - 1))
                    parent.cui_prop_active_row_index -= 1

            elif self.direction == "Right":
                if (len(row_collection.values()) > int(active_row_index + 1)):
                    row_collection.move(active_row_index, int(active_row_index + 1))
                    parent.cui_prop_active_row_index += 1
            else:
                pass
            return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)
    


def get_inherit_list():
    context = bpy.context
    def get_family(obj, prev_obj=None, family_list=[[], []], is_child=False, is_first=True):
        if is_first or obj.cui_prop_let_inheritance:
            if not is_child:
                family_list[0].append(obj.name)
            else:
                family_list[1].append(obj.name)
        if obj.parent is not None and not (prev_obj is not None and obj.parent == prev_obj):
            family_list = get_family(obj.parent, obj, family_list, False, False)
        if len(obj.children) > 0:
            for child in obj.children:
                if not (prev_obj is not None and child == prev_obj):
                    family_list = get_family(child, obj, family_list, True, False)
        return family_list

    if context.object is not None:
        family = get_family(context.object)
        items = family[0] + family[1]
    else:
        items = []
    return items

def cui_editor_object_enum_items(self, context):
    items = get_inherit_list()
    enum_items = [(item, item, '', 0, idx) for (idx, item) in enumerate(items)]
    return enum_items



class CUI_GROUP_CUI_LAYER_ROW_GROUP(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', description='', default='Button', subtype='NONE', maxlen=0)
    type: bpy.props.EnumProperty(name='Type', description='', items=[('Layer', 'Layer', '', 0, 0), ('Bool Path', 'Bool Path', '', 0, 1)])
    layer_index: bpy.props.IntProperty(name='Layer Index', description='', default=1, subtype='NONE')
    path: bpy.props.StringProperty(name='Path', description='', default='bpy.context.object.data.layers[1]', subtype='NONE', maxlen=0)
    icon: bpy.props.IntProperty(name='Icon', description='', default=0, subtype='NONE', min=0, max=936)
    hide: bpy.props.StringProperty(name='Hide Condition', description='', default='', subtype='NONE', maxlen=0)

class CUI_GROUP_CUI_LAYER_COL_GROUP(bpy.types.PropertyGroup):
    split: bpy.props.BoolProperty(name='Split', description='A type of separator for interface', default=False)
    split_box: bpy.props.BoolProperty(name='Split Box', description='Split box if use_box is enabled', default=False)
    header: bpy.props.StringProperty(name='Header', description='', default='', subtype='NONE', maxlen=0)
    row_collection: bpy.props.CollectionProperty(name='Row Collection', description='', type=CUI_GROUP_CUI_LAYER_ROW_GROUP)

def cui_group_parent_enum_items(self, context):
    def get_parent_list():
        if context.mode == 'POSE':
            items = context.object.pose.bones
        else:
            items = None
        parent = get_parent('BONE')
        parent_list = []
        if items is not None:
            parent_list = [item.name for item in items if len(item.cui_prop_col_collection) > 0 and item != parent]
        return ['--- Select ---'] + parent_list

    parent_list = get_parent_list()
    enum_items = [(item, item, '', 0, idx) for idx, item in enumerate(parent_list)]
    return enum_items

def cui_group_enum_items(self, context):
    def get_group_list():
        parent_name = context.scene.cui_prop_group_parent
        parent = None
        if context.mode == 'POSE':
            if parent_name in context.object.pose.bones:
                parent = context.object.pose.bones[parent_name]
        group_list = []
        if parent is not None:
            col_collection = parent.cui_prop_col_collection
            for col in col_collection:
                grp = col.group.strip()
                if not col.align and grp != '':
                    group_list.append(grp)
        return ['--- Select ---'] + group_list

    group_list = get_group_list()
    enum_items = [(item, item, '', 0, idx) for idx, item in enumerate(group_list)]
    return enum_items

prev_group_parent = '--- Select ---'
freeze_group_update = False
def cui_update_group_parent(self, context):
    global prev_group_parent, freeze_group_update
    if prev_group_parent != self.cui_prop_group_parent:
        prev_group_parent = self.cui_prop_group_parent
        if not freeze_group_update:
            self.cui_prop_group = '--- Select ---'

        parent = get_parent('BONE')
        if parent is not None:
            col_collection = parent.cui_prop_col_collection
            active_col_index = parent.cui_prop_active_col_index
            row_collection = col_collection[active_col_index].row_collection
            active_row_index = parent.cui_prop_active_row_index
            button = row_collection[active_row_index]
            if button.type == 'Group':
                button.group_parent = self.cui_prop_group_parent


def cui_update_group(self, context):
    parent = get_parent('BONE')
    if parent is not None:
        col_collection = parent.cui_prop_col_collection
        active_col_index = parent.cui_prop_active_col_index
        row_collection = col_collection[active_col_index].row_collection
        active_row_index = parent.cui_prop_active_row_index
        button = row_collection[active_row_index]
        if button.type == 'Group':
            button.group = self.cui_prop_group


def update_group_data(context=bpy.context):
    parent = get_parent('BONE')
    if parent is not None:
        col_collection = parent.cui_prop_col_collection
        active_col_index = parent.cui_prop_active_col_index
        row_collection = col_collection[active_col_index].row_collection
        active_row_index = parent.cui_prop_active_row_index
        button = row_collection[active_row_index]
        if button.type == 'Group':
            global freeze_group_update
            freeze_group_update = True
            context.scene.cui_prop_group_parent = button.group_parent
            context.scene.cui_prop_group = button.group
            freeze_group_update = False


def cui_update_editor_group(self, context):
    update_group_data(context)

def cui_update_enum_custom(self, context):
    if repr(self).find('...CUI_GROUP_CUI_PROP_ROW_GROUP') > -1:
        parent = get_parent('BONE')
    else:
        parent = self.id_data
    custom_enum_property(self, 'T' + parent.cui_id, False)
def cui_update_bool_custom(self, context):
    if repr(self).find('...CUI_GROUP_CUI_PROP_ROW_GROUP') > -1:
        parent = get_parent('BONE')
    else:
        parent = self.id_data
    custom_bool_property(self, 'T' + parent.cui_id, False)
def cui_update_oper_custom(self, context):
    if repr(self).find('...CUI_GROUP_CUI_PROP_ROW_GROUP') > -1:
        parent = get_parent('BONE')
    else:
        parent = self.id_data
    custom_operator(self, 'T' + parent.cui_id, False)

# TODO Register
class CUI_OT_REGISTER_CUSTOM_BUTTONS(bpy.types.Operator):
    bl_idname = "cui.register_custom_buttons"
    bl_label = "Register Custom Buttons"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if context.mode == 'POSE':
            register_custom_buttons('BONE')
        register_custom_buttons('OBJECT')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

register_done_list = []
def need_register_custom_buttons(mode):
    need_register = False
    is_done = False
    def register_buttons(col_collection, need_register, is_done):
        for col_item in col_collection:
            for button in col_item.row_collection:
                if button.type == 'Bool Custom':
                    if button.bool_id != '' and not hasattr(bpy.context.scene, button.bool_id):
                        need_register = True
                        is_done = True
                elif button.type == 'Enum Custom':
                    if button.enum_id != '' and not hasattr(bpy.context.scene, button.enum_id):
                        need_register = True
                        is_done = True
                elif button.type == 'Operator Custom':
                    if button.oper_id != '' and  button.oper_class != '' and not has_operator(button.oper_id):
                        need_register = True
                        is_done = True
                elif button.type == 'Group':
                    group_col_list = get_group_col(button.group_parent, button.group)
                    if group_col_list:
                        (need_register, is_done) = register_buttons(group_col_list, need_register, is_done)
                if is_done:
                    break
            if is_done:
                break
        return (need_register, is_done)
    global register_done_list
    parent = get_parent(mode)
    col_collection = parent.cui_prop_col_collection
    (need_register, _) = register_buttons(col_collection, need_register, is_done)
    if not need_register:
        register_done_list.append(f"{mode}_{parent.cui_id}")
    return need_register

def register_custom_buttons(mode):
    def register_buttons(col_collection, cui_id):
        for col_item in col_collection:
            for button in col_item.row_collection:
                if button.type == 'Bool Custom':
                    print('\nbool found : ', button.bool_id)
                    if button.bool_id != '' and not hasattr(bpy.context.scene, button.bool_id):
                        custom_bool_property(button, cui_id, False)
                        print(f"bpy.context.scene.{button.bool_id}")
                elif button.type == 'Enum Custom':
                    print('\nenum found : ', button.enum_id)
                    if button.enum_id != '' and not hasattr(bpy.context.scene, button.enum_id):
                        custom_enum_property(button, cui_id, False)
                        print(f"bpy.context.scene.{button.enum_id}")
                elif button.type == 'Operator Custom':
                    print('\noper found : ', button.oper_class)
                    if button.oper_id != '' and  button.oper_class != '' and not has_operator(button.oper_id):
                        custom_operator(button, cui_id, False)
                        print(f"bpy.ops.{button.oper_class}")
                elif button.type == 'Group':
                    group_col_list = get_group_col(button.group_parent, button.group)
                    if group_col_list:
                        parents = get_parents(mode)
                        parent = parents[button.group_parent]
                        register_buttons(group_col_list, 'T' + parent.cui_id)
    global register_done_list
    parent = get_parent(mode)
    col_collection = parent.cui_prop_col_collection
    register_buttons(col_collection, 'T' + parent.cui_id)
    register_done_list.append(f"{mode}_{parent.cui_id}")

class CUI_GROUP_CUI_PROP_ENUM_ITEMS(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', description='', default='Item', subtype='NONE', maxlen=0)

def cui_enum_items_button_type(self, context):
    items=[
        ('Property', 'Property', '', 0, 0),
        ('Operator', 'Operator', '', 0, 1),
        ('Bool Custom', 'Bool Custom', '', 0, 2),
        ('Enum Custom', 'Enum Custom', '', 0, 3),
        ('Operator Custom', 'Operator Custom', '', 0, 4),
    ]
    if repr(self).find('...CUI_GROUP_CUI_PROP_ROW_GROUP') > -1:
        items += [('Group', 'Group', '', 0, 5)]
    return items

# TODO : PROP_ROW_GROUP
class CUI_GROUP_CUI_PROP_ROW_GROUP(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', description='', default='Button', subtype='NONE', maxlen=0)
    type: bpy.props.EnumProperty(name='Type', description='', items=cui_enum_items_button_type)
    icon: bpy.props.IntProperty(name='Icon', description='', default=0, subtype='NONE', min=0, max=936)
    use_icon_code: bpy.props.BoolProperty(name='Use Icon Condition', description='', default=False)
    icon_code: bpy.props.StringProperty(name='Icon Condition', description='', default='0', subtype='NONE', maxlen=0)
    hide: bpy.props.StringProperty(name='Hide Condition', description='', default='', subtype='NONE', maxlen=0)
    scale: bpy.props.IntProperty(name='Scale', description='', default=1, subtype='NONE', min=1, max=100)
    path_prop: bpy.props.StringProperty(name='Path Property', description='', default='bpy.context.object.show_name', subtype='NONE', maxlen=0)
    path_oper: bpy.props.StringProperty(name='Path Operator', description='', default='bpy.ops.cui.dummy_button_operator()', subtype='NONE', maxlen=0)
    group_parent: bpy.props.StringProperty(name='Group Parent', description='', default='--- Select ---', subtype='NONE', maxlen=0)
    group: bpy.props.StringProperty(name='Group', description='', default='--- Select ---', subtype='NONE', maxlen=0)

    oper_name: bpy.props.StringProperty(name='Operator Name', description='', default='', subtype='NONE', maxlen=0, update=cui_update_oper_custom)
    oper_disc: bpy.props.StringProperty(name='Operator Discription', description='', default='', subtype='NONE', maxlen=0, update=cui_update_oper_custom)
    oper_code: bpy.props.StringProperty(name='Operator Code', description='', default='', subtype='NONE', maxlen=0, update=cui_update_oper_custom)
    oper_id: bpy.props.StringProperty(name='Operator ID', description='', default='', subtype='NONE', maxlen=0)
    oper_class: bpy.props.StringProperty(name='Operator Class', description='', default='', subtype='NONE', maxlen=0)
    oper_keys: bpy.props.EnumProperty(name='Layer Template', description='', options={'ENUM_FLAG'}, items=[
        ('SHIFT', 'self.shift', '', 0, 1),
        ('CTRL', 'self.ctrl', '', 0, 2),
        ('ALT', 'self.alt', '', 0, 4),
        ('OSKEY', 'self.oskey', '', 0, 8),
    ], update=cui_update_oper_custom)

    bool_name: bpy.props.StringProperty(name='Bool Property Name', description='', default='', subtype='NONE', maxlen=0, update=cui_update_bool_custom)
    bool_disc: bpy.props.StringProperty(name='Bool Discription', description='', default='', subtype='NONE', maxlen=0, update=cui_update_bool_custom)
    bool_default: bpy.props.BoolProperty(name='Bool Default', description='', default=False, update=cui_update_bool_custom)
    bool_update_code: bpy.props.StringProperty(name='Bool Update Code', description='', default='', subtype='NONE', maxlen=0, update=cui_update_bool_custom)
    bool_id: bpy.props.StringProperty(name='Bool ID', description='', default='', subtype='NONE', maxlen=0)

    enum_name: bpy.props.StringProperty(name='Enum Property Name', description='', default='', subtype='NONE', maxlen=0, update=cui_update_enum_custom)
    enum_items: bpy.props.CollectionProperty(name='Enum Items', description='', type=CUI_GROUP_CUI_PROP_ENUM_ITEMS)
    enum_active_index: bpy.props.IntProperty(name='Enum Active Index', description='', default=0, subtype='NONE')
    use_dynamic_items: bpy.props.BoolProperty(name='Use Dynamic Items', description='', default=False, update=cui_update_enum_custom)
    item_list_code: bpy.props.StringProperty(name='Item List Code', description="use 'item' for active item name", default='', subtype='NONE', maxlen=0, update=cui_update_enum_custom)
    enum_update_code: bpy.props.StringProperty(name='Item List Code', description="use 'item' for active item name", default='', subtype='NONE', maxlen=0, update=cui_update_enum_custom)
    enum_disc: bpy.props.StringProperty(name='Enum Discription', description='', default='', subtype='NONE', maxlen=0, update=cui_update_enum_custom)
    enum_id: bpy.props.StringProperty(name='Enum ID', description='', default='', subtype='NONE', maxlen=0)

    error: bpy.props.StringProperty(name='Error', description='', default='', subtype='NONE', maxlen=0)
    use_name: bpy.props.BoolProperty(name='Use Name', description='', default=True)
    label: bpy.props.StringProperty(name='Name', description='', default='', subtype='NONE', maxlen=0)
    label_scale: bpy.props.IntProperty(name='Label Scale', description='', default=1, subtype='NONE', min=1, max=100)

    is_emboss: bpy.props.BoolProperty(name='Is Emboss', description='', default=True)
    is_expand: bpy.props.BoolProperty(name='Is Expand', description='', default=False)
    is_slider: bpy.props.BoolProperty(name='Is Slider', description='', default=False)
    is_toggle: bpy.props.BoolProperty(name='Is Toggle', description='', default=True)
    is_invert: bpy.props.BoolProperty(name='Is Invert', description='', default=False)
    is_split: bpy.props.BoolProperty(name='Is Split', description='', default=False)


def cui_update_col_group_align(self, context):
    if self.align: self.split = False

def cui_update_col_group_split(self, context):
    if self.split: self.align = False

class CUI_GROUP_CUI_PROP_COL_GROUP(bpy.types.PropertyGroup):
    align: bpy.props.BoolProperty(name='Align', description='', default=False, update=cui_update_col_group_align)
    split: bpy.props.BoolProperty(name='Split', description='A type of separator for interface', default=False, update=cui_update_col_group_split)
    split_box: bpy.props.BoolProperty(name='Split Box', description='Split box if use_box is enabled', default=False)
    header: bpy.props.StringProperty(name='Header', description='', default='', subtype='NONE', maxlen=0)
    group: bpy.props.StringProperty(name='Group', description='', default='', subtype='NONE', maxlen=0)
    row_collection: bpy.props.CollectionProperty(name='Row Collection', description='', type=CUI_GROUP_CUI_PROP_ROW_GROUP)


grp_classes = (
    CUI_UL_DISPLAY_COLLECTION_ENUM_ITEMS,
    CUI_GROUP_CUI_PROP_ENUM_ITEMS,
    CUI_GROUP_CUI_LAYER_ROW_GROUP,
    CUI_GROUP_CUI_LAYER_COL_GROUP,
    CUI_GROUP_CUI_PROP_ROW_GROUP,
    CUI_GROUP_CUI_PROP_COL_GROUP,
)
classes = (
    CUI_OT_DUMMY_BUTTON_OPERATOR,
    CUI_OT_Set_Selection,
    CUI_OT_CHILDREN_SELECTION,
    CUI_OT_CUI_SETTINGS,
    CUI_OT_REGISTER_CUSTOM_BUTTONS,
    CUI_OT_COPY_LAYER_CODE,
    CUI_OT_SELECT_LAYER_BONES,
    CUI_OT_ADD_CUSTOM_ENUM_ITEM,
    CUI_OT_REMOVE_CUSTOM_ENUM_ITEM,
    CUI_OT_MOVE_CUSTOM_ENUM_ITEM,
    CUI_OT_ADD_TO_LAYER,
    CUI_OT_SET_BUTTON_ACTIVE,
    CUI_OT_ADD_ROW_BUTTON,
    CUI_OT_ADD_COLUMN_BUTTON,
    CUI_OT_REMOVE_BUTTON,
    CUI_OT_MOVE_BUTTON,
    CUI_OT_SET_LAYER_INDEX,
    
    CUI_OT_SET_ICON,
    CUI_OT_SELECT_ICON,
    CUI_PT_EDITOR_PANEL,
    CUI_PT_LAYER_PANEL,
    CUI_PT_BONE_PANEL,
    CUI_PT_OBJECT_PANEL,
    CUI_PT_SCENE_PANEL,
)

def register():
    from bpy.utils import register_class
    for cls in grp_classes:
        try: register_class(cls)
        except: pass

    try:
        if bpy.context.mode == 'POSE':
            register_custom_buttons('BONE')
        register_custom_buttons('OBJECT')
    except: pass

    bpy.types.Scene.cui_id = bpy.props.StringProperty(name='CUI ID', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Object.cui_id = bpy.props.StringProperty(name='CUI ID', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.PoseBone.cui_id = bpy.props.StringProperty(name='CUI ID', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Armature.cui_id = bpy.props.StringProperty(name='CUI ID', description='', default='', subtype='NONE', maxlen=0)

    # bpy.types.Scene.cui_editor_mode = bpy.props.EnumProperty(name='Editor Mode', description='', update=cui_update_editor_group, items=[('Layer', 'Layer', '', 0, 0), ('Bone', 'Bone', '', 0, 1), ('Object', 'Object', '', 0, 2), ('Scene', 'Scene', '', 0, 3)])
    bpy.types.Object.cui_editor_object = bpy.props.EnumProperty(name='Editor Object', description='', default=0, items=cui_editor_object_enum_items)
    bpy.types.Scene.cui_prop_template = bpy.props.EnumProperty(name='Layer Template', description='', items=[('None', 'None', '', 0, 0), ('Rigify', 'Rigify', '', 0, 1)])
    bpy.types.Scene.cui_prop_group_parent = bpy.props.EnumProperty(name='Group Parent', description='', items=cui_group_parent_enum_items, update=cui_update_group_parent)
    bpy.types.Scene.cui_prop_group = bpy.props.EnumProperty(name='Group', description='', items=cui_group_enum_items, update=cui_update_group)

    # Layer Properties
    bpy.types.Scene.cui_prop_select_mode = bpy.props.BoolProperty(name='Select Mode', description='', default=False)
    bpy.types.Scene.cui_prop_add_mode = bpy.props.BoolProperty(name='Add Mode', description='', default=False)

    bpy.types.Armature.cui_prop_use_parent_buttons = bpy.props.BoolProperty(name='Hide Parent Buttons', description='', default=True)
    bpy.types.Armature.cui_prop_use_display_buttons = bpy.props.BoolProperty(name='Hide Display Buttons', description='', default=True)
    bpy.types.Armature.cui_prop_use_view_buttons = bpy.props.BoolProperty(name='Hide View Buttons', description='', default=True)

    bpy.types.Armature.cui_prop_edit_mode = bpy.props.BoolProperty(name='Edit Mode', description='', default=True)
    bpy.types.Armature.cui_prop_test_mode = bpy.props.BoolProperty(name='Test Mode', description='', default=False)
    bpy.types.Armature.cui_prop_use_select_add = bpy.props.BoolProperty(name='Use Select And Add Buttons', description='', default=False)
    bpy.types.Armature.cui_prop_align_rows = bpy.props.BoolProperty(name='Align Rows', description='', default=False)
    bpy.types.Armature.cui_prop_use_box = bpy.props.BoolProperty(name='Use Box', description='', default=False)

    bpy.types.Armature.cui_prop_col_collection = bpy.props.CollectionProperty(name='Col Collection', description='', type=CUI_GROUP_CUI_LAYER_COL_GROUP)
    bpy.types.Armature.cui_prop_active_col_index = bpy.props.IntProperty(name='Active Col Index', description='', default=0, subtype='NONE')
    bpy.types.Armature.cui_prop_active_row_index = bpy.props.IntProperty(name='Active Row Index', description='', default=0, subtype='NONE')

    bpy.types.Scene.cui_prop_edit_mode = bpy.props.BoolProperty(name='Edit Mode', description='', default=True)
    bpy.types.Scene.cui_prop_use_box = bpy.props.BoolProperty(name='Use Box', description='', default=False)
    bpy.types.Scene.cui_prop_col_collection = bpy.props.CollectionProperty(name='Col Collection', description='', type=CUI_GROUP_CUI_PROP_COL_GROUP)
    bpy.types.Scene.cui_prop_active_col_index = bpy.props.IntProperty(name='Active Col Index', description='', default=0, subtype='NONE')
    bpy.types.Scene.cui_prop_active_row_index = bpy.props.IntProperty(name='Active Row Index', description='', default=0, subtype='NONE')

    bpy.types.Object.cui_prop_let_inheritance = bpy.props.BoolProperty(name='Let Inheritance', description='Allow children and parents to use these properties', default=False)
    bpy.types.Object.cui_prop_show_inherited = bpy.props.BoolProperty(name='Show Inherited', description='Show inherited children and parents properties', default=True)
    bpy.types.Object.cui_prop_show_inherited_as_drop_down = bpy.props.BoolProperty(name='Show Inherited Options As Drop-Down', description='', default=False)

    bpy.types.Object.cui_prop_edit_mode = bpy.props.BoolProperty(name='Edit Mode', description='', default=True)
    bpy.types.Object.cui_prop_use_box = bpy.props.BoolProperty(name='Use Box', description='', default=False)
    bpy.types.Object.cui_prop_col_collection = bpy.props.CollectionProperty(name='Col Collection', description='', type=CUI_GROUP_CUI_PROP_COL_GROUP)
    bpy.types.Object.cui_prop_active_col_index = bpy.props.IntProperty(name='Active Col Index', description='', default=0, subtype='NONE')
    bpy.types.Object.cui_prop_active_row_index = bpy.props.IntProperty(name='Active Row Index', description='', default=0, subtype='NONE')

    bpy.types.PoseBone.cui_prop_edit_mode = bpy.props.BoolProperty(name='Edit Mode', description='', default=True)
    bpy.types.PoseBone.cui_prop_use_box = bpy.props.BoolProperty(name='Use Box', description='', default=False)
    bpy.types.PoseBone.cui_prop_col_collection = bpy.props.CollectionProperty(name='Col Collection', description='', type=CUI_GROUP_CUI_PROP_COL_GROUP)
    bpy.types.PoseBone.cui_prop_active_col_index = bpy.props.IntProperty(name='Active Col Index', description='', default=0, subtype='NONE', update=cui_update_editor_group)
    bpy.types.PoseBone.cui_prop_active_row_index = bpy.props.IntProperty(name='Active Row Index', description='', default=0, subtype='NONE', update=cui_update_editor_group)

    for cls in classes:
        try: register_class(cls)
        except: pass


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        try: unregister_class(cls)
        except: pass

    for cls in reversed(grp_classes):
        try: register_class(cls)
        except: pass


# bpy.context.scene.mx.addon_unregister.append(unregister)
register()


