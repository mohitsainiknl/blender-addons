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

bl_info = {
    "name" : "Custom Tools",
    "author" : "MohitX", 
    "description" : "",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 2),
    "location" : "",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "User Interface" 
}


import bpy
import bpy.utils.previews
import os
import json
import re
import subprocess
import sys
import traceback


addon_keymaps = {}
_icons = None
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
scene = bpy.types.Scene


def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0


def string_to_icon(value):
    if value in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].value
    return string_to_int(value)


setup_variables = []
addon_keymaps = {}
_icons = None
enums = {'ctl_group_list': [], 'ctl_tool_list': [], 'ctl_prop_pie_space_list': [], 'ctl_file_list': [], }
main = {'ctl_group_dict': None, }
variables = {'ctl_test': None, 'ctl_freeze_check': False, }


def ctl_update_ctl_prop_active_file_index_54956(self, context):
    ctl_updated_prop = self.ctl_prop_active_file_index
    ctl_switch_file_to_editor_D655A()


# O_MODE = ('Create' if bpy.context.scene.ctl_prop_setup_mode == 'Update' else 'Update')
# temp_tool_dict = ctl_read_setup_tool_dict_2974(O_MODE)
# TODO X Update Mode
mode_prev = ''


def ctl_update_ctl_prop_setup_mode(self, context):
    MODE = self.ctl_prop_setup_mode
    global mode_prev
    global freeze_var_for_switch
    freeze_var_for_switch = True
    if mode_prev != MODE:
        mode_prev = MODE
        O_MODE = ('Create' if MODE == 'Update' else 'Update')
        tool_dict = get_setup_tool_dict(O_MODE)
        temp_setup_data = ctl_read_setup_tool_dict_2974(MODE)
        if len(temp_setup_data) <= 0:
            bpy.ops.ctl.clear_setup_data('INVOKE_DEFAULT', )
        else:
            set_setup_switch_data(MODE, temp_setup_data)
        ctl_write_setup_tool_dict_8736(O_MODE, tool_dict.copy())
    freeze_var_for_switch = False


def ctl_load_setup_data_5638():
    setup_mode = bpy.context.scene.ctl_prop_setup_mode
    tool_dict = ctl_read_setup_tool_dict_2974(setup_mode)
    if len(tool_dict) <= 0:
        bpy.ops.ctl.clear_setup_data('INVOKE_DEFAULT', )
    else:
        set_setup_switch_data(setup_mode, tool_dict)


def ctl_save_setup_data_5638():
    setup_mode = bpy.context.scene.ctl_prop_setup_mode
    tool_dict = get_setup_tool_dict(setup_mode)
    ctl_write_setup_tool_dict_8736(setup_mode, tool_dict)


def ctl_write_setup_tool_dict_8736(mode, tool_dict):
    if mode == 'Create' or mode == 'Update':
        file_name = f'tools\\00.setup.00.{mode.lower()}.json'
        set_file_data(file_name, json.dumps(tool_dict, indent = 4))


def ctl_read_setup_tool_dict_2974(mode):
    tool_dict = {}
    if mode == 'Create' or mode == 'Update':
        file_name = f'tools\\00.setup.00.{mode.lower()}.json'
        json_data = get_file_data(file_name)
        try:
            tool_dict = json.loads(json_data)
        except: pass
    return tool_dict


class CTL_UL_display_collection_list_7DA87(bpy.types.UIList):

    def draw_item(self, context, layout, data, file, icon, active_data, active_propname, index_7DA87):
        row = layout
        file_name = file.pointer.name if file.pointer is not None else file.name
        layout.label(text=(file_name if ('' != file_name) else 'No File'), icon_value=(694 if (None != file.pointer) else 2))


_item_map = dict()


def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]


def display_collection_id(uid, vars):
    id = f"coll_{uid}"
    for var in vars.keys():
        if var.startswith("i_"):
            id += f"_{var}_{vars[var]}"
    return id


def print_error(e):
    if hasattr(e, 'message'):
        print('Message :', e.message)
    else:
        print('Error :', e)


class CTL_UL_display_collection_list_F34BC(bpy.types.UIList):

    def draw_item(self, context, layout, data, item_F34BC, icon, active_data, active_propname, index_F34BC):
        row = layout
        layout.label(text=item_F34BC.name, icon_value=string_to_icon(ctl_var_type_icon_7F9BF(item_F34BC.type)))


class CTL_OT_Remove_File_C67B0(bpy.types.Operator):
    bl_idname = "ctl.remove_file_c67b0"
    bl_label = "Remove File"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        file_col = bpy.context.scene.ctl_prop_file_collection
        file_idx = bpy.context.scene.ctl_prop_active_file_index
        if len(file_col) > file_idx:
            file_col.remove(file_idx)
        if ((len(file_col.values()) <= file_idx) and (len(file_col.values()) != 0)):
            file_idx = int(len(file_col.values()) - 1.0)
        bpy.context.scene.ctl_prop_active_file_index = file_idx
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_Move_File_22Dd8(bpy.types.Operator):
    bl_idname = "ctl.move_file_22dd8"
    bl_label = "Move File"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    ctl_is_up: bpy.props.BoolProperty(name='Is Up', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.context.scene.ctl_prop_file_collection.move(bpy.context.scene.ctl_prop_active_file_index, (int(bpy.context.scene.ctl_prop_active_file_index - 1.0) if self.ctl_is_up else int(bpy.context.scene.ctl_prop_active_file_index + 1.0)))
        item_6F64F = bpy.context.scene.ctl_prop_file_collection[(int(bpy.context.scene.ctl_prop_active_file_index - 1.0) if self.ctl_is_up else int(bpy.context.scene.ctl_prop_active_file_index + 1.0))]
        bpy.context.scene.ctl_prop_active_file_index = (int(bpy.context.scene.ctl_prop_active_file_index - 1.0) if self.ctl_is_up else int(bpy.context.scene.ctl_prop_active_file_index + 1.0))
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_Add_File_A05Dc(bpy.types.Operator):
    bl_idname = "ctl.add_file_a05dc"
    bl_label = "Add File"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        item_88A45 = bpy.context.scene.ctl_prop_file_collection.add()
        if (1 < len(bpy.context.scene.ctl_prop_file_collection.values())):
            bpy.context.scene.ctl_prop_file_collection.move(bpy.context.scene.ctl_prop_file_collection.values().index(item_88A45), int(bpy.context.scene.ctl_prop_active_file_index + 1.0))
            item_F9F8A = bpy.context.scene.ctl_prop_file_collection[int(bpy.context.scene.ctl_prop_active_file_index + 1.0)]
            bpy.context.scene.ctl_prop_active_file_index = bpy.context.scene.ctl_prop_file_collection.values().index(item_F9F8A)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_switch_text_in_editor(text):
    if text is not None:

        def get_main_editor():
            editors = []
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
                return main_editor
            return None
        editor = get_main_editor()
        if editor is not None:
            editor.spaces[0].text = text


def ctl_update_ctl_prop_switch_file_live(self, context):
    ctl_switch_file_to_editor_D655A()


def ctl_switch_file_to_editor_D655A():
    if bpy.context.scene.ctl_prop_switch_file_live:
        index = bpy.context.scene.ctl_prop_active_file_index
        scene = bpy.context.scene
        file = scene.ctl_prop_file_collection[index].pointer
        ctl_switch_text_in_editor(file)


# TODO: <--- Custom Interface


def ctl_setup_custom_tool_interface_A85ED(layout, tool):
    layout.separator(factor=1)
    row_U088V = layout.row(heading='', align=True)
    row_U088V.scale_x = 1.2
    row_U088V.scale_y = 1.0
    row_U088V.operator_context = "INVOKE_DEFAULT"
    op = row_U088V.operator('ctl.reload_custom_tool', text='Reload', icon_value=692, emboss=True, depress=False)
    op = row_U088V.operator('ctl.register_custom_tool', text='', icon_value=495, emboss=True, depress=False)
    op = row_U088V.operator('ctl.unregister_custom_tool', text='', icon_value=582, emboss=True, depress=False)


class CTL_OT_RELOAD_CUSTOM_TOOL(bpy.types.Operator):
    bl_idname = "ctl.reload_custom_tool"
    bl_label = "Reload Custom Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.ops.ctl.register_custom_tool('INVOKE_DEFAULT', tool=self.tool)
        bpy.ops.ctl.unregister_custom_tool('INVOKE_DEFAULT', tool=self.tool)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_REGISTER_CUSTOM_TOOL(bpy.types.Operator):
    bl_idname = "ctl.register_custom_tool"
    bl_label = "Register Custom Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def get_test_code_4628():
            code = ''
            for file in bpy.context.scene.ctl_prop_file_collection:
                if code != '':
                    code = code + '\n'
                code = code + file.pointer.as_string()
            return code

        def get_tool_code_8027(tool):
            code = ''
            tool_dict = get_tool_dict_from_tool(tool)
            if tool_dict is not None and 'files' in tool_dict:
                for file_tuple in tool_dict['files']:
                    if isinstance(file_tuple[1], list):
                        file_data = '\n'.join(file_tuple[1])
                        if code != '':
                            code = code + '\n'
                        code = code + file_data
            return code
        # if self.tool != '':
        #     code_3089 = ''
        #     if self.tool == 'test':
        #         code_3089 = get_test_code_4628()
        #     else:
        #         code_3089 = get_tool_code_8027(self.tool)
        #     if code_3089 != '':
        #         global tool_data_9645
        #         if self.tool not in tool_data_9645:
        #             tool_data_9645[self.tool] = {}
        #         tool_code_2962 = f'tool = bpy.context.scene.ctl_{processed_name(self.tool)}\n'
        #         data_code_5680 = f'data = tool_data_9645[self.tool]\n'
        #         code_3089 = tool_code_2962 + data_code_5680 + code_3089
        #         try:
        #             exec(code_3089)
        #         except Exception as e:
        #             print('Run Code :')
        #             print(code_3089)
        #             print('Error: In Tool Run')
        #             print_error(e)
        #             return False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_UNREGISTER_CUSTOM_TOOL(bpy.types.Operator):
    bl_idname = "ctl.unregister_custom_tool"
    bl_label = "UNRegister Custom Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def get_test_code_4628():
            code = ''
            for file in bpy.context.scene.ctl_prop_file_collection:
                if code != '':
                    code = code + '\n'
                code = code + file.pointer.as_string()
            return code

        def get_tool_code_8027(tool):
            code = ''
            tool_dict = get_tool_dict_from_tool(tool)
            if tool_dict is not None and 'files' in tool_dict:
                for file_tuple in tool_dict['files']:
                    if isinstance(file_tuple[1], list):
                        file_data = '\n'.join(file_tuple[1])
                        if code != '':
                            code = code + '\n'
                        code = code + file_data
            return code
        # if self.tool != '':
        #     code_3089 = ''
        #     if self.tool == 'test':
        #         code_3089 = get_test_code_4628()
        #     else:
        #         code_3089 = get_tool_code_8027(self.tool)
        #     if code_3089 != '':
        #         global tool_data_9645
        #         if self.tool not in tool_data_9645:
        #             tool_data_9645[self.tool] = {}
        #         tool_code_2962 = f'tool = bpy.context.scene.ctl_{processed_name(self.tool)}\n'
        #         data_code_5680 = f'data = tool_data_9645[self.tool]\n'
        #         code_3089 = tool_code_2962 + data_code_5680 + code_3089
        #         try:
        #             exec(code_3089)
        #         except Exception as e:
        #             print('Run Code :')
        #             print(code_3089)
        #             print('Error: In Tool Run')
        #             print_error(e)
        #             return False
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


temp_bool_8943 = False
temp_bool_1010 = False
tool_data_9645 = {}


def ctl_setup_simple_tool_interface_A85ED(layout_function, tool_name, has_undo_data):

    def is_mode_active(type):
        is_active = True
        if type == 'Edit Bone' or type == 'Edit Bone Set':
            is_active = bpy.context.mode == 'EDIT_ARMATURE'
        elif type == 'Pose Bone' or type == 'Pose Bone Set':
            is_active = bpy.context.mode == 'POSE'
        return is_active

    def tool_interface(layout, var):
        global temp_bool_8943
        global temp_bool_1010
        temp_bool_8943 = False
        if var['disappear_if'] != '':
            disappear_code = f"global temp_bool_8943\ntemp_bool_8943 = {var['disappear_if']}"
            ctl_run_code_with_args(None, None, tool_name, disappear_code, f'Disappear Code ({tool_name}.{var["name"]})')
        temp_bool_1010 = False
        if var['disable_if'] != '':
            disable_code = f"global temp_bool_1010\ntemp_bool_1010 = {var['disable_if']}"
            ctl_run_code_with_args(None, None, tool_name, disable_code, f'Disable Code ({tool_name}.{var["name"]})')
        if isinstance(temp_bool_8943, bool) and not temp_bool_8943:
            row_40C85 = layout.row(heading='', align=True)
            row_40C85.alert = False
            row_40C85.enabled = not temp_bool_1010 if isinstance(temp_bool_1010, bool) else True
            row_40C85.active = True
            row_40C85.use_property_split = True
            row_40C85.use_property_decorate = False
            row_40C85.scale_x = 1.0
            row_40C85.scale_y = 1.0
            row_40C85.alignment = 'EXPAND'
            row_40C85.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            var_name = var['name']
            prop_name = processed_name(var_name)
            var_type = var['type']
            options = ''
            if var['emboss']:
                options = options + ', emboss=True'
            if var['expand']:
                options = options + ', expand=True'
            if var['slider']:
                options = options + ', slider=True'
            if var['toggle']:
                options = options + ', toggle=True'
            base_path = f'bpy.context.scene.ctl_{processed_name(tool_name)}'
            var_prop = f"prop({base_path}, \"{prop_name}\", text=\"{var_name}\", icon_value=0 {options})"
            # print(var_prop)
            if var_type == 'Edit Bone' or var_type == 'Pose Bone' or var_type == 'Edit Bone Set' or var_type == 'Pose Bone Set':
                row_picker = row_40C85.row(heading='', align=True)
                row_picker.active = is_mode_active(var_type)
                try:
                    code = f"row_picker.{var_prop}"
                    exec(code)
                except Exception as e:
                    print(code)
                    print_error(e)
                picker = row_picker.operator('ctl.pick_selected_27dd5', text='', icon_value=256, emboss=True, depress=False)
                picker.ctl_tool = tool_name
                picker.ctl_type = var_type
                picker.ctl_property = base_path + '.' + prop_name
            else:
                try:
                    code = f"row_40C85.{var_prop}"
                    exec(code)
                except Exception as e:
                    print(code)
                    print_error(e)
            col_0268D.separator(factor=var['separator']) #<--- Separator

    def has_update_file(var):
        file_tuple  = var["update_file"]
        file_name = file_tuple[0]
        if file_name != '':
            return True
        return False
    # TODO Var Interface #####
    layout_function.separator(factor=0.5)
    col_0268D = layout_function.column(heading='', align=False)
    col_0268D.alert = False
    col_0268D.enabled = True
    col_0268D.active = True
    col_0268D.use_property_split = False
    col_0268D.use_property_decorate = False
    col_0268D.scale_x = 1.0
    col_0268D.scale_y = 1.0
    col_0268D.alignment = 'EXPAND'
    col_0268D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    if tool_name not in variables:
        variables[tool_name] = []
    for var in variables[tool_name]:
        if not has_update_file(var):
            tool_interface(col_0268D, var)
    col_0268D.separator(factor=0.2)
    row_C5193 = col_0268D.row(heading='', align=True)
    row_C5193.scale_x = 1.17
    row_C5193.scale_y = 1.05
    op = row_C5193.operator('ctl.run_tool', text='Run Tool', icon_value=495, emboss=True, depress=False)
    op.tool = tool_name
    if has_undo_data:
        op = row_C5193.operator('ctl.run_undo_tool', text='', icon_value=715, emboss=True, depress=False)
        op.tool = tool_name
    col_0268D.separator(factor=1)
    for var in variables[tool_name]:
        if has_update_file(var):
            tool_interface(col_0268D, var)
    if bpy.context.scene.ctl_prop_is_show_done:
        global tool_data_9645
        enable_done = False
        if tool_name in tool_data_9645:
            data = tool_data_9645[tool_name]
            if (isinstance(data, list) or isinstance(data, dict) or isinstance(data, str)) and len(data) > 0:
                enable_done = True
        col = col_0268D.column(heading='', align=False)
        col.active = enable_done
        col.separator(factor=0.2)
        op = col.operator('ctl.clear_data', text='Done', icon_value=0, emboss=True, depress=False)
        op.tool = tool_name


def get_tool_dict_from_tool(tool):
    global global_tool_list
    for group_data in global_tool_list:
        (group_name, tool_data_list) = group_data
        for tool_data in tool_data_list:
            (tool_name, tool_dict) = tool_data
            if tool == tool_name:
                return tool_dict
    return None


class CTL_OT_CLEAR_DATA(bpy.types.Operator):
    bl_idname = "ctl.clear_data"
    bl_label = "Clear Data"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        global tool_data_9645
        if self.tool in tool_data_9645:
            tool_data_9645[self.tool] = {}
        self.report({'INFO'}, message='Data Cleared')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_RUN_TOOL(bpy.types.Operator):
    bl_idname = "ctl.run_tool"
    bl_label = "Run Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def get_test_code_4628():
            code_list = []
            for file in bpy.context.scene.ctl_prop_file_collection:
                has_error = False
                try:
                    name = file.pointer.name
                    length = len(file.pointer.lines)
                    code = file.pointer.as_string()
                except:
                    has_error = True
                if not has_error:
                    code_list.append((name, length, code))
            has_vars = len(bpy.context.scene.ctl_prop_var_collection) > 0
            return (code_list, has_vars)

        def get_tool_code_8027(tool):
            code_list = []
            tool_dict = get_tool_dict_from_tool(tool)
            if tool_dict is not None and 'files' in tool_dict:
                for file_tuple in tool_dict['files']:
                    if isinstance(file_tuple[1], list):
                        name = file_tuple[0]
                        length = len(file_tuple[1])
                        code = '\n'.join(file_tuple[1])
                        code_list.append((name, length, code))
            has_vars = tool_dict is not None and 'variables' in tool_dict and len(tool_dict['variables']) > 0
            return (code_list, has_vars)
        if self.tool != '':
            ctl_save_setup_data_5638()
            code_list_3089 = []
            if self.tool == 'test':
                (code_list_3089, has_vars) = get_test_code_4628()
            else:
                (code_list_3089, has_vars) = get_tool_code_8027(self.tool)
            code_3089 = '\n'.join([item[2] for item in code_list_3089])
            if code_3089 != '':
                ctl_run_code_with_functions(self, context, self.tool, code_3089, f"Running Tool Code ('{self.tool}')", has_vars)
            else:
                self.report({'ERROR'}, message='Code Not Found')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


function_list = []


def ctl_run_code_with_args(self, context, tool_name, main_code, location, need_args=True):
    global tool_data_9645
    if tool_name not in tool_data_9645:
        tool_data_9645[tool_name] = {}
    fn_define_code = ((f'def run_code({("self, context, tool, data, " if need_args else "")}processed_name):\n' + main_code).replace('\n', '\n   ')) + '\n\n'
    tool_code = f'tool = bpy.context.scene.ctl_{processed_name(tool_name)}\n'
    data_code = f'global tool_data_9645\ndata = tool_data_9645["{tool_name}"]\n'
    fn_call_code = f'run_code({("self, context, tool, data, " if need_args else "")}processed_name)'
    code = fn_define_code + (tool_code if need_args else '') + data_code + fn_call_code
    try:
        exec(code)
    except:
        if self is not None:
            self.report({'ERROR'}, message='error-in-code')
        # print('Error in '+ location)
        # print('------- CODE ---------')
        # print(code)
        # print('----------------------')
        traceback.print_exc()


# TODO <--- Run


def ctl_run_code_with_functions(self, context, tool_name, main_code, location, need_tool=True):

    def print_tool_error(e):
        error_text = f"{type(e).__name__}, {e}"
        self.report({"ERROR"}, error_text)

    def get_outer_code():
        file_code = get_file_data('ctl_common_functions.py')
        exp = r"\ndef[ ]+([a-z_|0-9]*)"
        fn_name_list = re.findall(exp, file_code)
        outer_pars = ', '.join(fn_name_list)
        fn_code = file_code + f"\nglobal function_list\n" + f"function_list = [{outer_pars}]"
        ctl_run_code_with_args(self, context, tool_name, fn_code, 'Outter Functions Code', False)
        global function_list
        return (function_list, outer_pars)
    global tool_data_9645
    if tool_name not in tool_data_9645:
        tool_data_9645[tool_name] = {}
    global convert_list_to_enum_list
    inner_args = 'self, context' + (', tool' if need_tool else '') + ', tool_name, data, processed_name, convert_list_to_enum_list'
    inner_pars = inner_args
    (function_list, outer_pars) = get_outer_code()
    outer_args = ', '.join([ f"function_list[{idx}]" for idx in range(len(function_list))])
    arguments = inner_args + ', ' + outer_args
    parameters = inner_pars + ', ' + outer_pars
    fn_define_code = (f'def tool_code({parameters}):\n' + main_code).replace('\n', '\n   ') + '\n\n'
    tool_code = f'tool = bpy.context.scene.ctl_{processed_name(tool_name)}\n'
    data_code = f'global tool_data_9645\ndata = tool_data_9645["{tool_name}"]\n'
    fn_call_code = f'tool_code({arguments})'
    code = fn_define_code + (tool_code if need_tool else '') + data_code + fn_call_code
    try:
        exec(code)
    except Exception as e:
        if self is not None:
            self.report({'ERROR'}, message='error-in-code')
        # print('Error in '+ location)
        # print('------- CODE ---------')
        # print(code)
        # print('----------------------')
        traceback.print_exc()
        # print_tool_error(e)


class CTL_OT_RUN_UNDO_TOOL(bpy.types.Operator):
    bl_idname = "ctl.run_undo_tool"
    bl_label = "Run Undo Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def get_test_code_4628():
            code = ''
            undo_file = bpy.context.scene.ctl_prop_undo_file2
            if undo_file is not None:
                code = undo_file.as_string()
            has_vars = len(bpy.context.scene.ctl_prop_var_collection) > 0
            return (code, has_vars)

        def get_tool_code_8027(tool):
            code = ''
            tool_dict = get_tool_dict_from_tool(tool)
            if tool_dict is not None and 'undo_file' in tool_dict:
                if isinstance(tool_dict['undo_file'], list) and len(tool_dict['undo_file']) == 2:
                    code = tool_dict['undo_file'][1]
            has_vars = tool_dict is not None and 'variables' in tool_dict and len(tool_dict['variables']) > 0
            return ('\n'.join(code), has_vars)
        if self.tool != '':
            code_3089 = ''
            if self.tool == 'test':
                (code_3089, has_vars) = get_test_code_4628()
            else:
                (code_3089, has_vars) = get_tool_code_8027(self.tool)
            if code_3089 != '':
                ctl_run_code_with_functions(self, context, self.tool, code_3089, f'Undo Code ({self.tool})', has_vars)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_setup_file_interface_6650F(layout_function, ):
    layout_function.separator(factor=1.0)
    col_2D080 = layout_function.column(heading='', align=False)
    col_2D080.alert = False
    col_2D080.enabled = True
    col_2D080.active = True
    col_2D080.use_property_split = False
    col_2D080.use_property_decorate = False
    col_2D080.scale_x = 1.0
    col_2D080.scale_y = 1.0
    col_2D080.alignment = 'EXPAND'
    col_2D080.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_7E143 = col_2D080.row(heading='', align=False)
    row_7E143.alert = False
    row_7E143.enabled = True
    row_7E143.active = True
    row_7E143.use_property_split = False
    row_7E143.use_property_decorate = False
    row_7E143.scale_x = 1.0
    row_7E143.scale_y = 1.0
    row_7E143.alignment = 'EXPAND'
    row_7E143.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    col_FFEC7 = row_7E143.column(heading='', align=True)
    col_FFEC7.alert = False
    col_FFEC7.enabled = True
    col_FFEC7.active = True
    col_FFEC7.use_property_split = False
    col_FFEC7.use_property_decorate = False
    col_FFEC7.scale_x = 1.0
    col_FFEC7.scale_y = 1.0
    col_FFEC7.alignment = 'EXPAND'
    col_FFEC7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    coll_id = display_collection_id('7DA87', locals())
    col_FFEC7.template_list('CTL_UL_display_collection_list_7DA87', coll_id, bpy.context.scene, 'ctl_prop_file_collection', bpy.context.scene, 'ctl_prop_active_file_index', rows=0)
    col_D6DCA = row_7E143.column(heading='', align=True)
    col_D6DCA.alert = False
    col_D6DCA.enabled = True
    col_D6DCA.active = True
    col_D6DCA.use_property_split = False
    col_D6DCA.use_property_decorate = False
    col_D6DCA.scale_x = 1.0
    col_D6DCA.scale_y = 1.0
    col_D6DCA.alignment = 'EXPAND'
    col_D6DCA.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = col_D6DCA.operator('ctl.add_file_a05dc', text='', icon_value=31, emboss=True, depress=False)
    op = col_D6DCA.operator('ctl.remove_file_c67b0', text='', icon_value=32, emboss=True, depress=False)
    col_D6DCA.separator(factor=1.0)
    row_CDD3A = col_D6DCA.row(heading='', align=True)
    row_CDD3A.alert = False
    row_CDD3A.enabled = True
    row_CDD3A.active = ctl_move_possibility_68AE7(len(bpy.context.scene.ctl_prop_file_collection.values()), bpy.context.scene.ctl_prop_active_file_index)[0]
    row_CDD3A.use_property_split = False
    row_CDD3A.use_property_decorate = False
    row_CDD3A.scale_x = 1.0
    row_CDD3A.scale_y = 1.0
    row_CDD3A.alignment = 'EXPAND'
    row_CDD3A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = row_CDD3A.operator('ctl.move_file_22dd8', text='', icon_value=7, emboss=True, depress=False)
    op.ctl_is_up = True
    row_58ADC = col_D6DCA.row(heading='', align=True)
    row_58ADC.alert = False
    row_58ADC.enabled = True
    row_58ADC.active = ctl_move_possibility_68AE7(len(bpy.context.scene.ctl_prop_file_collection.values()), bpy.context.scene.ctl_prop_active_file_index)[1]
    row_58ADC.use_property_split = False
    row_58ADC.use_property_decorate = False
    row_58ADC.scale_x = 1.0
    row_58ADC.scale_y = 1.0
    row_58ADC.alignment = 'EXPAND'
    row_58ADC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = row_58ADC.operator('ctl.move_file_22dd8', text='', icon_value=5, emboss=True, depress=False)
    op.ctl_is_up = False
    col_D6DCA.separator(factor=1.0)
    col_D6DCA.prop(bpy.context.scene, 'ctl_prop_switch_file_live', text='', icon_value=256, emboss=True)
    col_2D080.separator(factor=0.5)
    if len(bpy.context.scene.ctl_prop_file_collection) > 0:
        row_OP05H = col_2D080.row(heading='', align=True)
        row_OP05H.alert = False
        row_OP05H.enabled = True
        row_OP05H.active = True
        row_OP05H.use_property_split = False
        row_OP05H.use_property_decorate = False
        row_OP05H.scale_x = 1.0
        row_OP05H.scale_y = 1.0
        row_OP05H.alignment = 'EXPAND'
        row_OP05H.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        file_item = bpy.context.scene.ctl_prop_file_collection[bpy.context.scene.ctl_prop_active_file_index]
        row_OP05H.prop(file_item, 'pointer', text='File ', icon_value=694, emboss=True)
        op = row_OP05H.operator('ctl.load_tool_file', text='', icon_value=707, emboss=True, depress=False)
        op.index = bpy.context.scene.ctl_prop_active_file_index


# FIXME Load Tool File
class CTL_OT_LOAD_TOOL_FILE(bpy.types.Operator):
    bl_idname = "ctl.load_tool_file"
    bl_label = "Load Tool File"
    bl_description = "If file is lost, try loading tool file, stored externally"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty(name='File Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def load_file_from_tool_dict(tool_dict):
            if len(tool_dict) > 0 and "files" in tool_dict and len(tool_dict["files"]) > self.index:
                text_pointer = bpy.context.scene.ctl_prop_file_collection[self.index].pointer
                (text_name, line_list) = tuple(tool_dict['files'][self.index])
                if text_pointer is None:
                    txt = ctl_create_text((create_text_name(text_name), line_list))
                else:
                    txt = ctl_create_text((text_pointer.name, line_list))
                if txt is not None:
                    ctl_switch_text_in_editor(txt)
                    if text_pointer is None:
                        bpy.context.scene.ctl_prop_file_collection[self.index].pointer = txt
                    return True
            return False
        ctl_load_file_with_function(load_file_from_tool_dict)
        return {"FINISHED"}

    def invoke(self, context, event):
        # text_pointer = bpy.context.scene.ctl_prop_undo_file2
        # if text_pointer is not None:
        #     return context.window_manager.invoke_confirm(self, event)
        # else:
        #     return self.execute(context)
        return self.execute(context)


# FIXME <--- enum
class CTL_OT_LOAD_ENUM_FILE(bpy.types.Operator):
    bl_idname = "ctl.load_enum_file"
    bl_label = "Load Enum File"
    bl_description = "If file is lost, try loading tool file, stored externally"
    bl_options = {"REGISTER", "UNDO"}
    id: bpy.props.StringProperty(name='Variable ID', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def load_file_from_tool_dict(tool_dict):
            if len(tool_dict) > 0 and "variables" in tool_dict and len(tool_dict["variables"]) > 0:
                data = ctl_get_var(self.id, 'ctl.load_enum_file')
                text_pointer = data.file
                variable = {}
                for var in tool_dict['variables']:
                    if var['id'] == self.id:
                        variable = var
                        break
                if len(variable) > 0 and 'data' in variable and 'file' in variable['data']:
                    file_item = variable['data']['file']
                    if len(file_item) > 0:
                        (text_name, line_list) = tuple(file_item)
                        if text_pointer is None:
                            txt = ctl_create_text((create_text_name(text_name), line_list))
                        else:
                            txt = ctl_create_text((text_pointer.name, line_list))
                        if txt is not None:
                            ctl_switch_text_in_editor(txt)
                            if text_pointer is None:
                                data.file = txt
                            return True
            return False
        ctl_load_file_with_function(load_file_from_tool_dict)
        return {"FINISHED"}

    def invoke(self, context, event):
        # text_pointer = bpy.context.scene.ctl_prop_undo_file2
        # if text_pointer is not None:
        #     return context.window_manager.invoke_confirm(self, event)
        # else:
        #     return self.execute(context)
        return self.execute(context)


class CTL_OT_LOAD_UPDATE_FILE(bpy.types.Operator):
    bl_idname = "ctl.load_update_file"
    bl_label = "Load Update File"
    bl_description = "If file is lost, try loading tool file, stored externally"
    bl_options = {"REGISTER", "UNDO"}
    id: bpy.props.StringProperty(name='Variable ID', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def load_file_from_tool_dict(tool_dict):
            if len(tool_dict) > 0 and "variables" in tool_dict and len(tool_dict["variables"]) > 0:
                text_pointer = None
                for var_col in context.scene.ctl_prop_var_collection:
                    if var_col.id == self.id:
                        text_pointer = var_col.update_file
                        break
                variable = {}
                for var in tool_dict['variables']:
                    if var['id'] == self.id:
                        variable = var
                        break
                if len(variable) > 0 and 'update_file' in variable:
                    file_item = variable['update_file']
                    if len(file_item) > 0:
                        (text_name, line_list) = tuple(file_item)
                        if text_pointer is None:
                            txt = ctl_create_text((create_text_name(text_name), line_list))
                        else:
                            txt = ctl_create_text((text_pointer.name, line_list))
                        if txt is not None:
                            ctl_switch_text_in_editor(txt)
                            if text_pointer is None:
                                var_col.update_file = txt
                            return True
            return False
        ctl_load_file_with_function(load_file_from_tool_dict)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_SWITCH_FILE_IN_EDITOR(bpy.types.Operator):
    bl_idname = "ctl.switch_file_in_editor"
    bl_label = "Get File in Editor"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty(name='Text Name', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.name != '' and self.name in bpy.data.texts:
            ctl_switch_text_in_editor(bpy.data.texts[self.name])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_get_group_list_3973B(setup_mode):
    group_list = []
    group_list.append('--- Select ---')
    global global_tool_list
    global group_rename
    for group_data in global_tool_list:
        group_name = group_data[0]
        if group_name in group_rename:
            group_list.append(group_rename[group_name])
        else:
            group_list.append(group_name)
    if setup_mode == 'Create':
        group_list.append('New Group')
    if len(group_list) > 0:
        return group_list
    else:
        return ['Not Available']


def ctl_get_tool_list_3973B():
    tool_list = []
    global global_tool_list
    global tool_rename
    group_selected = bpy.context.scene.ctl_prop_group_set
    for group_data in global_tool_list:
        (group_name, tool_data_list) = group_data
        if group_name == group_selected:
            for tool_data in tool_data_list:
                tool_name = tool_data[0]
                if tool_name in tool_rename:
                    tool_list.append(tool_rename[tool_name])
                else:
                    tool_list.append(tool_name)
    if len(tool_list) > 0:
        return tool_list
    else:
        return ['-- Empty --']


# TODO X group set enum list


def convert_list_to_enum_list(item_list):

    def type_enum_tuple(item):
        if (isinstance(item, tuple) or isinstance(item, list)) and len(item) == 2 and isinstance(item[0], str) and (isinstance(item[1], str) or isinstance(item[1], int)):
            return True
        else:
            return False
    new_list = []
    for idx in range(len(item_list)):
        item = item_list[idx]
        item_idx = (1 if idx == 0 else idx*2)
        if isinstance(item, str):
            new_list.append((item, item, '', 0, item_idx))
        elif type_enum_tuple(item):
            name = item[0]
            if isinstance(item[1], str):
                icon = string_to_icon(item[1])
            else:
                icon = item[1]
            new_list.append((name, name, '', icon, item_idx))
    return new_list


def ctl_prop_tool_set_enum_items(self, context):
    item_list = ctl_get_tool_list_3973B()
    return convert_list_to_enum_list(item_list)


def ctl_prop_group_set_items(self, context):
    item_list = ctl_get_group_list_3973B('')
    return convert_list_to_enum_list(item_list)


def ctl_prop_create_group_set_items(self, context):
    item_list = ctl_get_group_list_3973B('Create')
    return convert_list_to_enum_list(item_list)


def ctl_prop_pie_space_enum_items(self, context):
    enum_items = ctl_get_space_list_1DD82()
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def ctl_get_space_list_1DD82():
    enums['ctl_prop_pie_space_list'] = []
    enums['ctl_prop_pie_space_list'].append(['Any Space', 'Any Space', '', 0])
    space_names = None
    space_names = {
        "EMPTY": "Window",
        "VIEW_3D": "3D View",
        "IMAGE_EDITOR": "Image",
        "NODE_EDITOR": "Node Editor",
        "SEQUENCE_EDITOR": "Sequencer",
        "CLIP_EDITOR": "Clip",
        "DOPESHEET_EDITOR": "Dopesheet",
        "GRAPH_EDITOR": "Graph Editor",
        "NLA_EDITOR": "NLA Editor",
        "TEXT_EDITOR": "Text",
        "CONSOLE": "Console",
        "INFO": "Info",
        "OUTLINER": "Outliner",
        "PROPERTIES": "Property Editor",
        "FILE_BROWSER": "File Browser"
    }
    for i_9C288 in range(len(space_names)):
        dict = space_names
        index = i_9C288
        key = None
        value = None
        keys = list(dict.keys())
        key = keys[index]
        value = dict[key]
        enums['ctl_prop_pie_space_list'].append([value, value, '', 0])
    return enums['ctl_prop_pie_space_list']


class CTL_MT_EA721(bpy.types.Menu):
    bl_idname = "CTL_MT_EA721"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.menu_pie()
        col_80CFE = layout.column(heading='', align=False)
        col_80CFE.alert = False
        col_80CFE.enabled = True
        col_80CFE.active = True
        col_80CFE.use_property_split = False
        col_80CFE.use_property_decorate = False
        col_80CFE.scale_x = 1.0
        col_80CFE.scale_y = 1.0
        col_80CFE.alignment = 'EXPAND'
        col_80CFE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_0210A = col_80CFE.row(heading='', align=False)
        row_0210A.alert = False
        row_0210A.enabled = True
        row_0210A.active = True
        row_0210A.use_property_split = False
        row_0210A.use_property_decorate = False
        row_0210A.scale_x = 1.0
        row_0210A.scale_y = 1.0
        row_0210A.alignment = 'EXPAND'
        row_0210A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_0210A.operator('sn.dummy_button_operator', text='My Button', icon_value=0, emboss=True, depress=False)
        op = row_0210A.operator('sn.dummy_button_operator', text='My Button', icon_value=0, emboss=True, depress=False)
        op = col_80CFE.operator('sn.dummy_button_operator', text='My Button', icon_value=0, emboss=True, depress=False)
        op = layout.operator('sn.dummy_button_operator', text='Button 2', icon_value=0, emboss=True, depress=False)
        op = layout.operator('sn.dummy_button_operator', text='Button 3', icon_value=0, emboss=True, depress=False)


is_ctl_registered_9042 = False
class CTL_PT_MAIN_PANEL(bpy.types.Panel):
    bl_label = 'Custom Tools'
    bl_idname = 'CTL_PT_MAIN_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        global is_ctl_registered_9042
        layout = self.layout
        if not is_ctl_registered_9042:
            op = layout.operator('ctl.register_ctl', text='Register CTL', icon_value=0, emboss=True, depress=False)
        else:
            if bpy.context.scene.ctl_prop_isolate_testing_mode:
                col_03669 = layout.column(heading='', align=False)
                col_03669.alert = False
                col_03669.enabled = True
                col_03669.active = True
                col_03669.use_property_split = False
                col_03669.use_property_decorate = False
                col_03669.scale_x = 1.0
                col_03669.scale_y = 1.0
                col_03669.alignment = 'EXPAND'
                col_03669.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                layout_function = col_03669
                ctl_setup_subpanel_interface(layout_function, )
            else:
                col_3FBD3 = layout.column(heading='', align=False)
                col_3FBD3.alert = False
                col_3FBD3.enabled = True
                col_3FBD3.active = True
                col_3FBD3.use_property_split = False
                col_3FBD3.use_property_decorate = False
                col_3FBD3.scale_x = 1.0
                col_3FBD3.scale_y = 1.0
                col_3FBD3.alignment = 'EXPAND'
                col_3FBD3.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_738D2 = col_3FBD3.row(heading='', align=True)
                row_738D2.alert = False
                row_738D2.enabled = True
                row_738D2.active = True
                row_738D2.use_property_split = False
                row_738D2.use_property_decorate = False
                row_738D2.scale_x = 1.2
                row_738D2.scale_y = 1.2
                row_738D2.alignment = 'RIGHT'
                row_738D2.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_738D2.prop(bpy.context.scene, 'ctl_prop_is_rename_mode', text='', icon_value=742, emboss=True)
                row_738D2.prop(bpy.context.scene, 'ctl_prop_is_reorder_mode', text='', icon_value=745, emboss=True)
                row_738D2.prop(bpy.context.scene, 'ctl_prop_is_edit_mode', text='', icon_value=197, emboss=True)
                row_738D2.prop(bpy.context.scene, 'ctl_prop_is_delete_mode', text='', icon_value=21, emboss=True)
                row_738D2.separator(factor=1.0)
                op = row_738D2.operator('ctl.reload_tool_list', text='', icon_value=692, emboss=True, depress=False)
                op = row_738D2.operator('ctl.copy_folder_path', text='', icon_value=598, emboss=True, depress=False)
                if bpy.context.scene.ctl_prop_is_edit_mode:
                    col_3FBD3.separator(factor=0.5)
                    layout_function = col_3FBD3
                    ctl_setup_tool_interface_515DA(layout_function, )
                if bpy.context.scene.ctl_prop_is_reorder_mode:
                    col_3FBD3.separator(factor=0.5)
                    row_7A52B = col_3FBD3.row(heading='', align=True)
                    row_7A52B.alert = False
                    row_7A52B.enabled = True
                    row_7A52B.active = True
                    row_7A52B.use_property_split = False
                    row_7A52B.use_property_decorate = False
                    row_7A52B.scale_x = 1.2
                    row_7A52B.scale_y = 1.0
                    row_7A52B.alignment = 'RIGHT'
                    row_7A52B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    op = row_7A52B.operator('ctl.move_group_or_tool', text='', icon_value=7, emboss=True, depress=False)
                    op.type = 'UP'
                    op = row_7A52B.operator('ctl.move_group_or_tool', text='', icon_value=5, emboss=True, depress=False)
                    op.type = 'DOWN'
                col_3FBD3.separator(factor=0.1)


def ctl_check_duplicate_name_B5648(new_name, item, collection):
    new_name = new_name
    item = item
    collection = collection
    name_changed = None
    need_var_update = None

    def create_name(name, list, o_name = '', count = 1):
        if o_name == '':
            o_name = name
        for item in list:
            if item == name:
                name = o_name + f"_{count:03d}"
                count = count + 1
                name = create_name(name, list, o_name, count)
                break
        return name

    def update_name(new_name):
        if new_name == '':
            if item.name == '':
                new_name = 'Variable'
            else:
                new_name = item.name
        names = [var.name for var in collection if not (var == item)]
        new_name = create_name(new_name, names)
        # print(new_name, '<--- Name Final')
        # print('')
        item.name = new_name
    name_changed = False
    is_freezed = variables['ctl_freeze_check']
    if not is_freezed:
        update_name(new_name)
        name_changed = True
    else:
        variables['ctl_freeze_check'] = False
    need_var_update = new_name != '' and name_changed
    return [name_changed, need_var_update]


# TODO Setup Tools


def ctl_setup_tool_interface_515DA(layout_function, ):
    box_ACEA2 = layout_function.box()
    box_ACEA2.alert = False
    box_ACEA2.enabled = True
    box_ACEA2.active = True
    box_ACEA2.use_property_split = False
    box_ACEA2.use_property_decorate = False
    box_ACEA2.alignment = 'EXPAND'
    box_ACEA2.scale_x = 1.0
    box_ACEA2.scale_y = 1.0
    box_ACEA2.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_E8474 = box_ACEA2.row(heading='', align=True)
    row_E8474.alert = False
    row_E8474.enabled = True
    row_E8474.active = True
    row_E8474.use_property_split = False
    row_E8474.use_property_decorate = False
    row_E8474.scale_x = 1.0
    row_E8474.scale_y = 1.0
    row_E8474.alignment = 'EXPAND'
    row_E8474.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_E8474.prop(bpy.context.scene, 'ctl_prop_setup_is_open', text='', icon_value=(46 if bpy.context.scene.ctl_prop_setup_is_open else 28), emboss=False)
    row_E8474.label(text='Setup', icon_value=0)
    if bpy.context.scene.ctl_prop_setup_is_open:
        row_HI046 = row_E8474.row(heading='', align=True)
        row_HI046.scale_x = 0.85
        row_HI046.scale_y = 1.0
        row_HI046.alignment = 'RIGHT'
        row_HI046.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_OU900 = row_HI046.row(heading='', align=True)
        row_OU900.scale_x = 1.2
        row_OU900.scale_y = 1.0
        is_update = bpy.context.scene.ctl_prop_setup_mode == 'Update'
        row_OU900.prop(bpy.context.scene, 'ctl_prop_setup_keep_file', text='', icon_value=103, emboss=True, toggle=False)
        op = row_HI046.operator('ctl.clear_setup_data', text='Clear', icon_value=0, emboss=True, depress=False)
        op.clear_files = True
        op.clear_update = is_update
        op.clear_create = not is_update
    if bpy.context.scene.ctl_prop_setup_is_open:
        col_836D9 = box_ACEA2.column(heading='', align=False)
        col_836D9.alert = False
        col_836D9.enabled = True
        col_836D9.active = True
        col_836D9.use_property_split = False
        col_836D9.use_property_decorate = False
        col_836D9.scale_x = 1.0
        col_836D9.scale_y = 1.0
        col_836D9.alignment = 'EXPAND'
        col_836D9.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_C90C9 = col_836D9.row(heading='', align=False)
        row_C90C9.alert = False
        row_C90C9.enabled = True
        row_C90C9.active = True
        row_C90C9.use_property_split = False
        row_C90C9.use_property_decorate = False
        row_C90C9.scale_x = 1.0
        row_C90C9.scale_y = 1.0
        row_C90C9.alignment = 'EXPAND'
        row_C90C9.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_C90C9.prop(bpy.context.scene, 'ctl_prop_setup_mode', text='Mode', icon_value=0, emboss=True, expand=True)
        col_836D9.separator(factor=0.5)
        col_3F9AD = col_836D9.column(heading='', align=False)
        col_3F9AD.alert = False
        col_3F9AD.enabled = True
        col_3F9AD.active = True
        col_3F9AD.use_property_split = True
        col_3F9AD.use_property_decorate = False
        col_3F9AD.scale_x = 1.0
        col_3F9AD.scale_y = 1.0
        col_3F9AD.alignment = 'EXPAND'
        col_3F9AD.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        if bpy.context.scene.ctl_prop_setup_mode == "Create":
            col_3F9AD.prop(bpy.context.scene, 'ctl_prop_create_group_set', text='Group', icon_value=0, emboss=True)
            if bpy.context.scene.ctl_prop_create_group_set.upper() == 'NEW GROUP':
                col_3F9AD.prop(bpy.context.scene, 'ctl_prop_new_group', text='Group Name', icon_value=0, emboss=True)
            col_3F9AD.prop(bpy.context.scene, 'ctl_prop_new_tool', text='Tool Name', icon_value=0, emboss=True)
        elif bpy.context.scene.ctl_prop_setup_mode == "Update":
            col_3F9AD.prop(bpy.context.scene, 'ctl_prop_group_set', text='Group', icon_value=0, emboss=True)
            col_3F9AD.prop(bpy.context.scene, 'ctl_prop_tool_set', text='Tool', icon_value=0, emboss=True)
        col_3F9AD.prop(bpy.context.scene, 'ctl_prop_tool_description', text='Description', icon_value=0, emboss=True)
        col_3F9AD.separator(factor=0.4)
        col_3F9AD.prop(bpy.context.scene, 'ctl_prop_tool_type', text='Tool Type', icon_value=0, emboss=True, expand=True)
        layout_function = col_3F9AD
        ctl_setup_subpanel_interface(layout_function, )
        col_836D9.separator(factor=1.0)
        col_5A4B8 = col_836D9.column(heading='', align=False)
        col_5A4B8.alert = False
        col_5A4B8.enabled = True
        col_5A4B8.active = True
        col_5A4B8.use_property_split = True
        col_5A4B8.use_property_decorate = False
        col_5A4B8.scale_x = 1.05
        col_5A4B8.scale_y = 1.05
        col_5A4B8.alignment = 'EXPAND'
        col_5A4B8.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        mode = bpy.context.scene.ctl_prop_setup_mode
        btn_name = mode + ' Tool'
        btn_icon = 31 if mode == 'Create' else 36
        op = col_5A4B8.operator('ctl.create_tool_28cc0', text=btn_name, icon_value=btn_icon, emboss=True, depress=False)


# TODO Testing Interface


def ctl_setup_subpanel_interface(layout_function, ):
    if bpy.context.scene.ctl_prop_tool_type == "CUSTOM":
        layout_function.separator(factor=0.5)
    elif bpy.context.scene.ctl_prop_tool_type == "SIMPLE":
        layout_function.separator(factor=0.15)
        layout_function = layout_function
        ctl_pie_menu_options_AABE5(layout_function, )
        layout_function.separator(factor=0.5)
        col_E7D00 = layout_function.column(heading='', align=False)
        col_E7D00.alert = False
        col_E7D00.enabled = True
        col_E7D00.active = True
        col_E7D00.use_property_split = False
        col_E7D00.use_property_decorate = False
        col_E7D00.scale_x = 1.0
        col_E7D00.scale_y = 1.0
        col_E7D00.alignment = 'EXPAND'
        col_E7D00.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        box_2D12B = col_E7D00.box()
        box_2D12B.alert = False
        box_2D12B.enabled = True
        box_2D12B.active = True
        box_2D12B.use_property_split = False
        box_2D12B.use_property_decorate = False
        box_2D12B.alignment = 'EXPAND'
        box_2D12B.scale_x = 1.0
        box_2D12B.scale_y = 1.0
        box_2D12B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_6E74B = box_2D12B.column(heading='', align=False)
        col_6E74B.alert = False
        col_6E74B.enabled = True
        col_6E74B.active = True
        col_6E74B.use_property_split = False
        col_6E74B.use_property_decorate = False
        col_6E74B.scale_x = 1.0
        col_6E74B.scale_y = 1.0
        col_6E74B.alignment = 'EXPAND'
        col_6E74B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_8621B = col_6E74B.row(heading='', align=True)
        row_8621B.alert = False
        row_8621B.enabled = True
        row_8621B.active = True
        row_8621B.use_property_split = False
        row_8621B.use_property_decorate = False
        row_8621B.scale_x = 1.0
        row_8621B.scale_y = 1.0
        row_8621B.alignment = 'EXPAND'
        row_8621B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_8621B.prop(bpy.context.scene, 'ctl_prop_var_is_open', text='', icon_value=(46 if bpy.context.scene.ctl_prop_var_is_open else 28), emboss=False)
        row_8621B.label(text='Variables', icon_value=0)
        row_6B48B = row_8621B.row(heading='', align=False)
        row_6B48B.alert = False
        row_6B48B.enabled = True
        row_6B48B.active = True
        row_6B48B.use_property_split = False
        row_6B48B.use_property_decorate = False
        row_6B48B.scale_x = 1.0
        row_6B48B.scale_y = 1.0
        row_6B48B.alignment = 'RIGHT'
        row_6B48B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_6B48B.operator('ctl.reload_enum_file', text='', icon_value=692, emboss=True, depress=False)
        # row_6B48B.separator(factor=1.0)
        op = row_6B48B.operator('sn.dummy_button_operator', text=str(len(bpy.context.scene.ctl_prop_var_collection.values())), icon_value=0, emboss=True, depress=False)
        if bpy.context.scene.ctl_prop_var_is_open:
            ctl_variables_interface_86A99(col_6E74B, )
    col_C4014 = layout_function.column(heading='', align=False)
    col_C4014.alert = False
    col_C4014.enabled = True
    col_C4014.active = True
    col_C4014.use_property_split = False
    col_C4014.use_property_decorate = False
    col_C4014.scale_x = 1.0
    col_C4014.scale_y = 1.0
    col_C4014.alignment = 'EXPAND'
    col_C4014.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    box_6AD39 = col_C4014.box()
    box_6AD39.alert = False
    box_6AD39.enabled = True
    box_6AD39.active = True
    box_6AD39.use_property_split = False
    box_6AD39.use_property_decorate = False
    box_6AD39.alignment = 'EXPAND'
    box_6AD39.scale_x = 1.0
    box_6AD39.scale_y = 1.0
    box_6AD39.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    col_67171 = box_6AD39.column(heading='', align=False)
    col_67171.alert = False
    col_67171.enabled = True
    col_67171.active = True
    col_67171.use_property_split = False
    col_67171.use_property_decorate = False
    col_67171.scale_x = 1.0
    col_67171.scale_y = 1.0
    col_67171.alignment = 'EXPAND'
    col_67171.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_B1722 = col_67171.row(heading='', align=True)
    row_B1722.alert = False
    row_B1722.enabled = True
    row_B1722.active = True
    row_B1722.use_property_split = False
    row_B1722.use_property_decorate = False
    row_B1722.scale_x = 1.0
    row_B1722.scale_y = 1.0
    row_B1722.alignment = 'EXPAND'
    row_B1722.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_B1722.prop(bpy.context.scene, 'ctl_prop_file_is_open', text='', icon_value=(46 if bpy.context.scene.ctl_prop_file_is_open else 28), emboss=False)
    row_B1722.label(text='Code Files', icon_value=0)
    row_B1722.prop(bpy.context.scene, 'ctl_prop_isolate_testing_mode', text='', icon_value=254, emboss=True)
    op = row_B1722.operator('ctl.load_all_tool_files', text='', icon_value=707, emboss=True, depress=False)
    # row_B1722.prop(bpy.context.scene, 'ctl_prop_setup_keep_file', text='', icon_value=103, emboss=True)
    row_B1722.separator(factor=1.0)
    row_12195 = row_B1722.row(heading='', align=False)
    row_12195.alert = False
    row_12195.enabled = True
    row_12195.active = True
    row_12195.use_property_split = False
    row_12195.use_property_decorate = False
    row_12195.scale_x = 1.0
    row_12195.scale_y = 1.0
    row_12195.alignment = 'RIGHT'
    row_12195.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = row_12195.operator('sn.dummy_button_operator', text=str(len(bpy.context.scene.ctl_prop_file_collection.values())), icon_value=0, emboss=True, depress=False)
    if bpy.context.scene.ctl_prop_file_is_open:
        ctl_setup_file_interface_6650F(col_67171, )
    box_96DD5 = col_C4014.box()
    box_96DD5.alert = False
    box_96DD5.enabled = True
    box_96DD5.active = True
    box_96DD5.use_property_split = False
    box_96DD5.use_property_decorate = False
    box_96DD5.alignment = 'EXPAND'
    box_96DD5.scale_x = 1.0
    box_96DD5.scale_y = 1.0
    box_96DD5.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    col_B2A12 = box_96DD5.column(heading='', align=False)
    col_B2A12.alert = False
    col_B2A12.enabled = True
    col_B2A12.active = True
    col_B2A12.use_property_split = False
    col_B2A12.use_property_decorate = False
    col_B2A12.scale_x = 1.0
    col_B2A12.scale_y = 1.0
    col_B2A12.alignment = 'EXPAND'
    col_B2A12.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_AD0F1 = col_B2A12.row(heading='', align=True)
    row_AD0F1.alert = False
    row_AD0F1.enabled = True
    row_AD0F1.active = True
    row_AD0F1.use_property_split = False
    row_AD0F1.use_property_decorate = False
    row_AD0F1.scale_x = 1.0
    row_AD0F1.scale_y = 1.0
    row_AD0F1.alignment = 'EXPAND'
    row_AD0F1.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_AD0F1.prop(bpy.context.scene, 'ctl_prop_testing_is_open', text='', icon_value=(46 if bpy.context.scene.ctl_prop_testing_is_open else 28), emboss=False)
    row_AD0F1.label(text='Testing Tool', icon_value=0)
    layout_function = row_AD0F1
    is_testing_open = bpy.context.scene.ctl_prop_testing_is_open
    if bpy.context.scene.ctl_prop_tool_type == "SIMPLE":
        ctl_tool_header_CA842(is_testing_open, layout_function, 'test')
    if is_testing_open:
        if bpy.context.scene.ctl_prop_tool_type == "SIMPLE":
            has_undo_data = bpy.context.scene.ctl_prop_undo_file2 is not None
            ctl_setup_simple_tool_interface_A85ED(col_B2A12, 'test', has_undo_data)
        elif bpy.context.scene.ctl_prop_tool_type == "CUSTOM":
            ctl_setup_custom_tool_interface_A85ED(col_B2A12, 'test')


def ctl_pie_menu_options_AABE5(layout_function, ):
    if not bpy.context.scene.ctl_prop_isolate_testing_mode:
        layout_function.prop(bpy.context.scene, 'ctl_prop_pie_enabled', text='Add to Pie', icon_value=0, emboss=True)
        if bpy.context.scene.ctl_prop_pie_enabled:
            layout_function.prop(bpy.context.scene, 'ctl_prop_tool_icon', text='Icon', icon_value=0, emboss=True)
            layout_function.prop(bpy.context.scene, 'ctl_prop_pie_space', text='Space', icon_value=0, emboss=True)
            layout_function.separator(factor=0.5)
    row_OP05H = layout_function.row(heading='', align=True)
    row_OP05H.alert = False
    row_OP05H.enabled = True
    row_OP05H.active = True
    row_OP05H.use_property_split = True
    row_OP05H.use_property_decorate = False
    row_OP05H.scale_x = 1.0
    row_OP05H.scale_y = 1.0
    row_OP05H.alignment = 'EXPAND'
    row_OP05H.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_OP05H.prop(bpy.context.scene, 'ctl_prop_undo_file2', text='Undo File', icon_value=694, emboss=True)
    op = row_OP05H.operator('ctl.load_undo_file', text='', icon_value=707, emboss=True, depress=False)
    layout_function.prop(bpy.context.scene, 'ctl_prop_is_show_done', text='Show Done Button', icon_value=0, emboss=True)


# FIXME Load UNDO File
class CTL_OT_LOAD_UNDO_FILE(bpy.types.Operator):
    bl_idname = "ctl.load_undo_file"
    bl_label = "Load Undo File"
    bl_description = "Try Loading Undo File Stored Externally"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def load_file_from_tool_dict(tool_dict):
            if len(tool_dict) > 0 and "undo_file" in tool_dict:
                (text_name, line_list) = tuple(tool_dict['undo_file'])
                text_pointer = bpy.context.scene.ctl_prop_undo_file2
                if text_pointer is None:
                    txt = ctl_create_text((create_text_name(text_name), line_list))
                else:
                    txt = ctl_create_text((text_pointer.name, line_list))
                if txt is not None:
                    ctl_switch_text_in_editor(txt)
                    if text_pointer is None:
                        bpy.context.scene.ctl_prop_undo_file2 = txt
                    return True
            return False
        ctl_load_file_with_function(load_file_from_tool_dict)
        return {"FINISHED"}

    def invoke(self, context, event):
        text_pointer = bpy.context.scene.ctl_prop_undo_file2
        if text_pointer is not None:
            return context.window_manager.invoke_confirm(self, event)
        else:
            return self.execute(context)


def ctl_load_file_with_function(load_file_from_tool_dict):

    def load_from_temp(setup_mode):
        file_name = f'tools\\00.setup.00.{setup_mode.lower()}.json'
        json_data = get_file_data(file_name)
        if json_data != '':
            tool_dict = {}
            try:
                tool_dict = json.loads(json_data)
            except:
                return False
            return load_file_from_tool_dict(tool_dict)
        return False

    def load_from_tool(group, tool):
        if isinstance(group, str) and  isinstance(tool, str) and group != '' and tool != '':
            file_name = 'tools\\' + get_tool_file_name(group, tool)
            json_data = get_file_data(file_name)
            if json_data != '':
                tool_dict = {}
                try:
                    tool_dict = json.loads(json_data)
                except:
                    return False
                return load_file_from_tool_dict(tool_dict)
            return False
    if bpy.context.scene.ctl_prop_setup_mode.lower() == 'update':
        group_name = bpy.context.scene.ctl_prop_group_set
        tool_name = bpy.context.scene.ctl_prop_tool_set
        if tool_name.replace('-', '').replace(' ', '').lower() != 'empty':
            is_done = load_from_temp('Update')
            if not is_done:
                print('Info : Reading File From Tool...')
                load_from_tool(group_name, tool_name)
        else:
            print('Error : Tool is not selected...')
    elif bpy.context.scene.ctl_prop_setup_mode.lower() == 'create':
        load_from_temp('Create')


def get_tool_file_name(group, tool):
    tool_file = ''
    group_p = processed_name(group)
    tool_p = processed_name(tool)
    file_list = get_file_list_from_tools_dir()
    for file_name in file_list:
        flist = file_name.split('.')
        if flist[1] == group_p and flist[3] == tool_p:
            tool_file = file_name
            break
    return tool_file


def create_text_name(new_name):

    def extract_old_name(name):
        if name.lower().startswith("ctl-"):
            word_list = name.split(' ')
            word_list.pop(0)
            return ' '.join(word_list)
        else:
            return ''

    def create_name(name, list, o_name = '', count = 1):
        if o_name == '':
            o_name = name
        for item in list:
            if item == name:
                name = f"CTL-{count} " + o_name
                count = count + 1
                name = create_name(name, list, o_name, count)
                break
        return name
    if new_name == '':
        new_name = 'text'
    names = [txt.name for txt in bpy.data.texts]
    old_name = extract_old_name(new_name)
    new_name = create_name(new_name, names)
    return new_name


class CTL_OT_LOAD_ALL_TOOL_FILES(bpy.types.Operator):
    bl_idname = "ctl.load_all_tool_files"
    bl_label = "Load All Files"
    bl_description = "Try Loading All Files Stored Externally"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        is_mode_update = bpy.context.scene.ctl_prop_setup_mode == 'Update'
        file_collection = bpy.context.scene.ctl_prop_file_collection

        def load_file_from_tool_dict(tool_dict):
            if len(tool_dict) > 0 and "files" in tool_dict and len(tool_dict["files"]) == len(file_collection):
                is_okay = True
                for text_index in range(len(file_collection)):
                    text_pointer = file_collection[text_index].pointer
                    (text_name, line_list) = tuple(tool_dict['files'][text_index])
                    if text_pointer is None:
                        txt = ctl_create_text((create_text_name(text_name), line_list))
                    else:
                        txt = ctl_create_text((text_pointer.name, line_list))
                    if txt is not None:
                        ctl_switch_text_in_editor(txt)
                        if text_pointer is None:
                            bpy.context.scene.ctl_prop_file_collection[text_index].pointer = txt
                        continue
                    is_okay = False
                    if is_mode_update:
                        break
                return is_okay
            return False
        ctl_load_file_with_function(load_file_from_tool_dict)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_create_text(ctl_text):
    if isinstance(ctl_text, tuple) and isinstance(ctl_text[0], str) and ctl_text[0] != '' and isinstance(ctl_text[1], list) and len(ctl_text) > 0:
        (text_name, line_list) = tuple(ctl_text)
        text_data =  '\n'.join(line_list)
        if text_data != '':
            if text_name not in bpy.data.texts:
                new_text = bpy.data.texts.new(text_name)
            else:
                new_text = bpy.data.texts[text_name]
                new_text.clear()
            new_text.write(text_data)
            return new_text
    return None


def ctl_update_variable_from_property(self, context):
    ctl_update_variable_3BA34('')


freeze_var_for_switch = False
# TODO Var Update


def ctl_update_variable_3BA34(tool):
    if tool == '':
        tool = 'test'
    global freeze_var_for_switch
    if not freeze_var_for_switch:
        freeze_var_for_switch = True
        # FIXME add unregister code
        ctl_recalculate_vaiables_list(tool)
        ctl_register_tool_variables(tool)
        freeze_var_for_switch = False


class CTL_OT_REGISTER_CTL(bpy.types.Operator):
    bl_idname = "ctl.register_ctl"
    bl_label = "Register CTL Addon"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        global is_ctl_registered_9042
        register_ctl()
        is_ctl_registered_9042 = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_RELOAD_TOOL_LIST(bpy.types.Operator):
    bl_idname = "ctl.reload_tool_list"
    bl_label = "Reload Tool List"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        global global_tool_list
        temp_tool_list = create_tool_list()
        ctl_unregister_tool_list()
        global_tool_list = temp_tool_list
        ctl_register_tool_list()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def copy_to_clip(txt):
    cmd='echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)


class CTL_OT_COPY_FOLDER_PATH(bpy.types.Operator):
    bl_idname = "ctl.copy_folder_path"
    bl_label = "Copy Folder Path"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        path = get_ctl_path()
        copy_to_clip(path)
        print('Path :', path)
        self.report({'INFO'}, 'Path Copied')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# class CTL_OT_COPY_VAR_PROP(bpy.types.Operator):
#     bl_idname = "ctl.copy_var_prop"
#     bl_label = "Copy Var Property"
#     bl_description = ""
#     bl_options = {"REGISTER", "UNDO"}
#     @classmethod
#     def poll(cls, context):
#         return not False
#     def execute(self, context):
#         copy_to_clip(get_ctl_path())
#         return {"FINISHED"}
#     def invoke(self, context, event):
#         return self.execute(context)
class CTL_OT_MOVE_GROUP_OR_TOOL(bpy.types.Operator):
    bl_idname = "ctl.move_group_or_tool"
    bl_label = "Move Group or Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    is_selected = False
    type: bpy.props.StringProperty(name='type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        type = self.type

        def get_is_selected(name, is_tool=False):
            if not is_tool:
                code = f'self.is_selected = bpy.context.scene.ctl_group_{processed_name(name)}.is_selected'
            else:
                code = f'self.is_selected = bpy.context.scene.ctl_tool_{processed_name(name)}.is_selected'
            exec(code)
            return self.is_selected

        def move_group_to_index(from_index, to_index):
            if from_index != to_index:
                (group_name, tool_data_list) = global_tool_list[to_index]
                if not get_is_selected(group_name):
                    item = global_tool_list.pop(from_index)
                    global_tool_list.insert(to_index, item)
                    write_tool_order_to_file()
                    bpy.ops.ctl.reload_tool_list('INVOKE_DEFAULT', )

        def move_tool_to_index(from_tool, to_tool):
            (from_group_index, from_tool_index) = from_tool
            (to_group_index, to_tool_index) = to_tool
            (from_group_name, from_tool_data_list) = global_tool_list[from_group_index]
            item = from_tool_data_list.pop(from_tool_index)
            (group_name, tool_data_list) = global_tool_list[to_group_index]
            if to_tool_index == -1 :
                to_tool_index = len(tool_data_list)
            tool_data_list.insert(to_tool_index, item)
            if len(from_tool_data_list) == 0:
                # print('poping group :', from_group_name)
                unregister_sub_panel(from_group_name)
                global_tool_list.pop(from_group_index)
        global global_tool_list
        is_group = get_is_any_group_selected()
        # print('Moveing Group....', type)
        if is_group:
            if type == 'UP':
                for group_idx in range(len(global_tool_list)):
                    (group_name, tool_data_list) = global_tool_list[group_idx]
                    if get_is_selected(group_name):
                        to_index = (group_idx - 1 if group_idx > 0 else 0)
                        move_group_to_index(group_idx, to_index)
            elif type == 'DOWN':
                tool_list_len = len(global_tool_list)
                for group_idx in range(tool_list_len - 1, -1, -1):
                    (group_name, tool_data_list) = global_tool_list[group_idx]
                    if get_is_selected(group_name): # 0 - 9
                        to_index = (group_idx + 1 if group_idx < (tool_list_len - 1) else (tool_list_len - 1))
                        move_group_to_index(group_idx, to_index)
        else:
            if type == 'UP':
                for group_idx in range(len(global_tool_list)):
                    (group_name, tool_data_list) = global_tool_list[group_idx]
                    tool_idx = 0
                    while tool_idx < len(tool_data_list):
                        (tool_name, tool_data) = tool_data_list[tool_idx]
                        if get_is_selected(tool_name, True):
                            to_group_index = -1
                            to_tool_index = -1
                            is_move = True
                            if tool_idx > 0:
                                to_group_index = group_idx
                                to_tool_index = tool_idx - 1
                            elif tool_idx == 0 and group_idx > 0:
                                to_group_index = group_idx - 1
                                tool_removed = True
                            else:
                                is_move = False
                            if is_move:
                                from_tool = (group_idx, tool_idx)
                                to_tool = (to_group_index, to_tool_index)
                                move_tool_to_index(from_tool, to_tool)
                        if len(tool_data_list) == 0:
                            break
                        (new_tool_name, tool_data) = tool_data_list[tool_idx]
                        if new_tool_name == tool_name:
                            tool_idx = tool_idx + 1
            elif type == 'DOWN':
                group_len = len(global_tool_list)
                for group_idx in range(group_len - 1, -1, -1):
                    (group_name, tool_data_list) = global_tool_list[group_idx]
                    tool_len = len(tool_data_list)
                    last_group_idx = group_len - 1
                    for tool_idx in range(tool_len - 1, -1, -1):
                        (tool_name, tool_data) = tool_data_list[tool_idx]
                        if get_is_selected(tool_name, True):
                            to_group_index = -1
                            to_tool_index = -1
                            last_tool_idx = (len(tool_data_list) - 1)
                            is_move = True
                            if tool_idx < last_tool_idx:
                                to_group_index = group_idx
                                to_tool_index = tool_idx + 1
                            elif tool_idx == last_tool_idx and group_idx < last_group_idx:
                                to_group_index = group_idx + 1
                                to_tool_index = 0
                            else:
                                is_move = False
                            if is_move:
                                from_tool = (group_idx, tool_idx)
                                to_tool = (to_group_index, to_tool_index)
                                move_tool_to_index(from_tool, to_tool)
                        if len(tool_data_list) == 0:
                            break
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_EDIT_TOOL(bpy.types.Operator):
    bl_idname = "ctl.edit_tool"
    bl_label = "Edit Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.StringProperty(name='Group', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        scene = bpy.context.scene
        group_set = ctl_get_group_list_3973B('')
        if len(group_set) > 0 and self.group in group_set:
            scene.ctl_prop_group_set = self.group
            tool_set = ctl_get_tool_list_3973B()
            if len(tool_set) > 0 and self.tool in tool_set:
                scene.ctl_prop_tool_set = self.tool
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# TODO <--- remove tool
class CTL_OT_REMOVE_TOOL(bpy.types.Operator):
    bl_idname = "ctl.remove_tool"
    bl_label = "Remove Tool"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    # tool = ''
    tool: bpy.props.StringProperty(name='tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def move_file_to_bin(file_name):
            if file_name != '':
                ctl_path = get_ctl_path()
                from_path = ctl_path + '\\tools\\' + file_name
                to_path = ctl_path + '\\recycle_bin\\' + file_name
                bin_path = ctl_path + '\\recycle_bin'
                if not os.path.exists(bin_path):
                    os.mkdir(bin_path)
                print('tool-to-bin :', bin_path)
                os.replace(from_path, to_path)

        def remove_tool(group, tool):
            tool_processed = processed_name(tool)
            prop_name = 'ctl_tool_' + tool_processed
            ctl_unregister_property(prop_name)
            move_file_to_bin(get_tool_file_name(group, tool))
        global global_tool_list
        for group_idx in range(len(global_tool_list)):
            (group_name, tool_data_list) = global_tool_list[group_idx]
            is_found = False
            found_idx = -1
            has_other_tools = False
            for tool_idx in range(len(tool_data_list)):
                (tool_name, tool_dict) = tool_data_list[tool_idx]
                if tool_name == self.tool:
                    is_found = True
                    found_idx = tool_idx
                    remove_tool(group_name, tool_name)
                else:
                    has_other_tools = True
            if is_found:
                tool_data_list.pop(found_idx)
                if not has_other_tools:
                    unregister_sub_panel(group_name)
                break
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class CTL_OT_RELOAD_ENUM_FILE(bpy.types.Operator):
    bl_idname = "ctl.reload_enum_file"
    bl_label = "Reload Enum File"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    # tool = ''
    # id: bpy.props.StringProperty(name='ID', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        ctl_update_variable_3BA34('test')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_tool_header_CA842(is_open, layout, tool):
    row_F9E7D = layout.row(heading='', align=False)
    row_F9E7D.scale_x = 0.95
    row_F9E7D.alignment = 'RIGHT'
    row_F9E7D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    if is_open:
        op = row_F9E7D.operator('ctl.clear_tool_fields', text='Clear', icon_value=0, emboss=True, depress=False)
        op.tool = tool
    else:
        op = row_F9E7D.operator('ctl.run_tool', text='Run', icon_value=495, emboss=True, depress=False)
        op.tool = tool


# TODO <---------------clear
class CTL_OT_CLEAR_TOOL_FIELDS(bpy.types.Operator):
    bl_idname = "ctl.clear_tool_fields"
    bl_label = "Clear Tool Fields"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    # tool = ''
    tool: bpy.props.StringProperty(name='Tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.tool != '':
            tool_name = 'ctl_' + processed_name(self.tool)
            tool_prop = f'bpy.context.scene.{tool_name}'
            if self.tool in variables:
                for var in variables[self.tool]:
                    ctl_clear_values_9846(tool_prop, var)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_clear_values_9846(tool_prop, var):

    def run_code(code):
        try:
            exec(code)
        except: pass
    if 'name' in var and 'type' in var:
        var_name = var['name']
        var_name_p = processed_name(var_name)
        type = var['type']
        if 'data' in var:
            if type == 'String' or type == 'Edit Bone' or type == 'Pose Bone' or type == 'Edit Bone Set' or type == 'Pose Bone Set':
                run_code(f"{tool_prop}.{var_name_p} = '{var['data']['default']}'")
            elif type == 'Boolean':
                run_code(f"{tool_prop}.{var_name_p} = {var['data']['default']}")
            elif type == 'Integer':
                run_code(f"{tool_prop}.{var_name_p} = {var['data']['default']}")
            elif type == 'Float':
                run_code(f"{tool_prop}.{var_name_p} = {var['data']['default']}")
            # elif type == 'Enum': # TODO <--- enum interface
                # item_list = get_enum_list(var)
                # print('item list :', item_list)
            elif type == 'Pointer':
                run_code(f"{tool_prop}.{var_name_p} = None")


# if data.is_dynamic and data.file is not None:


def get_file_tuple(file):
    if file is not None:
        data_lines = []
        for line in file.lines:
            data_lines.append(line.body)
        return (file.name, data_lines)
    else:
        return ('', '')


def get_setup_tool_dict(setup_mode, add_group_tool = True):
    scene = bpy.context.scene

    def get_file_list():
        file_list = []
        file_collection = scene.ctl_prop_file_collection
        for file in file_collection:
            file_list.append(get_file_tuple(file.pointer))
        return file_list
    tool_dict = {}
    if add_group_tool:
        if setup_mode == 'Create':
            tool_dict = {
                'group': (scene.ctl_prop_create_group_set if scene.ctl_prop_create_group_set.upper() != 'NEW GROUP' else scene.ctl_prop_new_group),
                'tool': scene.ctl_prop_new_tool,
            }
        elif setup_mode == 'Update':
            tool_dict = {
                'group': scene.ctl_prop_group_set,
                'tool': scene.ctl_prop_tool_set,
            }
    tool_dict.update({
        'description': scene.ctl_prop_tool_description,
        'type' : scene.ctl_prop_tool_type,
        'pie' : {
            'enabled' : scene.ctl_prop_pie_enabled,
            'icon' : scene.ctl_prop_tool_icon,
            'space' : scene.ctl_prop_pie_space,
        },
        'undo_file': get_file_tuple(scene.ctl_prop_undo_file2),
        'done' : scene.ctl_prop_is_show_done,
        'variables' : (get_setup_variable_list('fn-get_setup_tool_dict()') if scene.ctl_prop_tool_type == 'SIMPLE' else []),
        'files' : get_file_list()
    })
    return tool_dict


def set_setup_switch_data(setup_mode, tool_dict):
    scene = bpy.context.scene
    if setup_mode == 'Create':
        # Setting Group
        group_set = ctl_get_group_list_3973B(setup_mode)
        if len(group_set) > 0 and (tool_dict['group'] in group_set):
            scene.ctl_prop_create_group_set = tool_dict['group']
        else:
            try: scene.ctl_prop_create_group_set = 'New Group'
            except: pass
            scene.ctl_prop_new_group = tool_dict['group']
        # Setting Tool
        scene.ctl_prop_new_tool = tool_dict['tool']
    elif setup_mode == 'Update':
        # Setting Group
        group_set = ctl_get_group_list_3973B(setup_mode)
        if len(group_set) > 0:
            if tool_dict['group'] in group_set:
                scene.ctl_prop_group_set = tool_dict['group']
            else:
                try: scene.ctl_prop_group_set = group_set[0]
                except: pass
        # Setting Tool
        tool_set = ctl_get_tool_list_3973B()
        if len(tool_set) > 0:
            if tool_dict['tool'] in tool_set:
                scene.ctl_prop_tool_set = tool_dict['tool']
            else:
                try: scene.ctl_prop_tool_set = tool_set[0]
                except: pass
    set_setup_tool_dict(tool_dict)


def ctl_update_ctl_prop_tool_set(self, context):
    global freeze_setup_change
    scene = bpy.context.scene

    def get_tool_dict(group, tool):
        file_name = '\\tools\\' + get_tool_file_name(group, tool)
        json_data = get_file_data(file_name)
        if json_data != '':
            tool_dict = {}
            try:
                tool_dict = json.loads(json_data)
            except:
                return None
            return tool_dict
        return None
    if not freeze_setup_change:
        if scene.ctl_prop_tool_set.replace('-', '').replace(' ', '').upper() == 'EMPTY':
            bpy.ops.ctl.clear_setup_data('INVOKE_DEFAULT', )
        else:
            group = scene.ctl_prop_group_set
            tool = scene.ctl_prop_tool_set
            tool_dict = get_tool_dict(group, tool)
            if tool_dict is not None:
                set_setup_tool_dict(tool_dict)
            else:
                bpy.ops.ctl.clear_setup_data('INVOKE_DEFAULT', )


# TODO <--- set setup


def set_setup_tool_dict(tool_dict):
    scene = bpy.context.scene
    file_collection = scene.ctl_prop_file_collection

    def set_file_list(file_list):
        file_collection.clear()
        if isinstance(file_list, list) and len(file_list) > 0:
            for file in file_list:
                (text_name, line_list) = tuple(file)
                new_file = file_collection.add()
                if text_name in bpy.data.texts:
                    new_file.pointer = bpy.data.texts[text_name]
                else:
                    new_file.name = text_name

    def get_undo_from_tuple(tuple_item):
        (text_name, line_list) = tuple(tuple_item)
        if text_name in bpy.data.texts:
            return bpy.data.texts[text_name]
        else:
            return None
    scene.ctl_prop_tool_description = tool_dict['description']
    scene.ctl_prop_tool_type = tool_dict['type']
    scene.ctl_prop_pie_enabled = tool_dict['pie']['enabled']
    scene.ctl_prop_tool_icon = tool_dict['pie']['icon']
    scene.ctl_prop_pie_space = tool_dict['pie']['space']
    scene.ctl_prop_undo_file2 = get_undo_from_tuple(tool_dict['undo_file'])
    scene.ctl_prop_is_show_done = get_undo_from_tuple(tool_dict['done'])
    variables['test'] = tool_dict['variables']
    ctl_directory_to_variable_collection('test')
    set_file_list(tool_dict['files'])


# FIXME bpy.ops.ctl.clear_setup_data('INVOKE_DEFAULT', is_mode_update)
freeze_setup_change = False
class CTL_OT_Clear_Setup_Data(bpy.types.Operator):
    bl_idname = "ctl.clear_setup_data"
    bl_label = "Clear Setup"
    bl_description = "Clear all the in data in Create or Update mode"
    bl_options = {"REGISTER", "UNDO"}
    clear_create: bpy.props.BoolProperty(name='Clear Create Header', description='', options={'HIDDEN'}, default=False)
    clear_update: bpy.props.BoolProperty(name='Clear Update Header', description='', options={'HIDDEN'}, default=False)
    clear_files: bpy.props.BoolProperty(name='Clear Files, If Not Protected', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def move_file_to_bin(file_name):
            if file_name != '':
                ctl_path = get_ctl_path()
                from_path = ctl_path + '\\tools\\' + file_name
                to_path = ctl_path + '\\recycle_bin\\' + file_name
                bin_path = ctl_path + '\\recycle_bin'
                if os.path.exists(from_path):
                    if not os.path.exists(bin_path):
                        os.mkdir(bin_path)
                    print('tool-to-bin :', bin_path)
                    os.replace(from_path, to_path)
        global freeze_setup_change
        scene = bpy.context.scene
        if self.clear_create:
            freeze_setup_change = True
            create_group_set = ctl_get_group_list_3973B('Create')
            if len(create_group_set) > 0:
                scene.ctl_prop_create_group_set = create_group_set[0]
            scene.ctl_prop_new_group = ''
            scene.ctl_prop_new_tool = ''
        if self.clear_update:
            freeze_setup_change = True
            group_set = ctl_get_group_list_3973B('')
            if len(group_set) > 0:
                scene.ctl_prop_group_set = group_set[0]
            tool_set = ctl_get_tool_list_3973B()
            if len(tool_set) > 0:
                scene.ctl_prop_tool_set = tool_set[0]
        freeze_setup_change = False
        if scene.ctl_prop_setup_mode == 'Update':
            move_file_to_bin('00.setup.00.update.json')
        else:
            move_file_to_bin('00.setup.00.create.json')
        if self.clear_files and not scene.ctl_prop_setup_keep_file:
            if scene.ctl_prop_undo_file2 is not None:
                bpy.data.texts.remove(scene.ctl_prop_undo_file2, do_unlink=True)
            for file_item in scene.ctl_prop_file_collection:
                if file_item.pointer is not None:
                    bpy.data.texts.remove(file_item.pointer, do_unlink=True)
            # FIXME Add (remove enum file)
        scene.ctl_prop_tool_description = ''
        scene.ctl_prop_tool_type = 'SIMPLE'
        scene.ctl_prop_pie_enabled = False
        scene.ctl_prop_tool_icon = ''
        scene.ctl_prop_pie_space = 'Any Space'
        scene.ctl_prop_undo_file2 = None
        global freeze_var_for_switch
        freeze_var_for_switch = True
        for var in bpy.context.scene.ctl_prop_var_collection:
            try: ctl_variable_unregister(var.id)
            except: pass
        scene.ctl_prop_var_collection.clear()
        freeze_var_for_switch = False
        scene.ctl_prop_active_var_index = 0
        scene.ctl_prop_file_collection.clear()
        scene.ctl_prop_active_file_index = 0
        variables['test'] = []
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# TODO X Create Tool Operator
class CTL_OT_Create_Tool_28Cc0(bpy.types.Operator):
    bl_idname = "ctl.create_tool_28cc0"
    bl_label = "Create Tool"
    bl_description = "Create a new tool by storing JSON file in addons folder"
    bl_options = {"REGISTER", "UNDO"}
    # is_done: bpy.props.BoolProperty(name='is var open', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):

        def is_tool_exists(tool):
            tool_p = processed_name(tool)
            file_list = get_file_list_from_tools_dir()
            for file_name in file_list:
                flist = file_name.split('.')
                if flist[3] == tool_p:
                    return True
            return False

        def write_tool_dict(setup_mode, group, tool):
            if group != '' and tool != '' and tool.replace('-', '').replace(' ', '').upper() != 'EMPTY':
                global global_tool_list
                tool_dict = get_setup_tool_dict(setup_mode, False)
                if setup_mode == 'Update':
                    file_name = 'tools\\' + get_tool_file_name(group, tool)
                    set_file_data(file_name, json.dumps(tool_dict, indent = 4))
                    is_found = False
                    for group_data in global_tool_list:
                        (group_name, tool_data_list) = group_data
                        if group_name == group:
                            for tool_index in range(len(tool_data_list)):
                                tool_name = tool_data_list[tool_index][0]
                                if tool_name == tool:
                                    tool_data_list[tool_index] = (tool, tool_dict)
                                    bpy.ops.ctl.reload_tool_list('INVOKE_DEFAULT', )
                                    return
                elif setup_mode == 'Create':
                    file_name = f'tools\\99.{processed_name(group)}.99.{processed_name(tool)}.json'
                    set_file_data(file_name, json.dumps(tool_dict, indent = 4))
                    is_found = False
                    for group_idx in range(len(global_tool_list)):
                        (group_name, tool_data_list) = global_tool_list[group_idx]
                        if group_name == group:
                            is_found = True
                            tool_data_list.append((tool, tool_dict))
                    if not is_found:
                        global_tool_list.append((group, [(tool, tool_dict)]))
                    write_tool_order_to_file()
                    bpy.ops.ctl.reload_tool_list('INVOKE_DEFAULT', )
        # tool = self.ctl_tool
        scene = bpy.context.scene
        is_mode_update = (scene.ctl_prop_setup_mode == 'Update')
        if is_mode_update:
            group = scene.ctl_prop_group_set
            tool = scene.ctl_prop_tool_set
            write_tool_dict('Update', group, tool)
        else:
            tool = scene.ctl_prop_new_tool
            if not is_tool_exists(tool):
                if scene.ctl_prop_create_group_set.upper() == 'NEW GROUP':
                    group = scene.ctl_prop_new_group
                else:
                    group = scene.ctl_prop_create_group_set
                write_tool_dict('Create', group, tool)
            else:
                print('ERROR: Tool already exists,', tool)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# TODO Pick Selected
class CTL_OT_Pick_Selected_27Dd5(bpy.types.Operator):
    bl_idname = "ctl.pick_selected_27dd5"
    bl_label = "Pick Selected"
    bl_description = "Pick the active or selected item in the field"
    bl_options = {"REGISTER", "UNDO"}
    ctl_tool: bpy.props.StringProperty(name='tool', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    ctl_type: bpy.props.StringProperty(name='type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    ctl_property: bpy.props.StringProperty(name='property', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        tool = self.ctl_tool
        type = self.ctl_type
        property = self.ctl_property

        def run_code(property, value):
            try:
                code = property + ' = "' + value + '"'
                exec(code)
            except:
                pass

        def get_edit_bone(type):
            if bpy.context.object is not None and bpy.context.active_bone is not None:
                obj_name = bpy.context.object.name
                bone_name = bpy.context.active_bone.name
                return f"{obj_name} : {bone_name}"

        def get_edit_bone_set(type):
            if bpy.context.object is not None:
                obj_name = bpy.context.object.name
                bone_list = bpy.context.selected_editable_bones
                pure_list = [bone.name for bone in bone_list]
                return f'{obj_name} : {pure_list}'

        def get_pose_bone(type):
            if bpy.context.object is not None and bpy.context.active_pose_bone is not None:
                obj_name = bpy.context.object.name
                bone_name = bpy.context.active_pose_bone.name
                return f'{obj_name} : {bone_name}'

        def get_pose_bone_set(type):
            if bpy.context.object is not None:
                obj_name = bpy.context.object.name
                bone_list = bpy.context.selected_pose_bones_from_active_object
                pure_list = [bone.name for bone in bone_list]
                return f'{obj_name} : {pure_list}'
        ###################### START ######################
        type = type
        property = property
        if tool == '':
            tool = 'test'
        if type == 'Edit Bone':
            if bpy.context.mode == 'EDIT_ARMATURE':
                value = get_edit_bone(type)
                run_code(property, value)
        elif type == 'Edit Bone Set':
            if bpy.context.mode == 'EDIT_ARMATURE':
                value = get_edit_bone_set(type)
                run_code(property, value)
        elif type == 'Pose Bone':
            if bpy.context.mode == 'POSE':
                value = get_pose_bone(type)
                run_code(property, value)
        elif type == 'Pose Bone Set':
            if bpy.context.mode == 'POSE':
                value = get_pose_bone_set(type)
                run_code(property, value)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# TODO Var Interface


def ctl_variables_interface_86A99(layout_function, ):
    layout_function.separator(factor=1.0)
    col_1535C = layout_function.column(heading='', align=False)
    col_1535C.alert = False
    col_1535C.enabled = True
    col_1535C.active = True
    col_1535C.use_property_split = False
    col_1535C.use_property_decorate = False
    col_1535C.scale_x = 1.0
    col_1535C.scale_y = 1.0
    col_1535C.alignment = 'EXPAND'
    col_1535C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_D86F4 = col_1535C.row(heading='', align=False)
    row_D86F4.alert = False
    row_D86F4.enabled = True
    row_D86F4.active = True
    row_D86F4.use_property_split = False
    row_D86F4.use_property_decorate = False
    row_D86F4.scale_x = 1.0
    row_D86F4.scale_y = 1.0
    row_D86F4.alignment = 'EXPAND'
    row_D86F4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    coll_id = display_collection_id('F34BC', locals())
    row_D86F4.template_list('CTL_UL_display_collection_list_F34BC', coll_id, bpy.context.scene, 'ctl_prop_var_collection', bpy.context.scene, 'ctl_prop_active_var_index', rows=0)
    col_BAEF7 = row_D86F4.column(heading='', align=True)
    col_BAEF7.alert = False
    col_BAEF7.enabled = True
    col_BAEF7.active = True
    col_BAEF7.use_property_split = False
    col_BAEF7.use_property_decorate = False
    col_BAEF7.scale_x = 1.0
    col_BAEF7.scale_y = 1.0
    col_BAEF7.alignment = 'EXPAND'
    col_BAEF7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = col_BAEF7.operator('ctl.add_variable_30407', text='', icon_value=31, emboss=True, depress=False)
    op = col_BAEF7.operator('ctl.remove_variable_265a2', text='', icon_value=32, emboss=True, depress=False)
    col_BAEF7.separator(factor=1.0)
    row_4CB65 = col_BAEF7.row(heading='', align=True)
    row_4CB65.alert = False
    row_4CB65.enabled = True
    row_4CB65.active = ctl_move_possibility_68AE7(len(bpy.context.scene.ctl_prop_var_collection.values()), bpy.context.scene.ctl_prop_active_var_index)[0]
    row_4CB65.use_property_split = False
    row_4CB65.use_property_decorate = False
    row_4CB65.scale_x = 1.0
    row_4CB65.scale_y = 1.0
    row_4CB65.alignment = 'EXPAND'
    row_4CB65.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = row_4CB65.operator('ctl.move_file_b83ed', text='', icon_value=7, emboss=True, depress=False)
    op.ctl_is_up = True
    row_4EA8B = col_BAEF7.row(heading='', align=True)
    row_4EA8B.alert = False
    row_4EA8B.enabled = True
    row_4EA8B.active = ctl_move_possibility_68AE7(len(bpy.context.scene.ctl_prop_var_collection.values()), bpy.context.scene.ctl_prop_active_var_index)[1]
    row_4EA8B.use_property_split = False
    row_4EA8B.use_property_decorate = False
    row_4EA8B.scale_x = 1.0
    row_4EA8B.scale_y = 1.0
    row_4EA8B.alignment = 'EXPAND'
    row_4EA8B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    op = row_4EA8B.operator('ctl.move_file_b83ed', text='', icon_value=5, emboss=True, depress=False)
    op.ctl_is_up = False
    col_1535C.separator(factor=1.0)
    var_col = bpy.context.scene.ctl_prop_var_collection
    if var_col is not None and len(var_col) > 0:
        var_idx = bpy.context.scene.ctl_prop_active_var_index
        var = var_col[var_idx]
        if (len(var_col.values()) != 0):
            data = ctl_get_var(var.id, 'fn-ctl_variables_interface_86A99()')
            col_1535C.label(text=processed_name(var.name), icon_value=746)
            col_1535C.prop(var, 'name', text='Name ', icon_value=0, emboss=True)
            col_1535C.prop(var, 'type', text='Type ', icon_value=0, emboss=True)
            col_1535C.prop(var, 'description', text='Descript ', icon_value=0, emboss=True)
            col_1535C.separator(factor=0.5)
            row = col_1535C.row(heading='', align=True)
            row.prop(bpy.context.scene, 'ctl_prop_var_display_type', text='Display ', emboss=True, expand=True)
            col_1535C.separator(factor=1)
            if bpy.context.scene.ctl_prop_var_display_type == 'DATA':
                ctl_variable_attach_data(col_1535C, data, var.id, var.type)
            elif bpy.context.scene.ctl_prop_var_display_type == 'OTHERS': # TODO <<<
                row = col_1535C.row(heading='', align=True)
                row.prop(var, 'emboss', text='Emboss ', icon_value=0, emboss=True, toggle=True)
                row.prop(var, 'expand', text='Expand ', icon_value=0, emboss=True, toggle=True)
                row.prop(var, 'slider', text='Slider ', icon_value=0, emboss=True, toggle=True)
                row.prop(var, 'toggle', text='Toggle ', icon_value=0, emboss=True, toggle=True)
                col_1535C.separator(factor=0.5)
                col_1535C.prop(var, 'disappear_if', text='Disappear if ', icon_value=0, emboss=True)
                col_1535C.prop(var, 'disable_if', text='Disable if ', icon_value=0, emboss=True)
                row = col_1535C.row(heading='', align=True)
                row.prop(var, 'update_file', text='Update ', icon_value=0, emboss=True)
                op = row.operator('ctl.load_update_file', text='', icon_value=707, emboss=True, depress=False)
                op.id = var.id
                if bpy.context.scene.ctl_prop_switch_file_live:
                    op = row.operator('ctl.switch_file_in_editor', text='', icon_value=256, emboss=True, depress=False)
                    op.name = var.update_file.name if var.update_file is not None else ''
                col_1535C.separator(factor=0.5)
                col_1535C.prop(var, 'separator', text='Separator ', icon_value=0, emboss=True)


def ctl_variable_register(id, type):
    if id != '':
        prop_name = f'ctl_prop_setup_var_{id}'
        class_name = ctl_get_var_class(type)
        register_code = f'bpy.types.Scene.{prop_name} = bpy.props.PointerProperty(type={class_name})'
        try:
            exec(register_code)
        except Exception as e:
            print('ERROR : In Creating Variable')
            print('Code :', register_code)
            print_error(e)


def ctl_variable_unregister(id):
    prop_name = f'ctl_prop_setup_var_{id}'
    unregister_code = f'del bpy.types.Scene.{prop_name}'
    try:
        exec(unregister_code)
    except Exception as e:
        print('ERROR : In Variable Unregister')
        print('Code :', unregister_code)
        print_error(e)


def ctl_variable_type_update(self, context):
    ctl_variable_unregister(self.id)
    ctl_variable_register(self.id, self.type)
    ctl_update_variable_3BA34('')


# TODO Add Variable
class CTL_OT_Add_Variable_30407(bpy.types.Operator):
    bl_idname = "ctl.add_variable_30407"
    bl_label = "Add Variable"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    temp_prop = None

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        # [(id), (common), (other)] setup_variables = []
        import random
        var_id_list = []
        for var in setup_variables:
            id = var[0]
            if id != '':
                var_id_list.append(id)

        def id_generate(id_list):
            num = random.randint(1010, 9989)
            if str(num) in id_list:
                return id_generate(id_list)
            else:
                return str(num)
        id = id_generate(var_id_list)
        # print(id, '<- id')
        col = bpy.context.scene.ctl_prop_var_collection
        idx = bpy.context.scene.ctl_prop_active_var_index
        global freeze_var_for_switch
        freeze_var_for_switch = True
        item = col.add()
        is_more_then_one = 1 < len(col.values())
        if is_more_then_one:
            col.move(col.values().index(item), int(idx + 1.0))
            item = col[int(idx + 1.0)]
            idx = col.values().index(item)
        bpy.context.scene.ctl_prop_active_var_index = idx
        ctl_check_duplicate_name_B5648('', item, col)
        ctl_variable_register(id, item.type)
        # var_data = ctl_get_var(id, '')
        item.id = id
        freeze_var_for_switch = False
        ctl_update_variable_3BA34('')
        # print(id, '<--- Variable Added')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_var_type_icon_7F9BF(Type):
    type = Type
    icon = None
    icon = 'ERROR'
    if type == 'Boolean':
        icon = 'FORCE_CHARGE'
    elif type == 'Integer':
        icon = 'DRIVER_TRANSFORM'
    elif type == 'Float':
        icon = 'CON_TRANSLIKE'
    elif type == 'String':
        icon = 'SYNTAX_OFF'
    elif type == 'Enum':
        icon = 'PRESET'
    elif type == 'Pointer':
        icon = 'MONKEY'
    elif type == 'Edit Bone':
        icon = 'BONE_DATA'
    elif type == 'Pose Bone':
        icon = 'BONE_DATA'
    elif type == 'Edit Bone Set':
        icon = 'GROUP_BONE'
    elif type == 'Pose Bone Set':
        icon = 'GROUP_BONE'
    return icon


class CTL_OT_Remove_Variable_265A2(bpy.types.Operator):
    bl_idname = "ctl.remove_variable_265a2"
    bl_label = "Remove Variable"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        var_col = bpy.context.scene.ctl_prop_var_collection
        var_index = bpy.context.scene.ctl_prop_active_var_index
        var = var_col[var_index]
        ctl_variable_unregister(var.id)
        if len(var_col) > var_index:
            var_col.remove(var_index)
        if ((len(var_col.values()) <= var_index) and (len(var_col.values()) != 0)):
            var_index = int(len(var_col.values()) - 1)
        bpy.context.scene.ctl_prop_active_var_index = var_index
        ctl_update_variable_3BA34('')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# TODO <--- fn
class CTL_OT_ADD_ENUM_FUNCTION(bpy.types.Operator):
    bl_idname = "ctl.add_enum_function"
    bl_label = "Add Enum Function"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    id: bpy.props.StringProperty(name='Variable ID', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if self.id != '':
            data = ctl_get_var(self.id, 'ctl.add_enum_function')
            text_pointer = data.file
            if text_pointer is not None:
                fn_code = get_file_data('enum_function_template.py')
                if fn_code != '':
                    text_pointer.write(fn_code)
                    data.function = 'get_item_list'
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def type_str_list(var):
    if isinstance(var, list):
        for item in var:
            if isinstance(item, str):
                pass
            else:
                return False
        return True
    return False


temp_list = []


def get_enum_list(var_dict):
    pass


def get_enum_code(id, tool):

    def get_var_from_collection(id):
        for var in bpy.context.scene.ctl_prop_var_collection:
            if var.id == id:
                return var
        return None

    def type_tuple_list(var):
        if isinstance(var, list):
            for item in var:
                if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) and (isinstance(item[1], str) or isinstance(item[1], int)):
                    pass
                else:
                    return False
            return True
        return False

    def is_fn_okay(tool_code, fn_name, fn_code, var_name):
        fn_call = f'\nglobal temp_list\ntemp_list = {fn_name}(tool)'
        test_code = tool_code + fn_code + fn_call
        ctl_run_code_with_functions(None, None, tool, test_code, f'Enum Variable Test Code ({tool}.{var_name})', False)
        global temp_list
        # print('list returned :', temp_list)
        if isinstance(temp_list, list):
            if len(temp_list) > 0:
                if type_str_list(temp_list) or type_tuple_list(temp_list):
                    return True
                else:
                    print('Error: List Is Not In Format, [str] or [(str, int)]')
            else:
                print('Error: List Is Empty')
        else:
            print('Error: List Is Not Returned')
        return False
    if id != '':
        data = ctl_get_var(id, 'fn-get_enum_code()')
        var = get_var_from_collection(id)
        fn_code = data.file.as_string() # FIXME ==== as_string()
        fn_name = data.function
        tool_code = f'tool = bpy.context.scene.ctl_{processed_name(tool)}\n'
        if is_fn_okay(tool_code, fn_name, fn_code, var.name):
            c1 = f"def ctl_enum_items_{processed_name(var.name)}(self, context):\n"
            c2 = f"    " + tool_code
            c3 = f"    item_list = {fn_name}(tool)\n"
            c4 = f"    return convert_list_to_enum_list(item_list)\n"
            fn_call = c1 + c2 + c3 + c4
            code = fn_code + fn_call
            # print('enum code :')
            # print(code)
            return code
    return ''


# TODO +++ Update Code


def get_update_code(file_code, var, tool):
    tool_code = f'tool = bpy.context.scene.ctl_{processed_name(tool)}\n'
    fn_define = f"def ctl_update_var_{processed_name(var['name'])}(self, context):\n" + tool_code
    fn_code = (fn_define + file_code).replace('\n', '\n    ') + '\n\n'
    return fn_code


def get_items_list(str_list):

    def get_var_from_collection(id):
        for var in bpy.context.scene.ctl_prop_var_collection:
            if var.id == id:
                return var
        return None

    def type_tuple_list(var):
        if isinstance(var, list):
            for item in var:
                if (isinstance(item, tuple) or isinstance(item, list)) and len(item) == 2 and isinstance(item[0], str) and (isinstance(item[1], str) or isinstance(item[1], int)):
                    pass
                else:
                    return False
            return True
        return False
    str_list = str_list.replace('(', '[').replace(')', ']').replace('\'', '"')
    try:
        item_list = json.loads(str_list)
    except:
        return ''
    # print('item_list :', item_list)
    if isinstance(item_list, list):
        if len(item_list) > 0:
            if type_str_list(item_list) or type_tuple_list(item_list):
                new_list = convert_list_to_enum_list(item_list)
                return new_list
            else:
                print('Error: List Is Not In Format, [str] or [(str, int)]')
        else:
            print('Error: List Is Empty')
    else:
        print('Error: List Is Not Returned')
    return ''


# TODO Move Variable
class CTL_OT_Move_Variable_B83Ed(bpy.types.Operator):
    bl_idname = "ctl.move_file_b83ed"
    bl_label = "Move File"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    ctl_is_up: bpy.props.BoolProperty(name='Is Up', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        var_col = bpy.context.scene.ctl_prop_var_collection
        var_idx = bpy.context.scene.ctl_prop_active_var_index
        move_to_idx = int(var_idx - 1) if self.ctl_is_up else int(var_idx + 1)
        var_col.move(var_idx, move_to_idx)
        var_idx = move_to_idx
        bpy.context.scene.ctl_prop_active_var_index = var_idx
        # item_CF1A4 = var_col[move_to_idx]
        ctl_update_variable_3BA34('')
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def ctl_move_possibility_68AE7(Length, Index):
    length = Length
    index = Index
    move_up = None
    move_down = None
    move_up = True
    move_down = True
    if index <= 0:
        move_up = False
    if index >= length-1:
        move_down = False
    return [move_up, move_down]


def ctl_pointer_type_enum_items(self, context):
    enum_items = [
        ('Scene', 'Scene', '', 0),
        ('Action', 'Action', '', 0),
        ('Armature', 'Armature', '', 0),
        ('Brush', 'Brush', '', 0),
        ('CacheFile', 'CacheFile', '', 0),
        ('Camera', 'Camera', '', 0),
        ('Collection', 'Collection', '', 0),
        ('Curve', 'Curve', '', 0),
        ('FreestyleLineStyle', 'FreestyleLineStyle', '', 0),
        ('GreasePencil', 'GreasePencil', '', 0),
        ('Image', 'Image', '', 0),
        ('Key', 'Key', '', 0),
        ('Lattice', 'Lattice', '', 0),
        ('Library', 'Library', '', 0),
        ('Light', 'Light', '', 0),
        ('LightProbe', 'LightProbe', '', 0),
        ('Mask', 'Mask', '', 0),
        ('Material', 'Material', '', 0),
        ('Mesh', 'Mesh', '', 0),
        ('MetaBall', 'MetaBall', '', 0),
        ('MovieClip', 'MovieClip', '', 0),
        ('NodeTree', 'NodeTree', '', 0),
        ('Object', 'Object', '', 0),
        ('PaintCurve', 'PaintCurve', '', 0),
        ('Palette', 'Palette', '', 0),
        ('ParticleSettings', 'ParticleSettings', '', 0),
        ('Screen', 'Screen', '', 0),
        ('Sound', 'Sound', '', 0),
        ('Speaker', 'Speaker', '', 0),
        ('Text', 'Text', '', 0),
        ('Texture', 'Texture', '', 0),
        ('VectorFont', 'VectorFont', '', 0),
        ('Volume', 'Volume', '', 0),
        ('WindowManager', 'WindowManager', '', 0),
        ('WorkSpace', 'WorkSpace', '', 0),
        ('World', 'World', '', 0),
    ]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def ctl_float_unit_enum_items(self, context):
    enum_items = [
        ('NONE', 'None', '', 0),
        ('LENGTH', 'Length', '', 0),
        ('AREA', 'Area', '', 0),
        ('VOLUME', 'Volume', '', 0),
        ('ROTATION', 'Rotation', '', 0),
        ('TIME', 'Time', '', 0),
        ('VELOCITY', 'Velocity', '', 0),
        ('ACCELERATION', 'Acceleration', '', 0),
        ('MASS', 'Mass', '', 0),
        ('CAMERA', 'Camera', '', 0),
        ('POWER', 'Power', '', 0),
        ('TEMPERATURE', 'Temperature', '', 0),
    ]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def ctl_num_subtype_enum_items(self, context):
    enum_items = [
        ('NONE', 'None', '', 0),
        ('PIXEL', 'Pixel', '', 0),
        ('UNSIGNED', 'Unsigned', '', 0),
        ('PERCENTAGE', 'Percentage', '', 0),
        ('FACTOR', 'Factor', '', 0),
        ('ANGLE', 'Angle', '', 0),
        ('TIME', 'Time', '', 0),
        ('DISTANCE', 'Distance', '', 0),
        ('DISTANCE_CAMERA', 'Camera Distance', '', 0),
        ('POWER', 'Power', '', 0),
        ('TEMPERATURE', 'Temperature', '', 0),
    ]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def ctl_string_subtype_enum_items(self, context):
    enum_items = [
        ('NONE', 'None', '', 0),
        ('FILE_PATH', 'File Path', '', 0),
        ('DIR_PATH', 'Directory Path', '', 0),
        ('FILE_NAME', 'File Name', '', 0),
        ('BYTE_STRING', 'Byte String', '', 0),
        ('PASSWORD', 'Password', '', 0),
    ]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


class CTL_GROUP_var_string_group(bpy.types.PropertyGroup):
    subtype: bpy.props.EnumProperty(name='Subtype', description='', items=ctl_string_subtype_enum_items, update=ctl_update_variable_from_property)

    default: bpy.props.StringProperty(name='Default', description='', default='', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)
    maxlen: bpy.props.IntProperty(name='Max Len', description='', default=0, subtype='NONE', update=ctl_update_variable_from_property)


class CTL_GROUP_var_bool_group(bpy.types.PropertyGroup):

    default: bpy.props.BoolProperty(name='var', description='', default=False, update=ctl_update_variable_from_property)


class CTL_GROUP_var_float_group(bpy.types.PropertyGroup):
    subtype: bpy.props.EnumProperty(name='Subtype', description='', items=ctl_num_subtype_enum_items, update=ctl_update_variable_from_property)
    unit: bpy.props.EnumProperty(name='Unit', description='', items=ctl_float_unit_enum_items, update=ctl_update_variable_from_property)

    default: bpy.props.FloatProperty(name='Default', description='', default=0.0, subtype='NONE', unit='NONE', step=3, precision=6, update=ctl_update_variable_from_property)
    step: bpy.props.IntProperty(name='Step', description='', default=3, subtype='NONE', update=ctl_update_variable_from_property)
    precision: bpy.props.IntProperty(name='Precision', description='', default=6, subtype='NONE', update=ctl_update_variable_from_property)
    use_min: bpy.props.BoolProperty(name='Use Minimum', description='', default=False, update=ctl_update_variable_from_property)
    use_max: bpy.props.BoolProperty(name='Use Maximum', description='', default=False, update=ctl_update_variable_from_property)
    use_soft_min: bpy.props.BoolProperty(name='Use Soft Minimum', description='', default=False, update=ctl_update_variable_from_property)
    use_soft_max: bpy.props.BoolProperty(name='Use Soft Maximum', description='', default=False, update=ctl_update_variable_from_property)
    min: bpy.props.FloatProperty(name='Minimum', description='', default=0.0, subtype='NONE', unit='NONE', step=3, precision=6, update=ctl_update_variable_from_property)
    max: bpy.props.FloatProperty(name='Maximum', description='', default=1.0, subtype='NONE', unit='NONE', step=3, precision=6, update=ctl_update_variable_from_property)
    soft_min: bpy.props.FloatProperty(name='Soft Minimum', description='', default=0.0, subtype='NONE', unit='NONE', step=3, precision=6, update=ctl_update_variable_from_property)
    soft_max: bpy.props.FloatProperty(name='Soft Maximum', description='', default=1.0, subtype='NONE', unit='NONE', step=3, precision=6, update=ctl_update_variable_from_property)


class CTL_GROUP_var_int_group(bpy.types.PropertyGroup):
    subtype: bpy.props.EnumProperty(name='Subtype', description='', items=ctl_num_subtype_enum_items, update=ctl_update_variable_from_property)

    default: bpy.props.IntProperty(name='Default', description='', default=0, subtype='NONE', update=ctl_update_variable_from_property)
    use_min: bpy.props.BoolProperty(name='Use Minimum', description='', default=False, update=ctl_update_variable_from_property)
    use_max: bpy.props.BoolProperty(name='Use Maximum', description='', default=False, update=ctl_update_variable_from_property)
    use_soft_min: bpy.props.BoolProperty(name='Use Soft Minimum', description='', default=False, update=ctl_update_variable_from_property)
    use_soft_max: bpy.props.BoolProperty(name='Use Soft Maximum', description='', default=False, update=ctl_update_variable_from_property)
    min: bpy.props.IntProperty(name='Minimum', description='', default=0, subtype='NONE', update=ctl_update_variable_from_property)
    max: bpy.props.IntProperty(name='Maximum', description='', default=1, subtype='NONE', update=ctl_update_variable_from_property)
    soft_min: bpy.props.IntProperty(name='Soft Minimum', description='', default=0, subtype='NONE', update=ctl_update_variable_from_property)
    soft_max: bpy.props.IntProperty(name='Soft Maximum', description='', default=1, subtype='NONE', update=ctl_update_variable_from_property)


class CTL_GROUP_var_enum_group(bpy.types.PropertyGroup):
    is_multiple: bpy.props.BoolProperty(name='Is Multiple', description='', default=False, update=ctl_update_variable_from_property)
    is_dynamic: bpy.props.BoolProperty(name='Is Dynamic', description='', default=False, update=ctl_update_variable_from_property)
    items: bpy.props.StringProperty(name='Items', description='', default='[]', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)
    file: bpy.props.PointerProperty(name='File', description='', type=bpy.types.Text, update=ctl_update_variable_from_property)
    function: bpy.props.StringProperty(name='Function', description='', default='', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)


class CTL_GROUP_var_pointer_group(bpy.types.PropertyGroup):
    datatype: bpy.props.EnumProperty(name='Data Type', description='', items=ctl_pointer_type_enum_items, update=ctl_update_variable_from_property)


def ctl_variable_type_enum_items(self, context):
    enum_items = [
        ('String', 'String', '', 742, 0),
        ('Boolean', 'Boolean', '', 343, 1),
        ('Integer', 'Integer', '', 428, 2),
        ('Float', 'Float', '', 422, 3),
        ('Enum', 'Enum', '', 190, 4),
        ('Pointer', 'Pointer', '', 292, 5),
        ('Edit Bone', 'Edit Bone', '', 174, 6),
        ('Pose Bone', 'Pose Bone', '', 174, 7),
        ('Edit Bone Set', 'Edit Bone Set', '', 200, 8),
        ('Pose Bone Set', 'Pose Bone Set', '', 200, 9)
    ]
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def ctl_get_var_property_type(type):
    prop_type = ''
    if type == 'Boolean':
        prop_type = 'BoolProperty'
    elif type == 'Integer':
        prop_type = 'IntProperty'
    elif type == 'Float':
        prop_type = 'FloatProperty'
    elif type == 'Enum':
        prop_type = 'EnumProperty'
    elif type == 'Pointer':
        prop_type = 'PointerProperty'
    elif type == 'String' or type == 'Edit Bone' or type == 'Pose Bone' or type == 'Edit Bone Set' or type == 'Pose Bone Set':
        prop_type = 'StringProperty'
    return prop_type


def ctl_get_var_class(type):
    class_name = ''
    if type == 'Boolean':
        class_name = 'CTL_GROUP_var_bool_group'
    elif type == 'Integer':
        class_name = 'CTL_GROUP_var_int_group'
    elif type == 'Float':
        class_name = 'CTL_GROUP_var_float_group'
    elif type == 'String':
        class_name = 'CTL_GROUP_var_string_group'
    elif type == 'Enum':
        class_name = 'CTL_GROUP_var_enum_group'
    elif type == 'Pointer':
        class_name = 'CTL_GROUP_var_pointer_group'
    elif type == 'Edit Bone':
        class_name = 'CTL_GROUP_var_string_group'
    elif type == 'Pose Bone':
        class_name = 'CTL_GROUP_var_string_group'
    elif type == 'Edit Bone Set':
        class_name = 'CTL_GROUP_var_string_group'
    elif type == 'Pose Bone Set':
        class_name = 'CTL_GROUP_var_string_group'
    else:
        class_name = 'CTL_GROUP_var_string_group'
    return class_name


def ctl_get_var(id, location):
    if id is not None and id != '':
        prop_name = f'bpy.context.scene.ctl_prop_setup_var_{str(id)}'
        try:
            global temp_prop
            exec(f'global temp_prop\ntemp_prop = {prop_name}')
            return temp_prop
        except Exception as e:
            # self.report({'ERROR'}, message='Error in Accessing Variable')
            print('ERROR: In Accessing Variable, Location :', location)
            print('ID :', id)
            print(prop_name)
            traceback.print_exc()
            return None
    else:
        return None


def ctl_recalculate_vaiables_list(tool):
    if tool == '':
        tool == 'test'
    variables[tool] = get_setup_variable_list('fn-ctl_recalculate_vaiables_list()')


def get_setup_variable_list(location):

    def get_data_directory(data, type):
        if type == 'String':
            return {
                'subtype' : data.subtype,
                'default' : data.default,
                'maxlen' : data.maxlen,
            }
        elif type == 'Boolean':
            return {
                'default' : data.default,
            }
        elif type == 'Integer':
            return {
                'subtype' : data.subtype,
                'default' : data.default,
                'use_min' : data.use_min,
                'use_max' : data.use_max,
                'use_soft_min' : data.use_soft_min,
                'use_soft_max' : data.use_soft_max,
                'min' : data.min,
                'max' : data.max,
                'soft_min' : data.soft_min,
                'soft_max' : data.soft_max,
            }
        elif type == 'Float':
            return {
                'subtype' : data.subtype,
                'unit' : data.unit,
                'default' : data.default,
                'step' : data.step,
                'precision' : data.precision,
                'use_min' : data.use_min,
                'use_max' : data.use_max,
                'use_soft_min' : data.use_soft_min,
                'use_soft_max' : data.use_soft_max,
                'min' : data.min,
                'max' : data.max,
                'soft_min' : data.soft_min,
                'soft_max' : data.soft_max,
            }
        elif type == 'Enum':
            return {
                'is_multiple' : data.is_multiple,
                'is_dynamic' : data.is_dynamic,
                'items' : data.items,
                'file' : (get_file_tuple(data.file) if data.is_dynamic else None),
                'function' : data.function,
            }
        elif type == 'Pointer':
            return {
                'datatype' : data.datatype,
            }
        elif type == 'Edit Bone':
            return {
                'subtype' : data.subtype,
                'default' : data.default,
                'maxlen' : data.maxlen,
            }
        elif type == 'Pose Bone':
            return {
                'subtype' : data.subtype,
                'default' : data.default,
                'maxlen' : data.maxlen,
            }
        elif type == 'Edit Bone Set':
            return {
                'subtype' : data.subtype,
                'default' : data.default,
                'maxlen' : data.maxlen,
            }
        elif type == 'Pose Bone Set':
            return {
                'subtype' : data.subtype,
                'default' : data.default,
                'maxlen' : data.maxlen,
            }
    list = []
    col = bpy.context.scene.ctl_prop_var_collection
    # print('Location :', location)
    # print([var.id for var in bpy.context.scene.ctl_prop_var_collection])
    for var in col:
        data = ctl_get_var(var.id, 'fn-get_setup_variable_list()')
        if data is not None:
            dir = {
                'id': var.id,
                'name': var.name,
                'type': var.type,
                'description': var.description,
                'disappear_if': var.disappear_if,
                'disable_if': var.disable_if,
                'emboss': var.emboss,
                'expand': var.expand,
                'slider': var.slider,
                'toggle': var.toggle,
                'separator': var.separator,
                'update_file': get_file_tuple(var.update_file),
                'data': get_data_directory(data, var.type)
            }
            list.append(dir)
    return list


# TODO <---- set


def ctl_directory_to_variable_collection(tool):
    if tool == '':
        tool == 'test'
    if tool in variables:
        global freeze_var_for_switch
        freeze_var_for_switch = True
        dict_list = variables[tool]
        set_setup_variable_list(dict_list)
        freeze_var_for_switch = False
        ctl_register_tool_variables(tool)


def set_setup_variable_list(dict_list):

    def get_enum_from_tuple(tuple_item):
        if isinstance(tuple_item, list) and len(tuple_item) == 2:
            (text_name, line_list) = tuple(tuple_item)
            if text_name in bpy.data.texts:
                return bpy.data.texts[text_name]
            else:
                return None

    def get_load_data(dict_data, col_data, type):
        if dict_data is not None and col_data is not None:
            if type == 'String':
                col_data.subtype = dict_data['subtype']
                col_data.default = dict_data['default']
                col_data.maxlen = dict_data['maxlen']
            elif type == 'Boolean':
                col_data.default = dict_data['default']
            elif type == 'Integer':
                col_data.subtype = dict_data['subtype']
                col_data.default = dict_data['default']
                col_data.use_min = dict_data['use_min']
                col_data.use_max = dict_data['use_max']
                col_data.use_soft_min = dict_data['use_soft_min']
                col_data.use_soft_max = dict_data['use_soft_max']
                col_data.min = dict_data['min']
                col_data.max = dict_data['max']
                col_data.soft_min = dict_data['soft_min']
                col_data.soft_max = dict_data['soft_max']
            elif type == 'Float':
                col_data.subtype = dict_data['subtype']
                col_data.unit = dict_data['unit']
                col_data.default = dict_data['default']
                col_data.step = dict_data['step']
                col_data.precision = dict_data['precision']
                col_data.use_min = dict_data['use_min']
                col_data.use_max = dict_data['use_max']
                col_data.use_soft_min = dict_data['use_soft_min']
                col_data.use_soft_max = dict_data['use_soft_max']
                col_data.min = dict_data['min']
                col_data.max = dict_data['max']
                col_data.soft_min = dict_data['soft_min']
                col_data.soft_max = dict_data['soft_max']
            elif type == 'Enum':
                col_data.is_multiple = dict_data['is_multiple']
                col_data.is_dynamic = dict_data['is_dynamic']
                col_data.items = dict_data['items']
                col_data.file = get_enum_from_tuple(dict_data['file'])
                col_data.function = dict_data['function']
            elif type == 'Pointer':
                col_data.datatype = dict_data['datatype']
            elif type == 'Edit Bone':
                col_data.subtype = dict_data['subtype']
                col_data.default = dict_data['default']
                col_data.maxlen = dict_data['maxlen']
            elif type == 'Pose Bone':
                col_data.subtype = dict_data['subtype']
                col_data.default = dict_data['default']
                col_data.maxlen = dict_data['maxlen']
            elif type == 'Edit Bone Set':
                col_data.subtype = dict_data['subtype']
                col_data.default = dict_data['default']
                col_data.maxlen = dict_data['maxlen']
            elif type == 'Pose Bone Set':
                col_data.subtype = dict_data['subtype']
                col_data.default = dict_data['default']
                col_data.maxlen = dict_data['maxlen']
    var_collection = bpy.context.scene.ctl_prop_var_collection
    var_collection.clear()
    for dict in dict_list:
        if len(dict) != 0:
            var = var_collection.add()
            var.id = dict['id']
            var.name = dict['name']
            var.type = dict['type']
            var.description = dict['description']
            var.disappear_if = dict['disappear_if']
            var.disable_if = dict['disable_if']
            var.emboss = dict['emboss']
            var.expand = dict['expand']
            var.slider = dict['slider']
            var.toggle = dict['toggle']
            var.toggle = dict['toggle']
            var.separator = dict['separator']
            var.update_file = get_enum_from_tuple(dict['update_file'])
            ctl_variable_register(var.id, var.type)
            # print('dictectory_to_collection, id : ', var.id)
            col_data = ctl_get_var(var.id, 'fn-set_setup_variable_list()')
            dict_data = dict['data']
            get_load_data(dict_data, col_data, var.type)
            ctl_check_duplicate_name_B5648('', var, var_collection)


def ctl_unregister_tool_variables(tool):

    def unregister_variables(tool):
        tool_name = 'ctl_' + processed_name(tool)
        class_name = tool_name.capitalize()
        class_prop = f'bpy.types.PropertyGroup.bl_rna_get_subclass_py("{class_name}")'
        class_unregister_code = f'bpy.utils.unregister_class({class_prop})'
        tool_unregister_code = f'del bpy.types.Scene.{tool_name}'
        try:
            exec(tool_unregister_code)
        except:
            pass
        try:
            exec(class_unregister_code)
        except:
            pass
    if tool == '':
        tool = 'test'
    if tool in variables and isinstance(variables[tool], dict) and len(variables[tool]) != 0 and isinstance(variables[tool], list):
        unregister_variables(tool)


okay_enum_variable = []


def ctl_register_tool_variables(tool):
    print('registering tool : ', tool)

    def get_file_data(file_tuple):
        if (isinstance(file_tuple, list) or isinstance(file_tuple, tuple)) and len(file_tuple) == 2:
            line_list = file_tuple[1]
            if isinstance(line_list, list) and len(line_list) > 0:
                file_code = '\n'.join(line_list)
                if file_code != '':
                    return (True, file_code)
        return (False, '')

    def get_pre_enum_code(var):
        global okay_enum_variable
        pre_code = ''
        enum_code = get_enum_code(var['id'], tool)
        if enum_code != '':
            okay_enum_variable.append(var['name'])
            pre_code = enum_code + '\n'
        return pre_code

    def get_variable_code(var):

        def get_min_max(data):
            attributes = ''
            if data["use_min"]:
                attributes = f'min={data["min"]}'
            if data["use_max"]:
                attributes = f'{attributes}, max={data["max"]}'
            if data["use_soft_min"]:
                attributes = f'{attributes}, soft_min={data["soft_min"]}'
            if data["use_soft_max"]:
                attributes = f'{attributes}, soft_max={data["soft_max"]}'
            if attributes != '':
                attributes = ', ' + attributes
            return attributes
        name = processed_name(var["name"])

        def get_enum_attributes(data):
            global okay_enum_variable
            options = ''
            attributes ='items=[]'
            if data['is_dynamic']:
                if var['name'] in okay_enum_variable:
                    attributes = f"items=ctl_enum_items_{name}"
                else:
                    attributes = "items=[]"
            else:
                list = get_items_list(data['items'])
                if list != '':
                    attributes = f"items={list}"
                else:
                    attributes = f"items=[]"
            if data['is_multiple']:
                options = '"ENUM_FLAG"'
                # attributes = f"{attributes}, options={{'ENUM_FLAG'}}"
            return (attributes, options)
        options = ''
        type = var["type"]
        data = var['data']
        if type == 'String' or type == 'Edit Bone' or type == 'Pose Bone' or type == 'Edit Bone Set' or type == 'Pose Bone Set':
            attributes = f'default="{data["default"]}", subtype="{data["subtype"]}", maxlen={data["maxlen"]}'
        elif type == 'Boolean':
            attributes = f'default={data["default"]}'
        elif type == 'Float':
            attributes = f'default={data["default"]}, subtype="{data["subtype"]}", unit="{data["unit"]}", step={data["step"]}, precision={data["precision"]}{get_min_max(data)}'
        elif type == 'Integer':
            attributes = f'default={data["default"]}, subtype="{data["subtype"]}"{get_min_max(data)}'
        elif type == 'Enum':
            (attributes, opts) = get_enum_attributes(data)
            options = options + ', ' + opts
        elif type == 'Pointer':
            attributes = f'type=bpy.types.{data["datatype"]}'
        else:
            return f'# unable to register type : {type}'
        common = f'name="{var["name"]}", description="{var["description"]}", options={{"HIDDEN"{options}}}'
        (has_data, file_data) = get_file_data(var["update_file"])
        update = ''
        if has_data:
            update = f", update=ctl_update_var_{processed_name(var['name'])}"
        prop_type = ctl_get_var_property_type(type)
        attributes = f'{common}, {attributes}{update}'
        return f'{name} : bpy.props.{prop_type}({attributes})'

    def get_class_code(class_name, variables):
        global okay_enum_variable
        okay_enum_variable = []
        class_code = ''
        for var in variables:
            if var["type"] == 'Enum' and var['data']['is_dynamic']:
                class_code = class_code + '\n' + get_pre_enum_code(var)
        for var in variables:
            if "update_file" in var:
                (has_data, file_data) = get_file_data(var["update_file"])
                if has_data:
                    class_code = class_code + '\n' + get_update_code(file_data, var, tool)
        class_code = class_code + f'class {class_name}(bpy.types.PropertyGroup):'
        for var in variables:
            var_code = get_variable_code(var)
            class_code = f'{class_code}\n    {var_code}'
        return class_code

    def register_variables(tool_name):
        global okay_enum_variable
        global tool_data_9645
        if tool_name not in tool_data_9645:
            tool_data_9645[tool_name] = {}
        tool_prop_name = 'ctl_' + processed_name(tool_name)
        class_name = tool_prop_name.capitalize()
        class_register_code = f'bpy.utils.register_class({class_name})'
        tool_register_code = f'bpy.types.Scene.{tool_prop_name} = bpy.props.PointerProperty(type={class_name})'
        class_code = get_class_code(class_name, variables[tool_name])
        register_code = f'{class_code}\n\n{class_register_code}\n{tool_register_code}\n'
        # print('')
        # print('<-------------------------', tool_name)
        ctl_run_code_with_functions(None, None, tool_name, register_code, f'Registering Tool Variables {tool_name}', False)
    if tool == '':
        tool = 'test'
    if tool in variables and len(variables[tool]) != 0:
        register_variables(tool)


def ctl_variable_attach_data(column, data, id, type):
    if data is not None:
        if type == 'String' or type == 'Edit Bone' or type == 'Pose Bone' or type == 'Edit Bone Set' or type == 'Pose Bone Set':
            column.prop(data, 'subtype', text='Subtype ', icon_value=0, emboss=True)
            column.prop(data, 'default', text='Default ', icon_value=0, emboss=True)
            column.prop(data, 'maxlen', text='Maxlen ', icon_value=0, emboss=True)
        elif type == 'Boolean':
            column.prop(data, 'default', text='Default ', icon_value=0, emboss=True)
        elif type == 'Integer':
            column.prop(data, 'subtype', text='Subtype ', icon_value=0, emboss=True)
            column.separator(factor=0.5)
            column.prop(data, 'default', text='Default ', icon_value=0, emboss=True)
            column.separator(factor=0.5)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_min', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_min
            row2.prop(data, 'min', text='Min ', icon_value=0, emboss=True)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_max', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_max
            row2.prop(data, 'max', text='Max ', icon_value=0, emboss=True)
            column.separator(factor=0.5)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_soft_min', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_soft_min
            row2.prop(data, 'soft_min', text='Soft Min ', icon_value=0, emboss=True)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_soft_max', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_soft_max
            row2.prop(data, 'soft_max', text='Soft Max ', icon_value=0, emboss=True)
        elif type == 'Float':
            column.prop(data, 'subtype', text='Subtype ', icon_value=0, emboss=True)
            column.prop(data, 'unit', text='Unit ', icon_value=0, emboss=True)
            column.separator(factor=0.5)
            column.prop(data, 'default', text='Default ', icon_value=0, emboss=True)
            column.prop(data, 'step', text='Step ', icon_value=0, emboss=True)
            column.prop(data, 'precision', text='Precision ', icon_value=0, emboss=True)
            column.separator(factor=0.5)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_min', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_min
            row2.prop(data, 'min', text='Min ', icon_value=0, emboss=True)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_max', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_max
            row2.prop(data, 'max', text='Max ', icon_value=0, emboss=True)
            column.separator(factor=0.5)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_soft_min', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_soft_min
            row2.prop(data, 'soft_min', text='Soft Min ', icon_value=0, emboss=True)
            row = column.row(heading='', align=True)
            row.prop(data, 'use_soft_max', text='', icon_value=0, emboss=True)
            row2 = row.row(heading='', align=True)
            row2.active = data.use_soft_max
            row2.prop(data, 'soft_max', text='Soft Max ', icon_value=0, emboss=True)
        elif type == 'Enum': # TODO <--- enum interface
            column.prop(data, 'is_multiple', text='Is_multiple ', icon_value=0, emboss=True)
            column.prop(data, 'is_dynamic', text='Is_dynamic ', icon_value=0, emboss=True)
            if not data.is_dynamic:
                column.prop(data, 'items', text='Items ', icon_value=0, emboss=True)
            else:
                row = column.row(heading='', align=True)
                row.operator_context = "INVOKE_DEFAULT"
                row.prop(data, 'file', text='File ', icon_value=0, emboss=True)
                op = row.operator('ctl.load_enum_file', text='', icon_value=707, emboss=True, depress=False)
                op.id = id
                if bpy.context.scene.ctl_prop_switch_file_live:
                    op = row.operator('ctl.switch_file_in_editor', text='', icon_value=256, emboss=True, depress=False)
                    op.name = data.file.name if data.file is not None else ''
                row = column.row(heading='', align=True)
                row.operator_context = "INVOKE_DEFAULT"
                row.prop(data, 'function', text='Fn ', icon_value=0, emboss=True)
                op = row.operator('ctl.add_enum_function', text='', icon_value=31, emboss=True, depress=False)
                op.id = id
        elif type == 'Pointer':
            column.prop(data, 'datatype', text='Data Type ', icon_value=0, emboss=True)


class CTL_GROUP_ctl_variables_group(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty(name='Id', description='', default='', subtype='NONE', maxlen=4, update=ctl_update_variable_from_property)
    name: bpy.props.StringProperty(name='Name', description='', default='Variable', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)
    type: bpy.props.EnumProperty(name='Type', description='', items=ctl_variable_type_enum_items, update=ctl_variable_type_update)
    description: bpy.props.StringProperty(name='Description', description='', default='', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)
    disappear_if: bpy.props.StringProperty(name='Disappear If Condition', description='', default='', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)
    disable_if: bpy.props.StringProperty(name='Disable If Condition', description='', default='', subtype='NONE', maxlen=0, update=ctl_update_variable_from_property)
    update_file: bpy.props.PointerProperty(name='Update File', description='', type=bpy.types.Text, update=ctl_update_variable_from_property)
    emboss: bpy.props.BoolProperty(name='Emboss', description='', default=True, update=ctl_update_variable_from_property)
    expand: bpy.props.BoolProperty(name='Expand', description='', default=False, update=ctl_update_variable_from_property)
    slider: bpy.props.BoolProperty(name='Slider', description='', default=False, update=ctl_update_variable_from_property)
    toggle: bpy.props.BoolProperty(name='Toggle', description='', default=False, update=ctl_update_variable_from_property)
    separator: bpy.props.FloatProperty(name='Separator', description='Separator for down', default=0.0, subtype='NONE', unit='NONE', step=2, precision=3, update=ctl_update_variable_from_property)


class CTL_GROUP_ctl_list_item(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', description='', default='Variable', subtype='NONE', maxlen=0)
    is_open: bpy.props.BoolProperty(name='Is Open', description='', default=False)
    is_selected: bpy.props.BoolProperty(name='Is Selected', description='', default=False)


def ctl_update_file_group(self, context):
    if self.pointer is not None:
        self.name = self.pointer.name


class CTL_GROUP_ctl_file_group(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', description='', default='', subtype='NONE', maxlen=0)
    pointer: bpy.props.PointerProperty(name='File Pointer', description='', type=bpy.types.Text, update=ctl_update_file_group)


def register_ctl():
    scene = bpy.context.scene
    # global _icons
    # _icons = bpy.utils.previews.new()
    bpy.utils.register_class(CTL_GROUP_ctl_variables_group)
    bpy.utils.register_class(CTL_GROUP_ctl_file_group)
    bpy.utils.register_class(CTL_GROUP_var_string_group)
    bpy.utils.register_class(CTL_GROUP_var_bool_group)
    bpy.utils.register_class(CTL_GROUP_var_float_group)
    bpy.utils.register_class(CTL_GROUP_var_int_group)
    bpy.utils.register_class(CTL_GROUP_var_enum_group)
    bpy.utils.register_class(CTL_GROUP_var_pointer_group)
    # bpy.utils.register_class(CTL_GROUP_var_common_group)
    # bpy.types.Scene.ctl_var_common = bpy.props.PointerProperty(name='Undo File', description='', type=CTL_GROUP_var_common_group)
    bpy.types.Scene.ctl_prop_setup_mode = bpy.props.EnumProperty(name='Mode', description='', items=[('Create', 'Create', '', 0, 0), ('Update', 'Update', '', 0, 1)], update=ctl_update_ctl_prop_setup_mode)
    bpy.types.Scene.ctl_prop_create_group_set = bpy.props.EnumProperty(name='Group Set for Create', description='', items=ctl_prop_create_group_set_items)
    if bpy.context.scene.ctl_prop_create_group_set is None or bpy.context.scene.ctl_prop_create_group_set == '':
        try: bpy.context.scene.ctl_prop_create_group_set = '--- Select ---'
        except: pass
    bpy.types.Scene.ctl_prop_group_set = bpy.props.EnumProperty(name='Group Set for Create', description='', items=ctl_prop_group_set_items)
    bpy.types.Scene.ctl_prop_tool_set = bpy.props.EnumProperty(name='Tool Set', description='', items=ctl_prop_tool_set_enum_items, update=ctl_update_ctl_prop_tool_set)
    bpy.types.Scene.ctl_prop_new_tool = bpy.props.StringProperty(name='Name Create', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Scene.ctl_prop_new_group = bpy.props.StringProperty(name='New Group', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Scene.ctl_prop_tool_description = bpy.props.StringProperty(name='Description', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Scene.ctl_prop_tool_icon = bpy.props.StringProperty(name='Tool Icon', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Scene.ctl_prop_pie_space = bpy.props.EnumProperty(name='Space', description='', items=ctl_prop_pie_space_enum_items)
    bpy.types.Scene.ctl_prop_setup_is_open = bpy.props.BoolProperty(name='is setup open', description='', default=False)
    bpy.types.Scene.ctl_prop_tool_type = bpy.props.EnumProperty(name='Tool Type', description='', items=[('SIMPLE', 'Simple', '', 0, 0), ('CUSTOM', 'Custom', '', 0, 1)])
    bpy.types.Scene.ctl_prop_var_is_open = bpy.props.BoolProperty(name='is var open', description='', default=False)
    bpy.types.Scene.ctl_prop_var_collection = bpy.props.CollectionProperty(name='Variables Collection', description='', type=CTL_GROUP_ctl_variables_group)
    bpy.types.Scene.ctl_prop_active_var_index = bpy.props.IntProperty(name='Active Var Index', description='', default=0, subtype='NONE')
    bpy.types.Scene.ctl_prop_file_is_open = bpy.props.BoolProperty(name='is File Open', description='', default=False)
    bpy.types.Scene.ctl_prop_file_collection = bpy.props.CollectionProperty(name='File Collection', description='', type=CTL_GROUP_ctl_file_group)
    bpy.types.Scene.ctl_prop_active_file_index = bpy.props.IntProperty(name='Active File Index', description='', default=0, subtype='NONE', update=ctl_update_ctl_prop_active_file_index_54956)
    bpy.types.Scene.ctl_prop_testing_is_open = bpy.props.BoolProperty(name='Testing Is Open', description='', default=False)
    bpy.types.Scene.ctl_prop_switch_file_live = bpy.props.BoolProperty(name='Live Switch File', description='', default=False, update=ctl_update_ctl_prop_switch_file_live)
    bpy.types.Scene.ctl_prop_pie_enabled = bpy.props.BoolProperty(name='Add to Pie', description='', default=False)
    # bpy.types.Scene.ctl_prop_undo_file = bpy.props.PointerProperty(name='Undo File', description='', type=bpy.types.Text)
    bpy.types.Scene.ctl_prop_undo_file2 = bpy.props.PointerProperty(name='Undo File', description='', type=bpy.types.Text)
    bpy.types.Scene.ctl_prop_setup_keep_file = bpy.props.BoolProperty(name='is keep file', description='', default=True)
    bpy.types.Scene.ctl_prop_isolate_testing_mode = bpy.props.BoolProperty(name='Isolate Testing Mode', description='', default=False)
    bpy.types.Scene.ctl_prop_is_edit_mode = bpy.props.BoolProperty(name='Edit Mode', description='', default=False)
    bpy.types.Scene.ctl_prop_is_rename_mode = bpy.props.BoolProperty(name='Rename Mode', description='', default=False)
    bpy.types.Scene.ctl_prop_is_delete_mode = bpy.props.BoolProperty(name='Delete Mode', description='', default=False)
    bpy.types.Scene.ctl_prop_is_reorder_mode = bpy.props.BoolProperty(name='Reorder Mode', description='', default=False)
    bpy.types.Scene.ctl_prop_is_show_done = bpy.props.BoolProperty(name='Show Done', description='', default=False)
    bpy.types.Scene.ctl_prop_var_display_type = bpy.props.EnumProperty(name='Var Display Type', description='', items=[('DATA', 'Data', '', 0, 0), ('OTHERS', 'Others', '', 0, 1)])
    bpy.utils.register_class(CTL_OT_Remove_File_C67B0)
    bpy.utils.register_class(CTL_OT_Move_File_22Dd8)
    bpy.utils.register_class(CTL_OT_Add_File_A05Dc)
    bpy.utils.register_class(CTL_UL_display_collection_list_7DA87)
    bpy.utils.register_class(CTL_MT_EA721)
    bpy.utils.register_class(CTL_OT_RELOAD_TOOL_LIST)
    bpy.utils.register_class(CTL_OT_REMOVE_TOOL)
    bpy.utils.register_class(CTL_OT_EDIT_TOOL)
    bpy.utils.register_class(CTL_OT_MOVE_GROUP_OR_TOOL)
    bpy.utils.register_class(CTL_OT_RELOAD_ENUM_FILE)
    bpy.utils.register_class(CTL_OT_CLEAR_TOOL_FIELDS)
    bpy.utils.register_class(CTL_OT_Pick_Selected_27Dd5)
    bpy.utils.register_class(CTL_UL_display_collection_list_F34BC)
    bpy.utils.register_class(CTL_OT_Add_Variable_30407)
    bpy.utils.register_class(CTL_OT_Remove_Variable_265A2)
    bpy.utils.register_class(CTL_OT_Move_Variable_B83Ed)
    bpy.utils.register_class(CTL_OT_Create_Tool_28Cc0)
    bpy.utils.register_class(CTL_OT_ADD_ENUM_FUNCTION)
    bpy.utils.register_class(CTL_OT_Clear_Setup_Data)
    bpy.utils.register_class(CTL_OT_LOAD_TOOL_FILE)
    bpy.utils.register_class(CTL_OT_LOAD_UNDO_FILE)
    bpy.utils.register_class(CTL_OT_LOAD_UPDATE_FILE)
    bpy.utils.register_class(CTL_OT_SWITCH_FILE_IN_EDITOR)
    bpy.utils.register_class(CTL_OT_LOAD_ENUM_FILE)
    bpy.utils.register_class(CTL_OT_LOAD_ALL_TOOL_FILES)
    bpy.utils.register_class(CTL_OT_RUN_TOOL)
    bpy.utils.register_class(CTL_OT_CLEAR_DATA)
    bpy.utils.register_class(CTL_OT_RUN_UNDO_TOOL)
    bpy.utils.register_class(CTL_OT_RELOAD_CUSTOM_TOOL)
    bpy.utils.register_class(CTL_OT_COPY_FOLDER_PATH)
    bpy.utils.register_class(CTL_OT_REGISTER_CUSTOM_TOOL)
    bpy.utils.register_class(CTL_OT_UNREGISTER_CUSTOM_TOOL)
    for var in bpy.context.scene.ctl_prop_var_collection:
        try:
            ctl_variable_register(var.id, var.type)
        except:
            pass
    bpy.utils.register_class(CTL_GROUP_ctl_list_item)
    ctl_register_tool_list()
    try: ctl_load_setup_data_5638()
    except: pass
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'T', 'ANY',
        ctrl=True, alt=True, shift=False, repeat=False)
    kmi.properties.name = 'CTL_MT_EA721'
    addon_keymaps['C5CE1'] = (km, kmi)


#bpy.context.scene.sn.addon_unregister.append(unregister)
#register()


def get_ctl_path():
    folder = 'dev_addons\\ctl_tools_old'
    path_high = bpy.utils.user_resource('SCRIPTS', path = "")
    path_list = path_high.split('\\')
    path_list.pop(-1)
    path_list.pop(-1)
    path_list.append(folder)
    path_main = '\\'.join(path_list)
    if not os.path.isdir(path_main):
        os.mkdir(path_main)
    return path_main


def processed_name(name, is_upper=False):
    new_name = ''.join(e for e in name if e.isalnum() or e == ' ' or e == '_').strip().replace(' ', '_')
    if is_upper:
        return new_name
    else:
        return new_name.casefold()


def get_file_data(file_name):
    data = ''
    ctl_path = get_ctl_path()
    file_path = ctl_path + '\\' + file_name
    if os.path.exists(file_path):
        file = None
        try:
            file = open(file_path, 'r')
            data = file.read()
        except:
            print('Error : In Reading File, ', file_path)
            traceback.print_exc()
        file.close()
    return data


def set_file_data(file_name, data):
    ctl_path = get_ctl_path()
    file_path = ctl_path + '\\' + file_name
    file = None
    if os.path.exists(file_path):
        file = open(file_path, 'w')
    else:
        file = open(file_path, 'x')
    if file is not None:
        try:
            file.write(data)
        except:
            print('Error : In Writing File, ', file_path)
            traceback.print_exc()
        file.close()


def get_file_list_from_tools_dir():

    def is_file_verified(name):
        return name.endswith('.json') and len(name.split('.')) == 5 and not name.lower().startswith('00.setup')
    ctl_path = get_ctl_path()
    tools_path = ctl_path + '\\tools'
    file_list = os.listdir(tools_path)
    file_list = [file_name for file_name in file_list if is_file_verified(file_name)]
    return sorted(file_list)


def convert_tool_list_to_config_dict(tlist):
    tdict = {}
    for item in tlist:
        (group, tool_list) = item
        new_tool_list = [tool_tuple[0] for tool_tuple in tool_list]
        tdict[group] = new_tool_list
    return tdict


# def write_tool_list(tlist):
#     file_name = 'group_config.json'
#     config_dict = convert_tool_list_to_config_dict(tlist)
#     set_file_data(file_name, json.dumps(config_dict, indent = 4))


def create_tool_list():
    # print('creating tool list...')
    tool_list = []

    def get_group_tool(fname):

        def extract_name(name):
            return name.replace('_', ' ').casefold().title()
        temp = fname.split('.')
        group = extract_name(temp[1])
        tool = extract_name(temp[3])
        return (group, tool)

    def add_in_tool_list(group, tool, fname):
        file_name = 'tools\\' + fname
        json_data = get_file_data(file_name)
        file_data = {}
        try:
            file_data = json.loads(json_data)
        except:
            print('JSON Data is Corrupted...')
        if len(file_data) > 0:
            tool_data = (tool, file_data)
            is_found = False
            for idx in range(len(tool_list)):
                (gname, tools) = tool_list[idx]
                if gname == group:
                    is_found = True
                    tools.append(tool_data)
                    break
            if not is_found:
                tool_list.append((group, [tool_data]))
    file_list = get_file_list_from_tools_dir()
    for fname in file_list:
        (group, tool) = get_group_tool(fname)
        add_in_tool_list(group, tool, fname)
    return tool_list


################################### TOOL SUB PANEL ###########################################


def ctl_tool_data_to_directory_list(tool_name, var_list):

    def get_data_directory(data, type):
        if type == 'String':
            return {
                'subtype' : data['subtype'],
                'default' : data['default'],
                'maxlen' : data['maxlen'],
            }
        elif type == 'Boolean':
            return {
                'default' : data['default'],
            }
        elif type == 'Integer':
            return {
                'subtype' : data['subtype'],
                'default' : data['default'],
                'use_min' : data['use_min'],
                'use_max' : data['use_max'],
                'use_soft_min' : data['use_soft_min'],
                'use_soft_max' : data['use_soft_max'],
                'min' : data['min'],
                'max' : data['max'],
                'soft_min' : data['soft_min'],
                'soft_max' : data['soft_max'],
            }
        elif type == 'Float':
            return {
                'subtype' : data['subtype'],
                'unit' : data['unit'],
                'default' : data['default'],
                'step' : data['step'],
                'precision' : data['precision'],
                'use_min' : data['use_min'],
                'use_max' : data['use_max'],
                'use_soft_min' : data['use_soft_min'],
                'use_soft_max' : data['use_soft_max'],
                'min' : data['min'],
                'max' : data['max'],
                'soft_min' : data['soft_min'],
                'soft_max' : data['soft_max'],
            }
        elif type == 'Enum':
            return {
                'is_multiple' : data['is_multiple'],
                'is_dynamic' : data['is_dynamic'],
                'items' : data['items'],
                'file' : data['file'],
            }
        elif type == 'Pointer':
            return {
                'datatype' : data['datatype'],
            }
        elif type == 'Edit Bone':
            return {
                'subtype' : data['subtype'],
                'default' : data['default'],
                'maxlen' : data['maxlen'],
            }
        elif type == 'Pose Bone':
            return {
                'subtype' : data['subtype'],
                'default' : data['default'],
                'maxlen' : data['maxlen'],
            }
        elif type == 'Edit Bone Set':
            return {
                'subtype' : data['subtype'],
                'default' : data['default'],
                'maxlen' : data['maxlen'],
            }
        elif type == 'Pose Bone Set':
            return {
                'subtype' : data['subtype'],
                'default' : data['default'],
                'maxlen' : data['maxlen'],
            }
    if tool_name == '':
        return False
    list = []
    for var in var_list:
        if ('id' in var) and ('name' in var) and ('type' in var) and ('data' in var):
            if (var['id'] != '') and (var['name'] != '') and (var['type'] != '') and len(var['data']) > 0:
                dir = {
                    'id': var['id'],
                    'name': var['name'],
                    'type': var['type'],
                    'description': var['description'],
                    'disappear_if': var['disappear_if'],
                    'disable_if': var['disable_if'],
                    'update_file': var['update_file'],
                    'emboss': var['emboss'],
                    'expand': var['expand'],
                    'slider': var['slider'],
                    'toggle': var['toggle'],
                    'separator': var['separator'],
                    'data': get_data_directory(var['data'], var['type'])
                }
                list.append(dir)
    variables[tool_name] = list


def ctl_load_variables(tool_data):
    (tool_name, tool_dict) = tool_data
    tool_type = tool_dict['type']
    if tool_type == 'SIMPLE' and 'variables' in tool_dict:
        var_list = tool_dict['variables']
        is_okay = True
        try:
            ctl_tool_data_to_directory_list(tool_name, var_list) #<--- Variable(tool)
        except:
            is_okay = False
            traceback.print_exc()
        if is_okay:
            ctl_register_tool_variables(tool_name)


def ctl_register_property(prop_name, class_name):
    prop_name = processed_name(prop_name)
    register_code = f'bpy.types.Scene.{prop_name} = bpy.props.PointerProperty(type={class_name})'
    try:
        exec(register_code)
    except Exception as e:
        print('ERROR : In Registering Property')
        print('Code :', register_code)
        traceback.print_exc()


def ctl_unregister_property(prop_name):
    prop_name = processed_name(prop_name)
    unregister_code = f'del bpy.types.Scene.{prop_name}'
    try:
        exec(unregister_code, {'bpy': bpy})
    except Exception as e:
        print('ERROR : In UnRegistering Property')
        print('Code :', unregister_code)
        traceback.print_exc()


#TODO Sub Panel


def ctl_register_group_sub_panel(index, group_data):
    (group_name, tool_data_list) = group_data
    group_name_p = processed_name(group_name)
    group_p_upper = group_name_p.upper()
    class_name = 'CTL_PT_MAIN_PANEL'
    class_prop = f'bpy.types.Panel.bl_rna_get_subclass_py("{class_name}")'
    sub_panel_code = get_file_data('group_sub_class.py')
    sub_panel_code = f"{sub_panel_code}".format(**locals())
    try:
        local_dict = {
            'bpy': bpy,
            'group': group_name,
            'get_global_tool_list' : get_global_tool_list,
            'get_is_any_group_selected' : get_is_any_group_selected,
            'processed_name': processed_name,
            'ctl_tool_header_CA842' : ctl_tool_header_CA842,
            'ctl_setup_simple_tool_interface_A85ED' : ctl_setup_simple_tool_interface_A85ED,
            'ctl_setup_custom_tool_interface_A85ED' : ctl_setup_custom_tool_interface_A85ED,
        }
        exec(sub_panel_code, local_dict)
    except Exception as e:
        print('ERROR : In Registering Group Sub Class')
        print('Code :', sub_panel_code)
        traceback.print_exc()


global_tool_list = create_tool_list()
temp_is_selected = False


def get_is_any_group_selected():
    global global_tool_list
    for group_data in global_tool_list:
        (group_name, tool_data_list) = group_data
        group_name_p = processed_name(group_name)
        code = f'global temp_is_selected\ntemp_is_selected = bpy.context.scene.ctl_group_{group_name_p}.is_selected'
        exec(code)
        global temp_is_selected
        if temp_is_selected:
            return True
    return False


def get_global_tool_list(group):

    def get_tool_list(tool_data_list):
        tool_list = []
        for item in tool_data_list:
            (tool_name, tool_data) = item
            if tool_data is not None and 'type' in tool_data:
                has_variable = 'variables' in tool_data and len(tool_data['variables']) > 0 
                has_undo_data = 'undo_file' in tool_data and len(tool_data['undo_file']) == 2 and tool_data['undo_file'][0] != '' and isinstance(tool_data['undo_file'][1], list) and len(tool_data['undo_file'][1]) > 0
                tool_list.append((tool_name, tool_data['type'], has_variable, has_undo_data))
        return tool_list
    global global_tool_list
    for group_data in global_tool_list:
        (group_name, tool_data_list) = group_data
        if group_name == group:
            return get_tool_list(tool_data_list)
    return []


def ctl_update_ctl_list_item(type, group_name, tool_name=''):
    group_processed = processed_name(group_name)
    if type == 'GROUP':
        path = f'{group_name}'
        exec(f'bpy.context.scene.ctl_group_{group_processed}.path = path', {'bpy': bpy, 'path': path})
        exec(f'bpy.context.scene.ctl_group_{group_processed}.name = group_name', {'bpy': bpy, 'group_name': group_name})
    elif type == 'TOOL':
        tool_processed = processed_name(tool_name)
        path = f'{group_name}@@@{tool_name}'
        exec(f'bpy.context.scene.ctl_tool_{tool_processed}.path = path', {'bpy': bpy, 'path': path})
        exec(f'bpy.context.scene.ctl_tool_{tool_processed}.name = tool_name', {'bpy': bpy, 'tool_name': tool_name})


def ctl_register_tool_list():
    global global_tool_list
    for group_data in global_tool_list:
        (group_name, tool_data_list) = group_data
        group_processed = processed_name(group_name)
        prop_name = 'ctl_group_' + group_processed
        class_name = 'CTL_GROUP_ctl_list_item'
        ctl_register_property(prop_name, class_name)
        ctl_update_ctl_list_item('GROUP', group_name)
        for tool_data in tool_data_list:
            (tool_name, tool_dict) = tool_data
            tool_processed = processed_name(tool_name)
            prop_name = 'ctl_tool_' + tool_processed
            class_name = 'CTL_GROUP_ctl_list_item'
            ctl_register_property(prop_name, class_name)
            ctl_update_ctl_list_item('TOOL', group_name, tool_name)
            ctl_load_variables(tool_data)
    for idx in range(len(global_tool_list)):
        group_data = global_tool_list[idx]
        ctl_register_group_sub_panel(idx, group_data)


def unregister_sub_panel(group_name):
    group_processed = processed_name(group_name).upper()
    class_name = f'CTL_PT_SUB_PANEL_{group_processed.upper()}'
    class_prop = f'bpy.types.Panel.bl_rna_get_subclass_py("{class_name}")'
    class_unregister_code = f'bpy.utils.unregister_class({class_prop})'
    try:
        exec(class_unregister_code)
    except:
        print('ERROR : In Unregistering SubPanel')
        print('Code :', class_unregister_code)


def ctl_unregister_tool_list():
    global global_tool_list
    for group_data in global_tool_list:
        (group, tool_data_list) = group_data
        unregister_sub_panel(group)
        for tool_data in tool_data_list:
            (tool, tool_dict) = tool_data
            prop_name = 'ctl_tool_' + tool
            ctl_unregister_property(prop_name)
        prop_name = 'ctl_group_' + group
        ctl_unregister_property(prop_name)


def write_tool_order_to_file():

    def rename_file(from_name, to_name):
        if from_name != to_name:
            ctl_path = get_ctl_path()
            tools_path = ctl_path + '\\tools'
            from_path = tools_path + '\\' + from_name
            to_path = tools_path + '\\' + to_name
            os.rename(from_path, to_path)

    def order_group(group_name, group_order, tool_name, tool_order):
        group_name_p = processed_name(group_name)
        tool_name_p = processed_name(tool_name)
        file_list = get_file_list_from_tools_dir()
        g_num = f"{group_order:02d}"
        t_num = f"{tool_order:02d}"
        for file_name in file_list:
            flist = file_name.split('.')
            if flist[1] == group_name_p and flist[3] == tool_name_p:
                flist[0] = g_num
                flist[2] = t_num
                new_grp = '.'.join(flist)
                rename_file(file_name, new_grp)
    global global_tool_list
    for group_idx in range(len(global_tool_list)):
        (group_name, tool_data_list) = global_tool_list[group_idx]
        for tool_idx in range(len(tool_data_list)):
            tool_name = tool_data_list[tool_idx][0]
            order_group(group_name, group_idx + 1, tool_name, tool_idx + 1)


group_rename = {}
tool_rename = {}


def ctl_update_list_item(self, context):

    def rename_file(from_name, to_name):
        ctl_path = get_ctl_path()
        tools_path = ctl_path + '\\tools'
        from_path = tools_path + '\\' + from_name
        to_path = tools_path + '\\' + to_name
        os.rename(from_path, to_path)

    def update_group_name(old_name, new_name):
        old_name_p = processed_name(old_name)
        new_name_p = processed_name(new_name)
        file_list = get_file_list_from_tools_dir()
        for file_name in file_list:
            flist = file_name.split('.')
            if len(flist) == 5 and flist[1] == old_name_p:
                flist[1] = new_name_p
                new_grp = '.'.join(flist)
                rename_file(file_name, new_grp)
        global group_rename
        group_rename[old_name] = new_name
        # for idx in range(len(global_tool_list)):
        #     group_data = global_tool_list[idx]
        #     (group_name, tool_data_list) = group_data
        #     if group_name == old_name:
        #         group_data = (new_name, tool_data_list)
        #         global_tool_list[idx] = group_data
        #         break

    def update_tool_name(group, old_name, new_name):
        group_p = processed_name(group)
        old_name_p = processed_name(old_name)
        new_name_p = processed_name(new_name)
        file_list = get_file_list_from_tools_dir()
        for file_name in file_list:
            flist = file_name.split('.')
            if len(flist) == 5 and flist[1] == group_p and flist[3] == old_name_p:
                flist[3] = new_name_p
                new_tl = '.'.join(flist)
                rename_file(file_name, new_tl)
        global tool_rename
        tool_rename[old_name] = new_name
        # for idx in range(len(global_tool_list)):
        #     group_data = global_tool_list[idx]
        #     (group_name, tool_data_list) = group_data
        #     if group_name == group:
        #         for idx2 in range(len(tool_data_list)):
        #             tool_data = tool_data_list[idx2]
        #             (tool_name, tool_dict) = tool_data
        #             if tool_name == old_name:
        #                 tool_data_list[idx2] = (new_name, tool_dict)
        #                 global_tool_list[idx] = (group_name, tool_data_list)
        #                 break
    list = self.path.split('@@@')
    if len(list) == 1: # GROUP
        group_name = list[0]
        if self.name != group_name:
            # print("GRP Name Changed...")
            update_group_name(group_name, self.name)
            self.path = self.name
    elif len(list) == 2: # TOOL
        group_name = list[0]
        tool_name = list[1]
        if self.name != tool_name:
            # print("TL Name Changed...")
            update_tool_name(group_name, tool_name, self.name)
            self.path = f'{group_name}@@@{self.name}'


class CTL_GROUP_ctl_list_item(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty(name='Destination Path', description='', default='Default.String', subtype='NONE', maxlen=0)
    name: bpy.props.StringProperty(name='Name', description='', default='Default String', subtype='NONE', maxlen=0, update=ctl_update_list_item)
    is_open: bpy.props.BoolProperty(name='Is Open', description='', default=False)
    is_selected: bpy.props.BoolProperty(name='Is Selected', description='', default=False)


# class SNA_PT_NEW_PANEL_C763F(bpy.types.Panel):
#     bl_label = 'New Panel'
#     bl_idname = 'SNA_PT_NEW_PANEL_C763F'
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_context = ''
#     bl_category = 'New Category'
#     bl_order = 0
#     bl_ui_units_x=0
#     @classmethod
#     def poll(cls, context):
#         return not (False)
#     def draw_header(self, context):
#         layout = self.layout
#     def draw(self, context):
#         layout = self.layout
#         exec("layout.prop(bpy.context.scene, 'ctl_prop_is_change_name', text='', icon_value=742, emboss=True)")
#         exec("layout.prop(bpy.context.scene, 'ctl_prop_is_change_order', text='', icon_value=745, emboss=True)")
#         exec("layout.prop(bpy.context.scene, 'ctl_prop_is_edit_mode', text='', icon_value=197, emboss=True)")
#         exec("layout.prop(bpy.context.scene, 'ctl_prop_is_delete_mode', text='', icon_value=21, emboss=True)")
# def register_ctl():
    # bpy.types.Scene.ctl_prop_is_edit_mode = bpy.props.BoolProperty(name='Is Edit Mode', description='', default=False)
    # bpy.types.Scene.ctl_prop_is_change_name = bpy.props.BoolProperty(name='Is Change Name', description='', default=False)
    # bpy.types.Scene.ctl_prop_is_change_order = bpy.props.BoolProperty(name='Is Change Order', description='', default=False)
    # bpy.types.Scene.ctl_prop_is_delete_mode = bpy.props.BoolProperty(name='Is Delete Mode', description='', default=False)
    # bpy.utils.register_class(SNA_PT_NEW_PANEL_C763F)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(CTL_OT_REGISTER_CTL)
    try: bpy.utils.register_class(CTL_PT_MAIN_PANEL)
    except: pass
    global is_ctl_registered_9042
    try:
        register_ctl()
        is_ctl_registered_9042 = True
    except:
        is_ctl_registered_9042 = False
        print('Panel Will Not Show...')
        traceback.print_exc()
    # is_ctl_registered_9042 = True


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    try:
        # global _icons
        # bpy.utils.previews.remove(_icons)
        # wm = bpy.context.window_manager
        # kc = wm.keyconfigs.addon
        # for km, kmi in addon_keymaps.values():
        #     km.keymap_items.remove(kmi)
        # addon_keymaps.clear()
        ctl_save_setup_data_5638()
        del bpy.types.Scene.ctl_prop_is_edit_mode
        del bpy.types.Scene.ctl_prop_is_delete_mode
        del bpy.types.Scene.ctl_prop_is_reorder_mode
        del bpy.types.Scene.ctl_prop_is_rename_mode
        del bpy.types.Scene.ctl_prop_var_display_type
        del bpy.types.Scene.ctl_prop_setup_is_open
        del bpy.types.Scene.ctl_prop_setup_mode
        del bpy.types.Scene.ctl_prop_group_set
        del bpy.types.Scene.ctl_prop_tool_set
        del bpy.types.Scene.ctl_prop_new_group
        del bpy.types.Scene.ctl_prop_new_tool
        del bpy.types.Scene.ctl_prop_tool_description
        del bpy.types.Scene.ctl_prop_tool_type
        del bpy.types.Scene.ctl_prop_pie_enabled
        del bpy.types.Scene.ctl_prop_tool_icon
        del bpy.types.Scene.ctl_prop_pie_space
        # del bpy.types.Scene.ctl_prop_undo_file
        del bpy.types.Scene.ctl_prop_undo_file2
        del bpy.types.Scene.ctl_prop_is_show_done
        del bpy.types.Scene.ctl_prop_file_is_open
        del bpy.types.Scene.ctl_prop_file_collection
        del bpy.types.Scene.ctl_prop_active_file_index
        del bpy.types.Scene.ctl_prop_switch_file_live
        del bpy.types.Scene.ctl_prop_setup_keep_file
        del bpy.types.Scene.ctl_prop_isolate_testing_mode
        del bpy.types.Scene.ctl_prop_testing_is_open
        for var in bpy.context.scene.ctl_prop_var_collection:
            try:
                ctl_variable_unregister(var.id)
            except:
                pass
        for tool in variables.keys():
            ctl_unregister_tool_variables(tool)
        del bpy.types.Scene.ctl_prop_var_is_open
        del bpy.types.Scene.ctl_prop_var_collection
        del bpy.types.Scene.ctl_prop_active_var_index
        # bpy.utils.unregister_class(CTL_GROUP_var_common_group)
        bpy.utils.unregister_class(CTL_GROUP_var_pointer_group)
        bpy.utils.unregister_class(CTL_GROUP_var_enum_group)
        bpy.utils.unregister_class(CTL_GROUP_var_int_group)
        bpy.utils.unregister_class(CTL_GROUP_var_float_group)
        bpy.utils.unregister_class(CTL_GROUP_var_bool_group)
        bpy.utils.unregister_class(CTL_GROUP_var_string_group)
        bpy.utils.unregister_class(CTL_GROUP_ctl_file_group)
        bpy.utils.unregister_class(CTL_GROUP_ctl_variables_group)
        bpy.utils.unregister_class(CTL_OT_Remove_File_C67B0)
        bpy.utils.unregister_class(CTL_OT_Move_File_22Dd8)
        bpy.utils.unregister_class(CTL_OT_Add_File_A05Dc)
        bpy.utils.unregister_class(CTL_UL_display_collection_list_7DA87)
        bpy.utils.unregister_class(CTL_MT_EA721)
        try: bpy.utils.unregister_class(CTL_PT_MAIN_PANEL)
        except: pass
        bpy.utils.unregister_class(CTL_OT_CLEAR_TOOL_FIELDS)
        bpy.utils.unregister_class(CTL_OT_COPY_FOLDER_PATH)
        bpy.utils.unregister_class(CTL_OT_RELOAD_TOOL_LIST)
        bpy.utils.unregister_class(CTL_OT_REMOVE_TOOL)
        bpy.utils.unregister_class(CTL_OT_EDIT_TOOL)
        bpy.utils.unregister_class(CTL_OT_MOVE_GROUP_OR_TOOL)
        bpy.utils.unregister_class(CTL_OT_RELOAD_ENUM_FILE)
        bpy.utils.unregister_class(CTL_OT_UNREGISTER_CUSTOM_TOOL)
        bpy.utils.unregister_class(CTL_OT_REGISTER_CUSTOM_TOOL)
        bpy.utils.unregister_class(CTL_OT_RELOAD_CUSTOM_TOOL)
        bpy.utils.unregister_class(CTL_OT_RUN_UNDO_TOOL)
        bpy.utils.unregister_class(CTL_OT_RUN_TOOL)
        bpy.utils.unregister_class(CTL_OT_CLEAR_DATA)
        bpy.utils.unregister_class(CTL_OT_LOAD_ALL_TOOL_FILES)
        bpy.utils.unregister_class(CTL_OT_LOAD_TOOL_FILE)
        bpy.utils.unregister_class(CTL_OT_LOAD_UNDO_FILE)
        bpy.utils.unregister_class(CTL_OT_LOAD_ENUM_FILE)
        bpy.utils.unregister_class(CTL_OT_LOAD_UPDATE_FILE)
        bpy.utils.unregister_class(CTL_OT_SWITCH_FILE_IN_EDITOR)
        bpy.utils.unregister_class(CTL_OT_Pick_Selected_27Dd5)
        bpy.utils.unregister_class(CTL_UL_display_collection_list_F34BC)
        bpy.utils.unregister_class(CTL_OT_Add_Variable_30407)
        bpy.utils.unregister_class(CTL_OT_Remove_Variable_265A2)
        bpy.utils.unregister_class(CTL_OT_Move_Variable_B83Ed)
        bpy.utils.unregister_class(CTL_OT_Create_Tool_28Cc0)
        bpy.utils.unregister_class(CTL_OT_ADD_ENUM_FUNCTION)
        bpy.utils.unregister_class(CTL_OT_Clear_Setup_Data)
    except: pass
    bpy.utils.unregister_class(CTL_OT_REGISTER_CTL)
    try:
        ctl_unregister_tool_list()
        bpy.utils.unregister_class(CTL_GROUP_ctl_list_item)
    except: pass
    # bpy.utils.unregister_class(SNA_PT_NEW_PANEL_C763F)
    # del bpy.types.Scene.ctl_prop_is_edit_mode
    # del bpy.types.Scene.ctl_prop_is_delete_mode
    # del bpy.types.Scene.ctl_prop_is_change_order
    # del bpy.types.Scene.ctl_prop_is_change_name
