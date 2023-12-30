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
    "name" : "GLink Addon",
    "author" : "MohitX", 
    "description" : "",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 1),
    "location" : "",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Animation" 
}


import bpy
import bpy.utils.previews
from bpy.app.handlers import persistent




def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0


def string_to_icon(value):
    if value in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].value
    return string_to_int(value)


addon_keymaps = {}
_icons = None
d_viewport_manager_ui = {'sna_operator_deps': None, }
enums_for_glink = {'sna_temp_action_list': [], 'sna_temp_group_list': [], 'sna_temp_fcurve_list': [], }
nodetree = {'sna_filter_list': [], 'sna_is_active_filter': False, 'sna_is_selected_filter': False, 'sna_is_none_filter': True, 'sna_is_filter': False, }
other_panels = {'sna_parent_links': [], 'sna_child_links': [], }
_item_map = dict()


def make_enum_item(_id, name, descr, preview_id, uid):
    lookup = str(_id)+"\0"+str(name)+"\0"+str(descr)+"\0"+str(preview_id)+"\0"+str(uid)
    if not lookup in _item_map:
        _item_map[lookup] = (_id, name, descr, preview_id, uid)
    return _item_map[lookup]


def sna_update_sna_editor_to_fcurve_0505D(self, context):
    sna_updated_prop = self.sna_editor_to_fcurve
    data_path_0_295e2, array_index_1_295e2, is_valid_2_295e2 = sna_get_fcurve_data_1A51D(bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].to_action, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].to_group, sna_updated_prop)
    self.sna_glink_collection[self.sna_editor_link_index].to_data_path = data_path_0_295e2
    self.sna_glink_collection[self.sna_editor_link_index].to_array_index = array_index_1_295e2
    self.sna_glink_collection[self.sna_editor_link_index].is_to_valid = is_valid_2_295e2


def sna_update_sna_editor_to_group_AD22C(self, context):
    sna_updated_prop = self.sna_editor_to_group
    self.sna_glink_collection[self.sna_editor_link_index].to_group = ('' if ('NONE' == sna_updated_prop) else sna_updated_prop)
    bpy.context.object.animation_data.action.sna_editor_to_fcurve = 'NONE'


def sna_update_sna_editor_to_action_D53F1(self, context):
    sna_updated_prop = self.sna_editor_to_action
    self.sna_glink_collection[self.sna_editor_link_index].to_action = ('' if (None == sna_updated_prop) else sna_updated_prop.name)
    bpy.context.object.animation_data.action.sna_editor_to_group = 'NONE'


def sna_update_sna_editor_from_group_A46E2(self, context):
    sna_updated_prop = self.sna_editor_from_group
    self.sna_glink_collection[self.sna_editor_link_index].from_group = ('' if ('NONE' == sna_updated_prop) else sna_updated_prop)
    bpy.context.object.animation_data.action.sna_editor_from_fcurve = 'NONE'


def sna_update_sna_editor_from_fcurve_E87BD(self, context):
    sna_updated_prop = self.sna_editor_from_fcurve
    data_path_0_2e8f3, array_index_1_2e8f3, is_valid_2_2e8f3 = sna_get_fcurve_data_1A51D(bpy.context.object.animation_data.action.name, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].from_group, sna_updated_prop)
    self.sna_glink_collection[self.sna_editor_link_index].from_data_path = data_path_0_2e8f3
    self.sna_glink_collection[self.sna_editor_link_index].from_array_index = array_index_1_2e8f3
    self.sna_glink_collection[self.sna_editor_link_index].is_from_valid = is_valid_2_2e8f3


def sna_glink_list_12FEE():
    parent_links = None
    child_links = None
    old_parent_links = other_panels['sna_parent_links']
    old_child_links = other_panels['sna_child_links']
    #import bpy
    #old_parent_links = []
    #old_child_links = []
    parent_links = []
    child_links = []
    ################################ FUNCTIONS ########################################

    def check_active(list):
        for action_tuple in list:
            (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
            (action_name, action_type) = (action_data[0], action_data[1])
            is_act_deactive = True
            for group_tuple in action_tuple[3]:
                (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                (group_name, group_type) = (group_data[0], group_data[1])
                is_grp_deactive = True
                for fcurve_tuple in group_tuple[2]:
                    (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                    (fc_path, fc_index, fc_label, fc_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
                    is_fc_deactive = True
                    for link_data in link_list:
                        link = link_data[0]
                        if not link.is_deactive:
                            is_act_deactive = False
                            is_grp_deactive = False
                            is_fc_deactive = False
                        if not is_fc_deactive:
                            break
                    fcurve_tuple[1][3] = is_fc_deactive
                group_tuple[1][3] = is_grp_deactive
            action_tuple[2][1] = is_act_deactive

    def get_obj_type(type):
        if type == 'GPENCIL':
            return 'OUTLINER_DATA_GREASEPENCIL'
        elif type == 'LIGHT_PROBE':
            return 'OUTLINER_DATA_LIGHTPROBE'
        elif type == 'SPEAKER':
            return 'OUTLINER_DATA_SPEAKER'
        else:
            return type + '_DATA'

    def get_fcurve_tuple(fcurve_tuple, link):
        (fcurve, group_name, fc_is_open) = fcurve_tuple
        fc_label = sna_create_fcurve_name_B67F8(fcurve.data_path, fcurve.array_index, group_name) if fcurve is not None else ''
        fcurve_data = (fcurve.data_path, fcurve.array_index, fc_label, 'NONE', fcurve) if fcurve is not None else ('', -1, 'No FCurve','ERROR', None)
        return [fcurve_data, fc_is_open, [link]]

    def get_group_tuple(group_tuple, fcurve_tuple, link):
        (group, group_is_open) = group_tuple
        group_data = (group.name, 'NONE', group) if group is not None else ('No Group', 'ERROR', None)
        return [group_data, group_is_open, [get_fcurve_tuple(fcurve_tuple, link)]]

    def get_action_tuple(action_tuple, group_tuple, fcurve_tuple, link):
        (action, obj, action_is_open) = action_tuple
        action_data = (action.name, 'ACTION', action) if action is not None else ('No Action', 'ERROR', None)
        obj_data = (obj.name, get_obj_type(obj.type), obj) if obj is not None else ('No Object', 'INFO', None)
        return [action_data, obj_data, action_is_open, [get_group_tuple(group_tuple, fcurve_tuple, link)]]

    def get_is_open(data, old_list):
        (action, group, fcurve) = data
        act_is_open = [False, False]
    #    action_is_open = (in_manager, is_deactivated)
        grp_is_open = [False, False, False, False]
    #    group_is_open = (in_manager, in_timeline, in_graph, is_deactivated)
        fc_is_open = [False, False, False, False]
    #    fcurve_is_open = (in_manager, in_timeline, in_graph, is_deactivated)
        for action_tuple in old_list:
            (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
            (action_name, action_type) = (action_data[0], action_data[1])
            if (action is None and action_name == 'No Action' and action_type == 'ERROR') or (action is not None and action_name == action.name and action_type == 'ACTION'):
                act_is_open = action_is_open
                for group_tuple in action_tuple[3]:
                    (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                    (group_name, group_type) = (group_data[0], group_data[1])
                    if (group is None and group_name == 'No Group' and group_type == 'ERROR') or (group is not None and group_name == group.name and group_type == 'NONE'):
                        grp_is_open = group_is_open
                        for fcurve_tuple in group_tuple[2]:
                            (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                            (fc_path, fc_index, fc_label, fc_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
                            if (fcurve is None and fc_path == '' and fc_type == 'ERROR') or (fcurve is not None and fc_path == fcurve.data_path and fc_index == fcurve.array_index and fc_type == 'NONE'):
                                fc_is_open = fcurve_is_open
                                break
                        break
                break
        return (act_is_open, grp_is_open, fc_is_open)

    def add_to_list(obj, link, data, list, old_list):
        (action, group, fcurve) = data
        (act_is_open, grp_is_open, fc_is_open) = get_is_open(data, old_list)
    #    print(action.name if action is not None else 'None', group.name if group is not None else 'None', fcurve.data_path if fcurve is not None else 'None')
    #    print(obj.name if obj is not None else 'NONE')
        fc_group_name = group.name if group is not None else ''
        action_found = False
        for action_tuple in list:
            (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
            (action_name, action_type) = (action_data[0], action_data[1])
            if (action is None and action_name == 'No Action' and action_type == 'ERROR') or (action is not None and action_name == action.name and action_type == 'ACTION'):
                action_found = True
                group_found = False
                for group_tuple in action_tuple[3]:
                    (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                    (group_name, group_type) = (group_data[0], group_data[1])
                    if (group is None and group_name == 'No Group' and group_type == 'ERROR') or (group is not None and group_name == group.name and group_type == 'NONE'):
                        group_found = True
                        fcurve_found = False
                        for fcurve_tuple in group_tuple[2]:
                            (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                            (fc_path, fc_index, fc_label, fc_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
                            if (fcurve is None and fc_path == '' and fc_type == 'ERROR') or (fcurve is not None and fc_path == fcurve.data_path and fc_index == fcurve.array_index and fc_type == 'NONE'):
                                fcurve_found = True
                                fcurve_tuple[2].append(link)
                                break
                        if not fcurve_found:
                            group_tuple[2].append(get_fcurve_tuple((fcurve, fc_group_name, fc_is_open), link))
                        break
                if not group_found:
                    action_tuple[3].append(get_group_tuple((group, grp_is_open), (fcurve, fc_group_name, fc_is_open), link))
                break
        if not action_found:
            list.append(get_action_tuple((action, obj, act_is_open), (group, grp_is_open), (fcurve, fc_group_name, fc_is_open), link))

    def check_action(obj, action):
        has_links = True if len(action.sna_glink_collection) != 0 else False
        if has_links:
    #        print(action.name, '<---', obj.name)
            for link_index in range(len(action.sna_glink_collection)):
                link = action.sna_glink_collection[link_index]
                from_group = None
                from_fcurve = None
                to_action = None
                to_group = None
                to_fcurve = None
                from_group = action.groups.get(link.from_group)
                if from_group is not None:
                    for fc in from_group.channels:
                        if fc.data_path == link.from_data_path and fc.array_index == link.from_array_index:
                            from_fcurve = fc
                            break
                to_action = bpy.data.actions.get(link.to_action)
                if to_action is not None:
                    to_group = to_action.groups.get(link.to_group)
                    if to_group is not None:
                        for fc in to_group.channels:
                            if fc.data_path == link.to_data_path and fc.array_index == link.to_array_index:
                                to_fcurve = fc
                                break
                to_obj = None
                if to_action is not None:
                    for o in bpy.data.objects:
                        if o.animation_data is not None and o.animation_data.action is not None and o.animation_data.action.name == to_action.name:
                            to_obj = o
                            break
                link.is_from_valid = True if from_group is not None and from_fcurve is not None else False
                link.is_to_valid = True if to_action is not None and to_group is not None and to_fcurve is not None else False
    #            print(obj.name if obj is not None else 'NONE', to_obj.name if to_obj is not None else "NONE")
                parent_data = (action, from_group, from_fcurve)
                child_data = (to_action, to_group, to_fcurve)
                add_to_list(to_obj, [link, link_index, parent_data], child_data, child_links, old_child_links)
                add_to_list(obj   , [link, link_index, child_data], parent_data, parent_links, old_parent_links)
    ################################ START ########################################
    action_with_no_obj = []
    for index in range(len(bpy.data.actions)):
        action_with_no_obj.append(True)
    #print(action_with_no_obj)
    for obj in bpy.data.objects:
        has_action = True if obj.animation_data is not None and obj.animation_data.action is not None else False
        if has_action:
            action = obj.animation_data.action
            index = bpy.data.actions.values().index(action)
            need_to_change = action_with_no_obj[index]
            if need_to_change:
                action_with_no_obj[index] = False
                check_action(obj, action)
    #print(action_with_no_obj)
    for index in range(len(action_with_no_obj)):
        need_to_check = action_with_no_obj[index]
        if need_to_check:
            action = bpy.data.actions[index]
            check_action(None, action)
    check_active(parent_links)
    check_active(child_links)
    other_panels['sna_parent_links'] = parent_links
    other_panels['sna_child_links'] = child_links
    #def print_list(list):
    #    is_first = True
    #    print('---------- List ----------')
    #    for action_tuple in list:
    #        (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
    #        (action_name, action_type) = (action_data[0], action_data[1])
    #        (obj_name, obj_type) = (obj_data[0], obj_data[1])
    #        print(action_name, obj_name)
    #        for group_tuple in action_tuple[3]:
    #            (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
    #            (group_name, group_type) = (group_data[0], group_data[1])
    #            print('  ', group_name)
    #            for fcurve_tuple in group_tuple[2]:
    #                (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
    #                (fc_path, fc_index, fc_label, fc_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
    #                print('  ', '  ', fc_label)
    #    print('--------------------------')
    #    print('')
    #print_list(child_links)
    return [parent_links, child_links]


class SNA_OT_Open_Target_In_Panel_F9E9B(bpy.types.Operator):
    bl_idname = "sna.open_target_in_panel_f9e9b"
    bl_label = "Open Target in Panel"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def sna_panel_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_panel: bpy.props.EnumProperty(name='Panel', description='', options={'HIDDEN'}, items=[('Manager', 'Manager', '', 0, 0), ('Timeline', 'Timeline', '', 0, 1), ('Graph Editor', 'Graph Editor', '', 0, 2), ('NONE', 'NONE', '', 0, 3)])

    def sna_target_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_target: bpy.props.EnumProperty(name='Target', description='', options={'HIDDEN'}, items=[('Action', 'Action', '', 0, 0), ('Group', 'Group', '', 0, 1), ('FCurve', 'FCurve', '', 0, 2), ('NONE', 'NONE', '', 0, 3)])
    sna_action: bpy.props.StringProperty(name='Action', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_action_type: bpy.props.StringProperty(name='Action Type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_group: bpy.props.StringProperty(name='Group', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_group_type: bpy.props.StringProperty(name='Group Type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_fc_path: bpy.props.StringProperty(name='FC Path', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_fc_index: bpy.props.IntProperty(name='FC Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')
    sna_fc_type: bpy.props.StringProperty(name='FC Type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        panel = self.sna_panel
        target = self.sna_target
        action = self.sna_action
        act_type = self.sna_action_type
        group = self.sna_group
        grp_type = self.sna_group_type
        fc_path = self.sna_fc_path
        fc_index = self.sna_fc_index
        fc_type = self.sna_fc_type
        list = other_panels['sna_parent_links']
        #print('Open Target in Panel :', target, panel)
        #print('Values :', action, action_type, group, grp_type, fc_path, fc_index, fc_type)
        if panel != 'NONE' and target != 'NONE' and panel != '' and target != '' and action != '':
            for action_tuple in list:
                (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
                (action_name, action_type) = (action_data[0], action_data[1])
                if action_name == action and action_type == act_type:
                    if target == 'Action' and panel == 'Manager':
                        action_tuple[2][0] = not action_tuple[2][0]
                        break
                    else:
                        for group_tuple in action_tuple[3]:
                            (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                            (group_name, group_type) = (group_data[0], group_data[1])
                            if group_name == group and group_type == grp_type:
                                if target == 'Group':
                                    if panel == 'Manager':
                                        group_tuple[1][0] = not group_tuple[1][0]
                                    elif panel == 'Timeline':
                                        group_tuple[1][1] = not group_tuple[1][1]
                                    elif panel == 'Graph Editor':
                                        group_tuple[1][2] = not group_tuple[1][2]
                                    break
                                else:
                                    for fcurve_tuple in group_tuple[2]:
                                        (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                                        (fcurve_path, fcurve_index, fc_label, fcurve_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
                                        if fcurve_path == fc_path and fcurve_index == fc_index and fcurve_type == fc_type:
                                            if target == 'FCurve':
                                                if panel == 'Manager':
                                                    fcurve_tuple[1][0] = not fcurve_tuple[1][0]
                                                elif panel == 'Timeline':
                                                    fcurve_tuple[1][1] = not fcurve_tuple[1][1]
                                                elif panel == 'Graph Editor':
                                                    fcurve_tuple[1][2] = not fcurve_tuple[1][2]
                                            break
                                    break
                        break
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_print_action_ui_B5A9F(layout_function, action_tuple, only_active_obj, only_selected_obj, is_filter, filter_list):
    if sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[7]:
        box_384A4 = layout_function.box()
        box_384A4.alert = False
        box_384A4.enabled = True
        box_384A4.active = True
        box_384A4.use_property_split = False
        box_384A4.use_property_decorate = False
        box_384A4.alignment = 'Expand'.upper()
        box_384A4.scale_x = 1.0
        box_384A4.scale_y = 1.0
        box_384A4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_C69B4 = box_384A4.column(heading='', align=False)
        col_C69B4.alert = False
        col_C69B4.enabled = True
        col_C69B4.active = True
        col_C69B4.use_property_split = False
        col_C69B4.use_property_decorate = False
        col_C69B4.scale_x = 1.0
        col_C69B4.scale_y = 1.0
        col_C69B4.alignment = 'Expand'.upper()
        col_C69B4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_896DE = col_C69B4.row(heading='', align=True)
        row_896DE.alert = False
        row_896DE.enabled = True
        row_896DE.active = True
        row_896DE.use_property_split = False
        row_896DE.use_property_decorate = False
        row_896DE.scale_x = 1.0
        row_896DE.scale_y = 1.0
        row_896DE.alignment = 'Expand'.upper()
        row_896DE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_896DE.operator('sna.open_target_in_panel_f9e9b', text='', icon_value=(5 if sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[4] else 4), emboss=False, depress=False)
        op.sna_panel = 'Manager'
        op.sna_target = 'Action'
        op.sna_action = sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[0]
        op.sna_action_type = sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[1]
        op.sna_group = ''
        op.sna_group_type = ''
        op.sna_fc_path = ''
        op.sna_fc_index = 0
        op.sna_fc_type = ''
        row_896DE.label(text=sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[2], icon_value=string_to_icon(sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[3]))
        if bpy.context.scene.sna_manager_is_edit_mode:
            op = row_896DE.operator('sn.dummy_button_operator', text='', icon_value=21, emboss=True, depress=False)
        else:
            row_5B133 = row_896DE.row(heading='', align=True)
            row_5B133.alert = False
            row_5B133.enabled = True
            row_5B133.active = True
            row_5B133.use_property_split = False
            row_5B133.use_property_decorate = False
            row_5B133.scale_x = 1.0
            row_5B133.scale_y = 1.0
            row_5B133.alignment = 'Expand'.upper()
            row_5B133.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            op = row_5B133.operator('sn.dummy_button_operator', text='', icon_value=555, emboss=sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[6], depress=True)
        if (bpy.context.scene.sna_manager_open_all or sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[4]):
            col_10F35 = col_C69B4.column(heading='', align=False)
            col_10F35.alert = False
            col_10F35.enabled = True
            col_10F35.active = True
            col_10F35.use_property_split = False
            col_10F35.use_property_decorate = False
            col_10F35.scale_x = 1.0
            col_10F35.scale_y = 1.0
            col_10F35.alignment = 'Expand'.upper()
            col_10F35.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_8B7AC = col_10F35.row(heading='', align=True)
            row_8B7AC.alert = False
            row_8B7AC.enabled = True
            row_8B7AC.active = True
            row_8B7AC.use_property_split = False
            row_8B7AC.use_property_decorate = False
            row_8B7AC.scale_x = 1.0
            row_8B7AC.scale_y = 1.0
            row_8B7AC.alignment = 'Expand'.upper()
            row_8B7AC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_8B7AC.label(text='', icon_value=101)
            row_8B7AC.label(text=sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[0], icon_value=string_to_icon(sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[1]))
            row_1F5A9 = col_10F35.row(heading='', align=True)
            row_1F5A9.alert = False
            row_1F5A9.enabled = True
            row_1F5A9.active = True
            row_1F5A9.use_property_split = False
            row_1F5A9.use_property_decorate = False
            row_1F5A9.scale_x = 1.0
            row_1F5A9.scale_y = 1.0
            row_1F5A9.alignment = 'Expand'.upper()
            row_1F5A9.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_1F5A9.separator(factor=2.0)
            col_8CEFE = row_1F5A9.column(heading='', align=False)
            col_8CEFE.alert = False
            col_8CEFE.enabled = True
            col_8CEFE.active = True
            col_8CEFE.use_property_split = False
            col_8CEFE.use_property_decorate = False
            col_8CEFE.scale_x = 1.0
            col_8CEFE.scale_y = 1.0
            col_8CEFE.alignment = 'Expand'.upper()
            col_8CEFE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            if is_filter:
                for i_16022 in range(len(filter_list)):
                    layout_function = col_8CEFE
                    sna_glink_loop_9D621(layout_function, sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[5][filter_list[i_16022][0]], sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[0], sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[1], False, is_filter, filter_list[i_16022][1])
            else:
                for i_BEADC in range(len(sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[5])):
                    layout_function = col_8CEFE
                    sna_glink_loop_9D621(layout_function, sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[5][i_BEADC], sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[0], sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj)[1], False, False, [])


def sna_display_filter_97D7D():
    filter = bpy.context.scene.sna_manager_filter
    is_none = None
    label = None
    icon = None
    label = ''
    icon = ''
    is_none = False
    if filter == 'ACTIVE':
        label = 'Active'
        icon = 'RADIOBUT_ON'
    elif filter == 'SELECTED':
        label = 'Selected'
        icon = 'RESTRICT_SELECT_OFF'
    elif filter == 'INVALID':
        label = 'Invalid'
        icon = 'UNLINKED'
    else:
        is_none = True
    return [is_none, label, string_to_icon(icon)]


class SNA_OT_Remove_Glink_9Dfc2(bpy.types.Operator):
    bl_idname = "sna.remove_glink_9dfc2"
    bl_label = "Remove GLink"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_action_name: bpy.props.StringProperty(name='action_name', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_link_index: bpy.props.IntProperty(name='link_index', description='', options={'HIDDEN'}, default=0, subtype='NONE')
    sna_do_refresh: bpy.props.BoolProperty(name='do refresh', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if len(bpy.data.actions[self.sna_action_name].sna_glink_collection) > self.sna_link_index:
            bpy.data.actions[self.sna_action_name].sna_glink_collection.remove(self.sna_link_index)
        if (self.sna_link_index == bpy.data.actions[self.sna_action_name].sna_editor_link_index):
            bpy.data.actions[self.sna_action_name].sna_editor_link_index = 0
        if self.sna_do_refresh:
            parent_links_0_7b521, child_links_1_7b521 = sna_glink_list_12FEE()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Edit_Glink_B1Df3(bpy.types.Operator):
    bl_idname = "sna.edit_glink_b1df3"
    bl_label = "Edit GLink"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_action_name: bpy.props.StringProperty(name='action_name', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    sna_link_index: bpy.props.IntProperty(name='link_index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        glink = bpy.data.actions[self.sna_action_name].sna_glink_collection[self.sna_link_index]
        index = self.sna_link_index
        action = bpy.data.actions[self.sna_action_name]
        from_group = glink.from_group
        from_path = glink.from_data_path
        from_index = glink.from_array_index
        to_group = glink.to_group
        to_path = glink.to_data_path
        to_index = glink.to_array_index
        for obj in bpy.context.view_layer.objects:
            if obj.animation_data is not None and obj.animation_data.action is not None and action.name == obj.animation_data.action.name:
                bpy.context.view_layer.objects.active = obj
                if bpy.context.active_object.name == obj.name:
                    # Loading Editor_Link_index
                    action.sna_editor_link_index = index
                    # Loading Editor_From_Group
                    found = False
                    if from_group != '' and from_group != 'NONE' :
                        for group in action.groups:
                            if group.name == from_group:
                                action.sna_editor_from_group = from_group
                                found = True
                                break
                    if not found:
                        action.sna_editor_from_group = 'NONE'
                    if found:
                        # Loading Editor_From_FCurve
                        found = False
                        if from_path != '' and from_path != 'NONE':
                            for fc in action.fcurves:
                                if fc.data_path == from_path and fc.array_index == from_index:
                                    action.sna_editor_from_fcurve = sna_create_fcurve_name_B67F8(from_path, from_index, from_group)
                                    found = True
                                    break
                        if not found:
                            glink.is_from_valid = False
                            action.sna_editor_from_fcurve = 'NONE'
                    # Loading Editor_To_Action
                    found = False
                    if glink.to_action != '' and glink.to_action != 'NONE':
                        for act in bpy.data.actions:
                            if act.name == glink.to_action:
                                action.sna_editor_to_action = act
                                found = True
                                break
                    if not found:
                        action.sna_editor_to_action = None
                    if found:
                        # Loading Editor_To_Group
                        found = False
                        if to_group != '' and to_group != 'NONE':
                            for group in action.sna_editor_to_action.groups:
                                if group.name == to_group:
                                    action.sna_editor_to_group = to_group
                                    found = True
                                    break
                        if not found:
                            action.sna_editor_to_group = 'NONE'
                        if found:
                            # Loading Editor_To_FCurve
                            found = False
                            if to_path != '' and to_path != 'NONE':
                                for fc in action.sna_editor_to_action.fcurves:
                                    if fc.data_path == to_path and fc.array_index == to_index:
                                        action.sna_editor_to_fcurve = sna_create_fcurve_name_B67F8(to_path, to_index, to_group)
                                        found = True
                                        break
                            if not found:
                                glink.is_to_valid = False
                                action.sna_editor_to_fcurve = 'NONE'
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_update_glinks_53D8F(is_update_all, obj_list):
    is_update_all = is_update_all
    obj_list = obj_list

    def print_keys(keys, name):
        prints = []
        for key in keys:
            prints.append((round(key.co[0], 1), round(key.co[1], 1)))
        print(prints, name)

    def get_keys(fc, f, t):
        is_inside = False
        keys = []
        for key in fc.keyframe_points:
            if key.co[0] >= f and key.co[0] <= t:
                if not is_inside:
                    is_inside = True
                keys.append(key)
            elif is_inside:
                break
        return keys

    def update_link(link, from_fc, to_fc):
        is_custom = link.range_options == 'Custom'
        is_self = False
        if str(from_fc) == str(to_fc):
            is_self = True
            if link.pivot_frame != 'Range End' or not is_custom:
                return
        from_keys = []
        if is_custom:
            is_inside = False
            from_keys = get_keys(from_fc, link.range_start, link.range_end)
        else:
            from_keys = from_fc.keyframe_points
        from_len = len(from_keys)
        print_keys(from_keys, '<-- from keys')
        if from_len != 0:
            flip_x = 1
            flip_y = 1
            if link.flip_x_axis == True:
                flip_x = -1
            if link.flip_y_axis == True:
                flip_y = -1
            first = from_keys[0]
            last = from_keys[from_len-1]
            first_key = (first.co[0], first.co[1])
            last_key = (last.co[0], last.co[1])
            length = last_key[0] - first_key[0]
            origin = (0, 0)
            if link.pivot_frame == 'Zero':
                pass
            elif link.pivot_frame == 'First Keyframe':
                origin = (first_key[0], origin[1])
            elif link.pivot_frame == 'Last Keyframe':
                origin = (last_key[0], origin[1])
            elif link.pivot_frame == 'Range End':
                origin = (link.range_end, origin[1])
            if link.pivot_value == 'Zero':
                pass
            elif link.pivot_value == 'First Keyframe':
                origin = (origin[0], first_key[1])
            elif link.pivot_value == 'Last Keyframe':
                origin = (origin[0], last_key[1])
            to_start = origin[0] + link.offset_x
            to_end = to_start + length
            to_keys = []
            to_len = 0
            if is_custom:
                to_keys = get_keys(to_fc, to_start, to_end)
                print_keys(to_keys, '<-- to keys')
                to_len = len(to_keys)
                if to_len == from_len:
                    pass
                elif to_len < from_len:
                    need = from_len - to_len
                    for i in range(need):
                        key = to_fc.keyframe_points.insert(frame=to_start + 1 + (i/10),value=0)
                        key.select_control_point = False
                        key.select_left_handle = False
                        key.select_right_handle = False
                        to_keys.append(key)
                    print('Addition....')
                    print_keys(to_keys, '<-- to keys before recal')
                    to_keys = get_keys(to_fc, to_start, to_end)
                    print_keys(to_keys, '<-- to keys after recal')
                    to_len = len(to_keys)
                elif to_len > from_len:
                    need = to_len - from_len
                    count = 0
                    for key in reversed(to_keys):
                        to_fc.keyframe_points.remove(key)
                        count = count + 1
                        if count >= need:
                            break
                    print('Removal....')
                    to_keys = get_keys(to_fc, to_start, to_end)
                    print_keys(to_keys, '<-- to keys after recal')
            else:
                to_len = len(to_fc.keyframe_points)
                to_keys = to_fc.keyframe_points
                if from_len == to_len:
                    pass
                elif from_len > to_len:
                    need = from_len - to_len
                    to_fc.keyframe_points.add(count=need)
                elif from_len < to_len:
                    need = to_len - from_len
                    count = 0
                    for key in reversed(to_fc.keyframe_points.values()):
                        to_fc.keyframe_points.remove(key)
                        count = count + 1
                        if count >= need:
                            break
            i = 0
            print('From len: ', len(from_keys), ' To len: ', len(to_keys))
            if len(from_keys) == len(to_keys):
                for from_key in from_keys:
                    x_add = 0
                    y_add = 0
    #                flip_x = flip_x + origin[0]
    #                flip_y = flip_y + origin[1]
                    if is_custom:
                        x_add = - first_key[0] + origin[0] + link.offset_x
                        y_add = - first_key[1] + origin[1] + link.offset_y
                    else:
                        x_add = link.offset_x
                        y_add = link.offset_y
                    to_keys[i].interpolation = from_keys[i].interpolation
                    handle_left = from_keys[i].handle_left
                    to_keys[i].handle_left = ((handle_left[0] + x_add) * flip_x, (handle_left[1]+ y_add) * flip_y)
                    handle_right = from_keys[i].handle_right
                    to_keys[i].handle_right = ((handle_right[0] + x_add) * flip_x, (handle_right[1]+ y_add) * flip_y)
                    from_co = from_keys[i].co
                    to_keys[i].co = ((from_co[0] + x_add) * flip_x, (from_co[1] + y_add) * flip_y)
                    i = i+1
    #            to_fc.keyframe_points.sort()

    def update_obj(is_all, obj_name = ''):
            list = other_panels['sna_child_links']
            for action_tuple in list:
                is_act_deactivated = action_tuple[2][1]
                if not is_act_deactivated:
                    to_obj = action_tuple[1][2]
                    if to_obj is not None and (is_all or to_obj.name == obj_name):
                        group_list = action_tuple[3]
                        to_action = action_tuple[0][2]
                        for group_tuple in group_list:
                            is_grp_deactivated = group_tuple[1][3]
                            if not is_grp_deactivated:
                                fc_list = group_tuple[2]
                                to_group = group_tuple[0][2]
                                for fc_tuple in fc_list:
                                    is_fc_deactivated = fc_tuple[1][3]
                                    if not is_fc_deactivated:
                                        link_list = fc_tuple[2]
                                        to_fc = fc_tuple[0][4]
                                        for link_data in link_list:
                                            link = link_data[0]
                                            if not link.is_deactive and link.is_from_valid and link.is_to_valid:
                                                parent_data = link_data[2]
                                                (from_action, from_group, from_fc) = parent_data
                                                if from_action is not None and from_group is not None and from_fc is not None:
                                                    from_data = (from_action, from_group, from_fc)
                                                    to_data = (to_action, to_group, to_fc)
                                                    update_link(link, to_fc, from_fc)
                                                    print(to_obj.name, to_group.name, to_fc.data_path, to_fc.array_index, '<--- Update')
                        if is_all:
                            break
    if is_update_all:
        update_obj(True)
    else:
        for obj_name in obj_list:
            update_obj(False, obj_name)


@persistent
def depsgraph_update_post_handler_82C62(dummy):
    if bpy.context.scene.sna_stop_addon:
        pass
    else:
        parent_links_0_99f6f, child_links_1_99f6f = sna_glink_list_12FEE()
        filter = bpy.context.scene.sna_manager_filter
        is_child = bpy.context.scene.sna_manager_is_group_child
        index_list = []
        is_active_selected = False
        is_none = False
        is_active = False
        is_selected = False
        is_filter = False
        list = []
        if is_child:
            list = other_panels['sna_child_links']
        else:
            list = other_panels['sna_parent_links']
        if filter == 'ACTIVE':
            is_active = True
        elif filter == 'SELECTED':
            is_selected = True
        elif filter == 'INVALID':
            is_filter = True
        else:
            is_none = True
        for index in range(len(list)):
            action_tuple = list[index]
            (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
            (action_name, action_type) = (action_data[0], action_data[1])
            (obj_name, obj_type) = (obj_data[0], obj_data[1])
            if filter == 'INVALID':
                g_list = []
                if action_type == 'ERROR':
                    for g_index in range(len(group_list)):
                        group_tuple = group_list[g_index]
                        (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                        f_list = []
                        for f_index in range(len(fc_list)):
                                f_list.append(f_index)
                        g_list.append([g_index, f_list])
                    index_list.append([index, g_list])
                else:
                    for g_index in range(len(group_list)):
                        group_tuple = group_list[g_index]
                        (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                        (group_name, group_type) = (group_data[0], group_data[1])
                        f_list = []
                        if group_type == 'ERROR':
                            for f_index in range(len(fc_list)):
                                f_list.append(f_index)
                            g_list.append([g_index, f_list])
                        else:
                            for f_index in range(len(fc_list)):
                                fcurve_tuple = fc_list[f_index]
                                (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                                (fc_path, fc_index, fc_label, fc_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
                                if fc_type == 'ERROR':
                                    f_list.append(f_index)
                            if len(f_list) != 0:
                                g_list.append([g_index, f_list])
                    if len(g_list) != 0:
                        index_list.append([index, g_list])
        nodetree['sna_filter_list'] = index_list
        nodetree['sna_is_active_filter'] = is_active
        nodetree['sna_is_selected_filter'] = is_selected
        nodetree['sna_is_none_filter'] = is_none
        nodetree['sna_is_filter'] = is_filter
        if bpy.context.scene.sna_is_tracking:
            obj_list = None
            obj_list = []
            scene = dummy
            depsgraph = bpy.context.evaluated_depsgraph_get()
            if d_viewport_manager_ui['sna_operator_deps'] is None:
                d_viewport_manager_ui['sna_operator_deps'] = bpy.context.active_operator
            for update in depsgraph.updates:
                if not update.is_updated_transform:
                    continue
                if d_viewport_manager_ui['sna_operator_deps'] == bpy.context.active_operator:
                    continue
                obj = bpy.context.active_object
                if obj is not None:
                    is_found = False
                    for obj_name in obj_list:
                        if obj.name == obj_name:
                            is_found = True
                            break
                    if not is_found:
                        obj_list.append(obj.name)
                    d_viewport_manager_ui['sna_operator_deps'] = None
            sna_update_glinks_53D8F(False, obj_list)


class SNA_PT_GLINK_MANAGER_DD502(bpy.types.Panel):
    bl_label = 'GLink Manager'
    bl_idname = 'SNA_PT_GLINK_MANAGER_DD502'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'GLink'
    bl_order = 1
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout
        layout.menu('SNA_MT_F8A8C', text='', icon_value=117)

    def draw(self, context):
        layout = self.layout
        if bpy.context.scene.sna_stop_addon:
            pass
        else:
            col_24D37 = layout.column(heading='', align=False)
            col_24D37.alert = False
            col_24D37.enabled = True
            col_24D37.active = True
            col_24D37.use_property_split = False
            col_24D37.use_property_decorate = False
            col_24D37.scale_x = 1.0
            col_24D37.scale_y = 1.0
            col_24D37.alignment = 'Expand'.upper()
            col_24D37.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            layout_function = col_24D37
            sna_track_and_refresh_464F5(layout_function, False)
            col_24D37.separator(factor=1.0)
            row_81202 = col_24D37.row(heading='', align=True)
            row_81202.alert = False
            row_81202.enabled = True
            row_81202.active = True
            row_81202.use_property_split = False
            row_81202.use_property_decorate = False
            row_81202.scale_x = 1.0
            row_81202.scale_y = 1.0
            row_81202.alignment = 'Expand'.upper()
            row_81202.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_81202.label(text='Group By :', icon_value=0)
            row_81202.prop(bpy.context.scene, 'sna_manager_is_group_child', text='Parent', icon_value=0, emboss=True, toggle=True, invert_checkbox=True)
            row_81202.prop(bpy.context.scene, 'sna_manager_is_group_child', text='Children', icon_value=0, emboss=True, toggle=True)
            col_24D37.separator(factor=1.0)
            col_24D37.prop(bpy.context.scene, 'sna_manager_open_all', text='Open All Columns', icon_value=0, emboss=True)
            col_24D37.separator(factor=1.0)
            col_CE883 = col_24D37.column(heading='', align=False)
            col_CE883.alert = False
            col_CE883.enabled = True
            col_CE883.active = True
            col_CE883.use_property_split = False
            col_CE883.use_property_decorate = False
            col_CE883.scale_x = 1.0
            col_CE883.scale_y = 1.0
            col_CE883.alignment = 'Expand'.upper()
            col_CE883.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_DD2C4 = col_CE883.row(heading='', align=True)
            row_DD2C4.alert = False
            row_DD2C4.enabled = True
            row_DD2C4.active = True
            row_DD2C4.use_property_split = False
            row_DD2C4.use_property_decorate = False
            row_DD2C4.scale_x = 1.100000023841858
            row_DD2C4.scale_y = 1.100000023841858
            row_DD2C4.alignment = 'Expand'.upper()
            row_DD2C4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_DD2C4.label(text='GLink List : ', icon_value=0)
            if sna_display_filter_97D7D()[0]:
                pass
            else:
                row_BF5CE = row_DD2C4.row(heading='', align=False)
                row_BF5CE.alert = False
                row_BF5CE.enabled = True
                row_BF5CE.active = (not bpy.context.scene.sna_manager_disable_filter)
                row_BF5CE.use_property_split = False
                row_BF5CE.use_property_decorate = False
                row_BF5CE.scale_x = 0.8999999761581421
                row_BF5CE.scale_y = 1.0
                row_BF5CE.alignment = 'Right'.upper()
                row_BF5CE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                row_BF5CE.prop(bpy.context.scene, 'sna_manager_disable_filter', text=sna_display_filter_97D7D()[1], icon_value=sna_display_filter_97D7D()[2], emboss=False)
            row_256A1 = row_DD2C4.row(heading='', align=False)
            row_256A1.alert = False
            row_256A1.enabled = True
            row_256A1.active = True
            row_256A1.use_property_split = False
            row_256A1.use_property_decorate = False
            row_256A1.scale_x = 0.4000000059604645
            row_256A1.scale_y = 1.0
            row_256A1.alignment = 'Expand'.upper()
            row_256A1.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_256A1.menu('SNA_MT_68936', text=' ', icon_value=688)
            row_DD2C4.prop(bpy.context.scene, 'sna_manager_is_edit_mode', text='', icon_value=197, emboss=True)
            if (not ((not nodetree['sna_is_filter']) or bpy.context.scene.sna_manager_disable_filter)):
                for i_99A85 in range(len(nodetree['sna_filter_list'])):
                    layout_function = col_CE883
                    sna_print_action_ui_B5A9F(layout_function, (other_panels['sna_child_links'] if bpy.context.scene.sna_manager_is_group_child else other_panels['sna_parent_links'])[nodetree['sna_filter_list'][i_99A85][0]], nodetree['sna_is_active_filter'], nodetree['sna_is_selected_filter'], True, nodetree['sna_filter_list'][i_99A85][1])
            else:
                for i_AB301 in range(len((other_panels['sna_child_links'] if bpy.context.scene.sna_manager_is_group_child else other_panels['sna_parent_links']))):
                    layout_function = col_CE883
                    sna_print_action_ui_B5A9F(layout_function, (other_panels['sna_child_links'] if bpy.context.scene.sna_manager_is_group_child else other_panels['sna_parent_links'])[i_AB301], nodetree['sna_is_active_filter'], nodetree['sna_is_selected_filter'], False, [])


class SNA_OT_Create_Link_Aedf6(bpy.types.Operator):
    bl_idname = "sna.create_link_aedf6"
    bl_label = "Create Link"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        if bpy.context.object.animation_data is not None and bpy.context.object.animation_data.action is not None:
            item_1430B = bpy.context.object.animation_data.action.sna_glink_collection.add()
            glink = item_1430B
            index = bpy.context.object.animation_data.action.sna_glink_collection.values().index(item_1430B)
            action = bpy.context.object.animation_data.action
            from_group = glink.from_group
            from_path = glink.from_data_path
            from_index = glink.from_array_index
            to_group = glink.to_group
            to_path = glink.to_data_path
            to_index = glink.to_array_index
            for obj in bpy.context.view_layer.objects:
                if obj.animation_data is not None and obj.animation_data.action is not None and action.name == obj.animation_data.action.name:
                    bpy.context.view_layer.objects.active = obj
                    if bpy.context.active_object.name == obj.name:
                        # Loading Editor_Link_index
                        action.sna_editor_link_index = index
                        # Loading Editor_From_Group
                        found = False
                        if from_group != '' and from_group != 'NONE' :
                            for group in action.groups:
                                if group.name == from_group:
                                    action.sna_editor_from_group = from_group
                                    found = True
                                    break
                        if not found:
                            action.sna_editor_from_group = 'NONE'
                        if found:
                            # Loading Editor_From_FCurve
                            found = False
                            if from_path != '' and from_path != 'NONE':
                                for fc in action.fcurves:
                                    if fc.data_path == from_path and fc.array_index == from_index:
                                        action.sna_editor_from_fcurve = sna_create_fcurve_name_B67F8(from_path, from_index, from_group)
                                        found = True
                                        break
                            if not found:
                                glink.is_from_valid = False
                                action.sna_editor_from_fcurve = 'NONE'
                        # Loading Editor_To_Action
                        found = False
                        if glink.to_action != '' and glink.to_action != 'NONE':
                            for act in bpy.data.actions:
                                if act.name == glink.to_action:
                                    action.sna_editor_to_action = act
                                    found = True
                                    break
                        if not found:
                            action.sna_editor_to_action = None
                        if found:
                            # Loading Editor_To_Group
                            found = False
                            if to_group != '' and to_group != 'NONE':
                                for group in action.sna_editor_to_action.groups:
                                    if group.name == to_group:
                                        action.sna_editor_to_group = to_group
                                        found = True
                                        break
                            if not found:
                                action.sna_editor_to_group = 'NONE'
                            if found:
                                # Loading Editor_To_FCurve
                                found = False
                                if to_path != '' and to_path != 'NONE':
                                    for fc in action.sna_editor_to_action.fcurves:
                                        if fc.data_path == to_path and fc.array_index == to_index:
                                            action.sna_editor_to_fcurve = sna_create_fcurve_name_B67F8(to_path, to_index, to_group)
                                            found = True
                                            break
                                if not found:
                                    glink.is_to_valid = False
                                    action.sna_editor_to_fcurve = 'NONE'
            parent_links_0_57f3c, child_links_1_57f3c = sna_glink_list_12FEE()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_PT_GLINK_CREATOR_76BD4(bpy.types.Panel):
    bl_label = 'GLink Creator'
    bl_idname = 'SNA_PT_GLINK_CREATOR_76BD4'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'GLink'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (bpy.context.scene.sna_stop_addon)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        if bpy.context.object is not None:
            col_C22D6 = layout.column(heading='', align=False)
            col_C22D6.alert = False
            col_C22D6.enabled = True
            col_C22D6.active = True
            col_C22D6.use_property_split = False
            col_C22D6.use_property_decorate = False
            col_C22D6.scale_x = 1.0
            col_C22D6.scale_y = 1.0
            col_C22D6.alignment = 'Expand'.upper()
            col_C22D6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            col_C22D6.label(text=bpy.context.object.name, icon_value=130)
            col_C22D6.label(text=bpy.context.object.animation_data.action.name if bpy.context.object.animation_data is not None and bpy.context.object.animation_data.action is not None else "No Action Attached", icon_value=115)
            col_78C50 = col_C22D6.column(heading='', align=False)
            col_78C50.alert = False
            col_78C50.enabled = bpy.context.object.animation_data is not None and bpy.context.object.animation_data.action is not None
            col_78C50.active = True
            col_78C50.use_property_split = False
            col_78C50.use_property_decorate = False
            col_78C50.scale_x = 1.0
            col_78C50.scale_y = 1.0
            col_78C50.alignment = 'Expand'.upper()
            col_78C50.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            col_78C50.separator(factor=1.0)
            row_FA3C1 = col_78C50.row(heading='', align=False)
            row_FA3C1.alert = False
            row_FA3C1.enabled = True
            row_FA3C1.active = True
            row_FA3C1.use_property_split = False
            row_FA3C1.use_property_decorate = False
            row_FA3C1.scale_x = 1.0
            row_FA3C1.scale_y = 1.399999976158142
            row_FA3C1.alignment = 'Expand'.upper()
            row_FA3C1.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            op = row_FA3C1.operator('sna.create_link_aedf6', text='CREATE GLINK', icon_value=31, emboss=True, depress=False)
            if (bpy.context.object.animation_data is not None and bpy.context.object.animation_data.action is not None and (len(bpy.context.object.animation_data.action.sna_glink_collection.values()) != 0)):
                col_5751E = col_C22D6.column(heading='', align=False)
                col_5751E.alert = False
                col_5751E.enabled = True
                col_5751E.active = True
                col_5751E.use_property_split = False
                col_5751E.use_property_decorate = False
                col_5751E.scale_x = 1.0
                col_5751E.scale_y = 1.0
                col_5751E.alignment = 'Expand'.upper()
                col_5751E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                col_5751E.separator(factor=1.0)
                col_5751E.prop(bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index], 'is_batch_armature', text='Batch Add', icon_value=0, emboss=True)
                col_5751E.separator(factor=1.0)
                if bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].is_batch_armature:
                    box_DE8FA = col_5751E.box()
                    box_DE8FA.alert = False
                    box_DE8FA.enabled = True
                    box_DE8FA.active = True
                    box_DE8FA.use_property_split = False
                    box_DE8FA.use_property_decorate = False
                    box_DE8FA.alignment = 'Expand'.upper()
                    box_DE8FA.scale_x = 1.0
                    box_DE8FA.scale_y = 1.0
                    box_DE8FA.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    col_0AED7 = box_DE8FA.column(heading='', align=False)
                    col_0AED7.alert = False
                    col_0AED7.enabled = True
                    col_0AED7.active = True
                    col_0AED7.use_property_split = False
                    col_0AED7.use_property_decorate = False
                    col_0AED7.scale_x = 1.0
                    col_0AED7.scale_y = 1.0
                    col_0AED7.alignment = 'Expand'.upper()
                    col_0AED7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    col_0AED7.prop(bpy.context.scene, 'sna_new_property', text='Selected Only', icon_value=0, emboss=True)
                    col_0AED7.separator(factor=1.0)
                    row_A3B87 = col_0AED7.row(heading='', align=True)
                    row_A3B87.alert = False
                    row_A3B87.enabled = True
                    row_A3B87.active = True
                    row_A3B87.use_property_split = False
                    row_A3B87.use_property_decorate = False
                    row_A3B87.scale_x = 1.0
                    row_A3B87.scale_y = 1.0
                    row_A3B87.alignment = 'Expand'.upper()
                    row_A3B87.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_A3B87.label(text='From :', icon_value=0)
                    row_A3B87.prop(bpy.context.scene, 'sna_new_property', text='Right', icon_value=0, emboss=True, toggle=True)
                    row_A3B87.prop(bpy.context.scene, 'sna_new_property', text='Left', icon_value=0, emboss=True, toggle=True)
                    col_0AED7.separator(factor=1.0)
                    col_0AED7.prop(bpy.context.scene, 'sna_new_property', text='Flip Center Bones', icon_value=0, emboss=True)
                    col_0AED7.prop(bpy.context.scene, 'sna_new_property', text='Add Cyclic Modifier', icon_value=0, emboss=True)
                else:
                    layout_function = col_5751E
                    sna_child_link_ui_945FA(layout_function, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index])
                    layout_function = col_5751E
                    sna_parent_link_ui_61779(layout_function, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index])
                layout_function = col_5751E
                sna_glink_options_DFBEF(layout_function, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index])
                col_5751E.separator(factor=0.20000000298023224)


class SNA_OT_Refresh_Operator_C9416(bpy.types.Operator):
    bl_idname = "sna.refresh_operator_c9416"
    bl_label = "Refresh Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        sna_update_glinks_53D8F(True, [])
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_track_and_refresh_464F5(layout_function, is_compact):
    if is_compact:
        row_373BC = layout_function.row(heading='', align=True)
        row_373BC.alert = False
        row_373BC.enabled = True
        row_373BC.active = True
        row_373BC.use_property_split = False
        row_373BC.use_property_decorate = False
        row_373BC.scale_x = 1.0
        row_373BC.scale_y = 1.0
        row_373BC.alignment = 'Expand'.upper()
        row_373BC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_373BC.prop(bpy.context.scene, 'sna_is_tracking', text='', icon_value=527, emboss=True)
        op = row_373BC.operator('sna.refresh_operator_c9416', text='', icon_value=692, emboss=True, depress=False)
    else:
        layout_function.prop(bpy.context.scene, 'sna_is_tracking', text='Track Change', icon_value=527, emboss=True)
        op = layout_function.operator('sna.refresh_operator_c9416', text='Refresh GLink', icon_value=692, emboss=True, depress=False)


def sna_glink_options_DFBEF(layout_function, collection_property):
    col_7596B = layout_function.column(heading='', align=False)
    col_7596B.alert = False
    col_7596B.enabled = True
    col_7596B.active = True
    col_7596B.use_property_split = True
    col_7596B.use_property_decorate = False
    col_7596B.scale_x = 1.0
    col_7596B.scale_y = 1.0
    col_7596B.alignment = 'Expand'.upper()
    col_7596B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    col_7596B.separator(factor=1.0)
    col_0DAFF = col_7596B.column(heading='', align=False)
    col_0DAFF.alert = False
    col_0DAFF.enabled = True
    col_0DAFF.active = True
    col_0DAFF.use_property_split = True
    col_0DAFF.use_property_decorate = False
    col_0DAFF.scale_x = 1.0
    col_0DAFF.scale_y = 1.0
    col_0DAFF.alignment = 'Expand'.upper()
    col_0DAFF.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    col_0DAFF.prop(collection_property, 'range_options', text='Range', icon_value=0, emboss=True, toggle=True)
    if (collection_property.range_options == 'Custom'):
        col_0DAFF.prop(collection_property, 'border_key_range', text='Edge Keys', icon_value=0, emboss=True)
        row_4AA20 = col_0DAFF.row(heading='', align=True)
        row_4AA20.alert = False
        row_4AA20.enabled = True
        row_4AA20.active = True
        row_4AA20.use_property_split = True
        row_4AA20.use_property_decorate = False
        row_4AA20.scale_x = 1.0
        row_4AA20.scale_y = 1.0
        row_4AA20.alignment = 'Expand'.upper()
        row_4AA20.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_4AA20.prop(collection_property, 'range_start', text=' ', icon_value=0, emboss=True)
        row_4AA20.prop(collection_property, 'range_end', text='', icon_value=0, emboss=True)
        row_4AA20.separator(factor=1.0)
        row_4AA20.prop(collection_property, 'range_in_parent', text='', icon_value=(254 if collection_property.range_in_parent else 253), emboss=True)
    col_7596B.separator(factor=1.0)
    col_7596B.prop(collection_property, 'pivot_frame', text='Pivot Frame', icon_value=0, emboss=True)
    col_7596B.prop(collection_property, 'pivot_value', text='Pivot Value', icon_value=0, emboss=True)
    col_7596B.separator(factor=1.0)
    row_6D549 = col_7596B.row(heading='', align=False)
    row_6D549.alert = False
    row_6D549.enabled = True
    row_6D549.active = True
    row_6D549.use_property_split = True
    row_6D549.use_property_decorate = False
    row_6D549.scale_x = 1.0
    row_6D549.scale_y = 1.0
    row_6D549.alignment = 'Expand'.upper()
    row_6D549.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_DDE59 = row_6D549.row(heading='', align=True)
    row_DDE59.alert = False
    row_DDE59.enabled = True
    row_DDE59.active = True
    row_DDE59.use_property_split = True
    row_DDE59.use_property_decorate = False
    row_DDE59.scale_x = 1.6299999952316284
    row_DDE59.scale_y = 1.0
    row_DDE59.alignment = 'Right'.upper()
    row_DDE59.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_DDE59.label(text='Flip Axes', icon_value=0)
    row_0162F = row_6D549.row(heading='', align=True)
    row_0162F.alert = False
    row_0162F.enabled = True
    row_0162F.active = True
    row_0162F.use_property_split = False
    row_0162F.use_property_decorate = False
    row_0162F.scale_x = 1.0
    row_0162F.scale_y = 1.0
    row_0162F.alignment = 'Expand'.upper()
    row_0162F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_0162F.prop(collection_property, 'flip_x_axis', text='X', icon_value=0, emboss=True, toggle=True)
    row_0162F.prop(collection_property, 'flip_y_axis', text='Y', icon_value=0, emboss=True, toggle=True)
    col_7596B.separator(factor=1.0)
    col_7A6D5 = col_7596B.column(heading='', align=False)
    col_7A6D5.alert = False
    col_7A6D5.enabled = True
    col_7A6D5.active = True
    col_7A6D5.use_property_split = False
    col_7A6D5.use_property_decorate = False
    col_7A6D5.scale_x = 1.0
    col_7A6D5.scale_y = 1.0
    col_7A6D5.alignment = 'Expand'.upper()
    col_7A6D5.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    col_7A6D5.label(text='Chieck Reverse Condition', icon_value=494)
    col_7A6D5.separator(factor=0.5)
    row_02A5A = col_7A6D5.row(heading='', align=True)
    row_02A5A.alert = False
    row_02A5A.enabled = True
    row_02A5A.active = True
    row_02A5A.use_property_split = True
    row_02A5A.use_property_decorate = False
    row_02A5A.scale_x = 1.0
    row_02A5A.scale_y = 1.0
    row_02A5A.alignment = 'Expand'.upper()
    row_02A5A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_02A5A.prop(collection_property, 'offset_x', text='Offset X', icon_value=0, emboss=True, slider=True)
    row_02A5A.separator(factor=1.0)
    row_02A5A.prop(collection_property, 'offsetx_in_parent', text='', icon_value=(254 if collection_property.offsetx_in_parent else 253), emboss=True)
    row_A3CD3 = col_7A6D5.row(heading='', align=True)
    row_A3CD3.alert = False
    row_A3CD3.enabled = True
    row_A3CD3.active = True
    row_A3CD3.use_property_split = True
    row_A3CD3.use_property_decorate = False
    row_A3CD3.scale_x = 1.0
    row_A3CD3.scale_y = 1.0
    row_A3CD3.alignment = 'Expand'.upper()
    row_A3CD3.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_A3CD3.prop(collection_property, 'offset_y', text='Offset Y', icon_value=0, emboss=True, slider=True)
    row_A3CD3.separator(factor=1.0)
    row_A3CD3.prop(collection_property, 'offsety_in_parent', text='', icon_value=(254 if collection_property.offsety_in_parent else 253), emboss=True)
    col_7596B.separator(factor=1.0)
    col_C24BC = col_7596B.column(heading='', align=False)
    col_C24BC.alert = False
    col_C24BC.enabled = True
    col_C24BC.active = True
    col_C24BC.use_property_split = False
    col_C24BC.use_property_decorate = False
    col_C24BC.scale_x = 1.0
    col_C24BC.scale_y = 1.0
    col_C24BC.alignment = 'Expand'.upper()
    col_C24BC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_5CA75 = col_C24BC.row(heading='', align=True)
    row_5CA75.alert = False
    row_5CA75.enabled = True
    row_5CA75.active = True
    row_5CA75.use_property_split = True
    row_5CA75.use_property_decorate = False
    row_5CA75.scale_x = 1.0
    row_5CA75.scale_y = 1.0
    row_5CA75.alignment = 'Expand'.upper()
    row_5CA75.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_5CA75.prop(collection_property, 'scale_x', text='Scale X', icon_value=0, emboss=True, slider=True)
    row_5CA75.separator(factor=1.0)
    row_5CA75.prop(collection_property, 'scalex_in_parent', text='', icon_value=(254 if collection_property.scalex_in_parent else 253), emboss=True)
    row_719EA = col_C24BC.row(heading='', align=True)
    row_719EA.alert = False
    row_719EA.enabled = True
    row_719EA.active = True
    row_719EA.use_property_split = True
    row_719EA.use_property_decorate = False
    row_719EA.scale_x = 1.0
    row_719EA.scale_y = 1.0
    row_719EA.alignment = 'Expand'.upper()
    row_719EA.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_719EA.prop(collection_property, 'scale_y', text='Scale Y', icon_value=0, emboss=True, slider=True)
    row_719EA.separator(factor=1.0)
    row_719EA.prop(collection_property, 'scaley_in_parent', text='', icon_value=(254 if collection_property.scaley_in_parent else 253), emboss=True)


def sna_child_link_ui_945FA(layout_function, glink_collection):
    box_E5F55 = layout_function.box()
    box_E5F55.alert = False
    box_E5F55.enabled = True
    box_E5F55.active = True
    box_E5F55.use_property_split = False
    box_E5F55.use_property_decorate = False
    box_E5F55.alignment = 'Expand'.upper()
    box_E5F55.scale_x = 1.0
    box_E5F55.scale_y = 1.0
    box_E5F55.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_EC32B = box_E5F55.row(heading='', align=False)
    row_EC32B.alert = False
    row_EC32B.enabled = True
    row_EC32B.active = True
    row_EC32B.use_property_split = False
    row_EC32B.use_property_decorate = False
    row_EC32B.scale_x = 1.0
    row_EC32B.scale_y = 1.0
    row_EC32B.alignment = 'Expand'.upper()
    row_EC32B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_EC32B.prop(glink_collection, 'is_from_link_open', text='', icon_value=(46 if glink_collection.is_from_link_open else 45), emboss=False)
    row_EC32B.label(text='Link From', icon_value=0)
    if glink_collection.is_from_valid:
        pass
    else:
        row_EC32B.label(text='Not Valid', icon_value=2)
    if glink_collection.is_from_link_open:
        col_DE1EC = box_E5F55.column(heading='', align=False)
        col_DE1EC.alert = False
        col_DE1EC.enabled = True
        col_DE1EC.active = True
        col_DE1EC.use_property_split = False
        col_DE1EC.use_property_decorate = False
        col_DE1EC.scale_x = 1.0
        col_DE1EC.scale_y = 1.0
        col_DE1EC.alignment = 'Expand'.upper()
        col_DE1EC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_1AF04 = col_DE1EC.row(heading='', align=False)
        row_1AF04.alert = False
        row_1AF04.enabled = True
        row_1AF04.active = True
        row_1AF04.use_property_split = False
        row_1AF04.use_property_decorate = False
        row_1AF04.scale_x = 1.0
        row_1AF04.scale_y = 1.0
        row_1AF04.alignment = 'Expand'.upper()
        row_1AF04.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_18FD7 = row_1AF04.column(heading='', align=False)
        col_18FD7.alert = False
        col_18FD7.enabled = True
        col_18FD7.active = True
        col_18FD7.use_property_split = False
        col_18FD7.use_property_decorate = False
        col_18FD7.scale_x = 1.0
        col_18FD7.scale_y = 1.0
        col_18FD7.alignment = 'Right'.upper()
        col_18FD7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_18FD7.label(text='Group : ', icon_value=0)
        col_18FD7.label(text='F-Curve : ', icon_value=0)
        col_DEBB3 = row_1AF04.column(heading='', align=False)
        col_DEBB3.alert = False
        col_DEBB3.enabled = True
        col_DEBB3.active = True
        col_DEBB3.use_property_split = False
        col_DEBB3.use_property_decorate = False
        col_DEBB3.scale_x = 1.0
        col_DEBB3.scale_y = 1.0
        col_DEBB3.alignment = 'Expand'.upper()
        col_DEBB3.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_DEBB3.prop(bpy.context.object.animation_data.action, 'sna_editor_from_group', text='', icon_value=0, emboss=True)
        col_DEBB3.prop(bpy.context.object.animation_data.action, 'sna_editor_from_fcurve', text='', icon_value=0, emboss=True)
        col_DE1EC.separator(factor=1.0)
        op = col_DE1EC.operator('sna.set_selected_fcurve_c68f3', text='Set Selected', icon_value=0, emboss=True, depress=False)
        op.sna_is_to_child_link = False


def sna_parent_link_ui_61779(layout_function, glink_collection):
    box_BF2B5 = layout_function.box()
    box_BF2B5.alert = False
    box_BF2B5.enabled = True
    box_BF2B5.active = True
    box_BF2B5.use_property_split = False
    box_BF2B5.use_property_decorate = False
    box_BF2B5.alignment = 'Expand'.upper()
    box_BF2B5.scale_x = 1.0
    box_BF2B5.scale_y = 1.0
    box_BF2B5.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_766E4 = box_BF2B5.row(heading='', align=False)
    row_766E4.alert = False
    row_766E4.enabled = True
    row_766E4.active = True
    row_766E4.use_property_split = False
    row_766E4.use_property_decorate = False
    row_766E4.scale_x = 1.0
    row_766E4.scale_y = 1.0
    row_766E4.alignment = 'Expand'.upper()
    row_766E4.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
    row_766E4.prop(glink_collection, 'is_to_link_open', text='', icon_value=(46 if glink_collection.is_to_link_open else 45), emboss=False)
    row_766E4.label(text='Link To', icon_value=0)
    if glink_collection.is_to_valid:
        pass
    else:
        row_766E4.label(text='Not Valid', icon_value=2)
    if glink_collection.is_to_link_open:
        col_828CA = box_BF2B5.column(heading='', align=False)
        col_828CA.alert = False
        col_828CA.enabled = True
        col_828CA.active = True
        col_828CA.use_property_split = False
        col_828CA.use_property_decorate = False
        col_828CA.scale_x = 1.0
        col_828CA.scale_y = 1.0
        col_828CA.alignment = 'Expand'.upper()
        col_828CA.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_6DB99 = col_828CA.row(heading='', align=False)
        row_6DB99.alert = False
        row_6DB99.enabled = True
        row_6DB99.active = True
        row_6DB99.use_property_split = False
        row_6DB99.use_property_decorate = False
        row_6DB99.scale_x = 1.0
        row_6DB99.scale_y = 1.0
        row_6DB99.alignment = 'Expand'.upper()
        row_6DB99.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_6D23A = row_6DB99.column(heading='', align=False)
        col_6D23A.alert = False
        col_6D23A.enabled = True
        col_6D23A.active = True
        col_6D23A.use_property_split = False
        col_6D23A.use_property_decorate = False
        col_6D23A.scale_x = 1.0
        col_6D23A.scale_y = 1.0
        col_6D23A.alignment = 'Right'.upper()
        col_6D23A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_6D23A.label(text='Action : ', icon_value=0)
        col_6D23A.label(text='Group : ', icon_value=0)
        col_6D23A.label(text='F-Curve : ', icon_value=0)
        col_47BEC = row_6DB99.column(heading='', align=False)
        col_47BEC.alert = False
        col_47BEC.enabled = True
        col_47BEC.active = True
        col_47BEC.use_property_split = False
        col_47BEC.use_property_decorate = False
        col_47BEC.scale_x = 1.0
        col_47BEC.scale_y = 1.0
        col_47BEC.alignment = 'Expand'.upper()
        col_47BEC.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_47BEC.prop(bpy.context.object.animation_data.action, 'sna_editor_to_action', text='', icon_value=0, emboss=True)
        col_47BEC.prop(bpy.context.object.animation_data.action, 'sna_editor_to_group', text='', icon_value=0, emboss=True)
        col_47BEC.prop(bpy.context.object.animation_data.action, 'sna_editor_to_fcurve', text='', icon_value=0, emboss=True)
        col_828CA.separator(factor=1.0)
        op = col_828CA.operator('sna.set_selected_fcurve_c68f3', text='Set Selected', icon_value=0, emboss=True, depress=False)
        op.sna_is_to_child_link = True


class SNA_OT_Set_Selected_Fcurve_C68F3(bpy.types.Operator):
    bl_idname = "sna.set_selected_fcurve_c68f3"
    bl_label = "Set Selected FCurve"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    sna_is_to_child_link: bpy.props.BoolProperty(name='Is to child link', description='', options={'HIDDEN'}, default=False)

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        action = None
        group_name = None
        data_path = None
        array_index = None
        is_found = None
        action = None
        group_name = ""
        data_path = ""
        array_index = 0
        is_found = False
        for obj in bpy.context.selected_objects:
            if obj.animation_data is not None and obj.animation_data.action is not None:
                act = bpy.context.object.animation_data.action
                for group in act.groups:
                    for channel in group.channels:
                        if channel.select == True:
                            action = act
                            group_name = group.name
                            data_path = channel.data_path
                            array_index = channel.array_index
                            is_found = True
                            break
                    if is_found:
                        break
                if is_found:
                    break
        if is_found:
            if self.sna_is_to_child_link:
                bpy.context.object.animation_data.action.sna_editor_to_action = action
                bpy.context.object.animation_data.action.sna_editor_to_group = group_name
                fcurve_0_6e323 = sna_create_fcurve_name_B67F8(data_path, array_index, group_name)
                bpy.context.object.animation_data.action.sna_editor_to_fcurve = fcurve_0_6e323
            else:
                bpy.context.object.animation_data.action.sna_editor_from_group = group_name
                fcurve_0_69ae9 = sna_create_fcurve_name_B67F8(data_path, array_index, group_name)
                bpy.context.object.animation_data.action.sna_editor_from_fcurve = fcurve_0_69ae9
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_editor_from_fcurve_enum_items(self, context):
    enum_items = sna_get_fcurves_display_885C9(bpy.context.object.animation_data.action.name, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].from_group)
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_editor_from_group_enum_items(self, context):
    enum_items = sna_get_action_groups_0760C(bpy.context.object.animation_data.action.name)
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_editor_to_group_enum_items(self, context):
    enum_items = sna_get_action_groups_0760C(bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].to_action)
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_editor_to_fcurve_enum_items(self, context):
    enum_items = sna_get_fcurves_display_885C9(bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].to_action, bpy.context.object.animation_data.action.sna_glink_collection[bpy.context.object.animation_data.action.sna_editor_link_index].to_group)
    return [make_enum_item(item[0], item[1], item[2], item[3], i) for i, item in enumerate(enum_items)]


def sna_get_action_groups_0760C(Action):
    enums_for_glink['sna_temp_group_list'] = []
    if ((Action != '') and (Action != 'NONE')):
        for i_BD0A5 in range(len(bpy.data.actions[Action].groups)):
            enums_for_glink['sna_temp_group_list'].append([bpy.data.actions[Action].groups[i_BD0A5].name, bpy.data.actions[Action].groups[i_BD0A5].name, '', 0])
    enums_for_glink['sna_temp_group_list'].append(['NONE', 'NONE', '', 0])
    return enums_for_glink['sna_temp_group_list']


def sna_get_fcurves_display_885C9(Action, Group):
    enums_for_glink['sna_temp_fcurve_list'] = []
    if ((Action != '') and (Action != 'NONE') and (Group != '') and (Group != 'NONE')):
        for i_7E228 in range(len(bpy.data.actions[Action].groups[Group].channels)):
            fcurve_0_b660d = sna_create_fcurve_name_B67F8(bpy.data.actions[Action].groups[Group].channels[i_7E228].data_path, bpy.data.actions[Action].groups[Group].channels[i_7E228].array_index, Group)
            enums_for_glink['sna_temp_fcurve_list'].append([fcurve_0_b660d, fcurve_0_b660d, '', 0])
    enums_for_glink['sna_temp_fcurve_list'].append(['NONE', 'NONE', '', 0])
    return enums_for_glink['sna_temp_fcurve_list']


def sna_create_fcurve_name_B67F8(data_path, array_index, group):
    data_path = data_path
    array_index = array_index
    group_name = group
    item_name = None
    first_letter = str(array_index)
    bone_name = ""
    channel_name = ""
    as_is = False
    if data_path.startswith("pose"):
        data_list = data_path.split(".")
        path = data_list[len(data_list) - 1]
        bone_name = data_path.replace("pose.bones[\"", "").replace("\"]." + path, "")
        data_path = path
        channel_name = path
    elif data_path.startswith("[\""):
        data_path = data_path.replace("[\"", "").replace("\"]", "")
        as_is = True
    elif data_path.startswith("delta"):
        channel_name = data_path.replace("delta_", "")
    else:
        channel_name = data_path
    if (channel_name == "location" or channel_name == "scale" or channel_name == "rotation_euler"
        or channel_name == "rotation_euler" ):
        if array_index == 0:
            first_letter = "X"
        elif array_index == 1:
            first_letter = "Y"
        elif array_index == 2:
            first_letter = "Z"
    elif channel_name == "rotation_quaternion" or channel_name == "rotation_axis_angle" :
        if array_index == 0:
            first_letter = "W"
        elif array_index == 1:
            first_letter = "X"
        elif array_index == 2:
            first_letter = "Y"
        elif array_index == 3:
            first_letter = "Z"
    item_name = data_path
    if not as_is:
        item_name = first_letter + " " + data_path.replace("_", " ").title()
    if bone_name != "" and group_name.find(bone_name) == -1:
        item_name = item_name + " (" + bone_name + ")"
    return item_name


def sna_get_fcurve_data_1A51D(Action, Group, FCurve):
    if ((FCurve != '') and (FCurve != 'NONE')):
        for i_77FD1 in range(len(bpy.data.actions[Action].groups[Group].channels)):
            data_path = bpy.data.actions[Action].groups[Group].channels[i_77FD1].data_path
            array_index = bpy.data.actions[Action].groups[Group].channels[i_77FD1].array_index
            group_name = Group
            item_name = None
            first_letter = str(array_index)
            bone_name = ""
            channel_name = ""
            as_is = False
            if data_path.startswith("pose"):
                data_list = data_path.split(".")
                path = data_list[len(data_list) - 1]
                bone_name = data_path.replace("pose.bones[\"", "").replace("\"]." + path, "")
                data_path = path
                channel_name = path
            elif data_path.startswith("[\""):
                data_path = data_path.replace("[\"", "").replace("\"]", "")
                as_is = True
            elif data_path.startswith("delta"):
                channel_name = data_path.replace("delta_", "")
            else:
                channel_name = data_path
            if (channel_name == "location" or channel_name == "scale" or channel_name == "rotation_euler"
                or channel_name == "rotation_euler" ):
                if array_index == 0:
                    first_letter = "X"
                elif array_index == 1:
                    first_letter = "Y"
                elif array_index == 2:
                    first_letter = "Z"
            elif channel_name == "rotation_quaternion" or channel_name == "rotation_axis_angle" :
                if array_index == 0:
                    first_letter = "W"
                elif array_index == 1:
                    first_letter = "X"
                elif array_index == 2:
                    first_letter = "Y"
                elif array_index == 3:
                    first_letter = "Z"
            item_name = data_path
            if not as_is:
                item_name = first_letter + " " + data_path.replace("_", " ").title()
            if bone_name != "" and group_name.find(bone_name) == -1:
                item_name = item_name + " (" + bone_name + ")"
            if (item_name == FCurve):
                return [bpy.data.actions[Action].groups[Group].channels[i_77FD1].data_path, bpy.data.actions[Action].groups[Group].channels[i_77FD1].array_index, True]
    else:
        return ['', 0, False]


def sna_fcurve_loop_47521(layout_function, fcurve_tuple, action_name, action_type, group, group_type):
    if sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[7]:
        row_A4C82 = layout_function.row(heading='', align=True)
        row_A4C82.alert = False
        row_A4C82.enabled = True
        row_A4C82.active = True
        row_A4C82.use_property_split = False
        row_A4C82.use_property_decorate = False
        row_A4C82.scale_x = 1.0
        row_A4C82.scale_y = 1.0
        row_A4C82.alignment = 'Expand'.upper()
        row_A4C82.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_A4C82.separator(factor=2.0)
        box_E124D = row_A4C82.box()
        box_E124D.alert = False
        box_E124D.enabled = True
        box_E124D.active = True
        box_E124D.use_property_split = False
        box_E124D.use_property_decorate = False
        box_E124D.alignment = 'Expand'.upper()
        box_E124D.scale_x = 1.0
        box_E124D.scale_y = 1.0
        box_E124D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_B68F7 = box_E124D.column(heading='', align=False)
        col_B68F7.alert = False
        col_B68F7.enabled = True
        col_B68F7.active = True
        col_B68F7.use_property_split = False
        col_B68F7.use_property_decorate = False
        col_B68F7.scale_x = 1.0
        col_B68F7.scale_y = 1.0
        col_B68F7.alignment = 'Expand'.upper()
        col_B68F7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_20456 = col_B68F7.row(heading='', align=True)
        row_20456.alert = False
        row_20456.enabled = True
        row_20456.active = True
        row_20456.use_property_split = False
        row_20456.use_property_decorate = False
        row_20456.scale_x = 1.0
        row_20456.scale_y = 1.0
        row_20456.alignment = 'Expand'.upper()
        row_20456.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_20456.operator('sna.open_target_in_panel_f9e9b', text='', icon_value=(5 if sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[4] else 4), emboss=False, depress=False)
        op.sna_panel = 'Manager'
        op.sna_target = 'FCurve'
        op.sna_action = action_name
        op.sna_action_type = action_type
        op.sna_group = group
        op.sna_group_type = group_type
        op.sna_fc_path = sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[2]
        op.sna_fc_index = sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[3]
        op.sna_fc_type = sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[1]
        row_20456.label(text=sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[0], icon_value=string_to_icon(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[1]))
        if bpy.context.scene.sna_manager_is_edit_mode:
            op = row_20456.operator('sn.dummy_button_operator', text='', icon_value=21, emboss=True, depress=False)
        else:
            row_01CD6 = row_20456.row(heading='', align=True)
            row_01CD6.alert = False
            row_01CD6.enabled = True
            row_01CD6.active = True
            row_01CD6.use_property_split = False
            row_01CD6.use_property_decorate = False
            row_01CD6.scale_x = 1.0
            row_01CD6.scale_y = 1.0
            row_01CD6.alignment = 'Expand'.upper()
            row_01CD6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            op = row_01CD6.operator('sn.dummy_button_operator', text='', icon_value=555, emboss=sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[6], depress=True)
        if (bpy.context.scene.sna_manager_open_all or sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[4]):
            row_AFEDB = col_B68F7.row(heading='', align=True)
            row_AFEDB.alert = False
            row_AFEDB.enabled = True
            row_AFEDB.active = True
            row_AFEDB.use_property_split = False
            row_AFEDB.use_property_decorate = False
            row_AFEDB.scale_x = 1.0
            row_AFEDB.scale_y = 1.0
            row_AFEDB.alignment = 'Expand'.upper()
            row_AFEDB.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            row_AFEDB.separator(factor=2.0)
            col_D0E76 = row_AFEDB.column(heading='', align=False)
            col_D0E76.alert = False
            col_D0E76.enabled = True
            col_D0E76.active = True
            col_D0E76.use_property_split = False
            col_D0E76.use_property_decorate = False
            col_D0E76.scale_x = 1.0
            col_D0E76.scale_y = 1.0
            col_D0E76.alignment = 'Expand'.upper()
            col_D0E76.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            for i_832FB in range(len(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5])):
                col_D0E76.separator(factor=0.5)
                box_F770B = col_D0E76.box()
                box_F770B.alert = False
                box_F770B.enabled = True
                box_F770B.active = True
                box_F770B.use_property_split = False
                box_F770B.use_property_decorate = False
                box_F770B.alignment = 'Expand'.upper()
                box_F770B.scale_x = 1.0
                box_F770B.scale_y = 1.0
                box_F770B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                col_7F8BD = box_F770B.column(heading='', align=False)
                col_7F8BD.alert = False
                col_7F8BD.enabled = True
                col_7F8BD.active = True
                col_7F8BD.use_property_split = False
                col_7F8BD.use_property_decorate = False
                col_7F8BD.scale_x = 1.0
                col_7F8BD.scale_y = 1.0
                col_7F8BD.alignment = 'Expand'.upper()
                col_7F8BD.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                if bpy.context.scene.sna_manager_is_edit_mode:
                    col_1582A = col_7F8BD.column(heading='', align=False)
                    col_1582A.alert = False
                    col_1582A.enabled = True
                    col_1582A.active = True
                    col_1582A.use_property_split = False
                    col_1582A.use_property_decorate = False
                    col_1582A.scale_x = 1.0
                    col_1582A.scale_y = 1.0
                    col_1582A.alignment = 'Expand'.upper()
                    col_1582A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_738D6 = col_1582A.row(heading='', align=False)
                    row_738D6.alert = False
                    row_738D6.enabled = True
                    row_738D6.active = True
                    row_738D6.use_property_split = False
                    row_738D6.use_property_decorate = False
                    row_738D6.scale_x = 1.0
                    row_738D6.scale_y = 1.0
                    row_738D6.alignment = 'Expand'.upper()
                    row_738D6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_738D6.label(text='Index ' + str(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][1]), icon_value=56)
                    row_BAD48 = row_738D6.row(heading='', align=True)
                    row_BAD48.alert = False
                    row_BAD48.enabled = True
                    row_BAD48.active = True
                    row_BAD48.use_property_split = False
                    row_BAD48.use_property_decorate = False
                    row_BAD48.scale_x = 1.0
                    row_BAD48.scale_y = 1.0
                    row_BAD48.alignment = 'Expand'.upper()
                    row_BAD48.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    op = row_BAD48.operator('sn.dummy_button_operator', text='', icon_value=7, emboss=True, depress=False)
                    op = row_BAD48.operator('sn.dummy_button_operator', text='', icon_value=5, emboss=True, depress=False)
                    op = row_738D6.operator('sna.remove_glink_9dfc2', text='', icon_value=21, emboss=True, depress=False)
                    op.sna_action_name = action_name
                    op.sna_link_index = sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][1]
                    op.sna_do_refresh = True
                    col_1582A.separator(factor=1.0)
                else:
                    col_7F8BD.separator(factor=0.5)
                col_782B1 = col_7F8BD.column(heading='', align=False)
                col_782B1.alert = False
                col_782B1.enabled = True
                col_782B1.active = (not sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].is_deactive)
                col_782B1.use_property_split = False
                col_782B1.use_property_decorate = False
                col_782B1.scale_x = 1.0
                col_782B1.scale_y = 1.0
                col_782B1.alignment = 'Expand'.upper()
                col_782B1.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                if (sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].range_in_parent and (sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].range_options == 'Custom')):
                    row_4191A = col_782B1.row(heading='', align=True)
                    row_4191A.alert = False
                    row_4191A.enabled = True
                    row_4191A.active = True
                    row_4191A.use_property_split = False
                    row_4191A.use_property_decorate = False
                    row_4191A.scale_x = 1.0
                    row_4191A.scale_y = 1.0
                    row_4191A.alignment = 'Expand'.upper()
                    row_4191A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_4191A.label(text='Range : ', icon_value=0)
                    row_4191A.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'range_start', text='', icon_value=0, emboss=True)
                    row_4191A.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'range_end', text='', icon_value=0, emboss=True)
                if sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].offsetx_in_parent:
                    row_15A0C = col_782B1.row(heading='', align=True)
                    row_15A0C.alert = False
                    row_15A0C.enabled = True
                    row_15A0C.active = True
                    row_15A0C.use_property_split = False
                    row_15A0C.use_property_decorate = False
                    row_15A0C.scale_x = 1.0
                    row_15A0C.scale_y = 1.0
                    row_15A0C.alignment = 'Expand'.upper()
                    row_15A0C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_15A0C.label(text='Offset X :', icon_value=0)
                    row_15A0C.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'offset_x', text='', icon_value=0, emboss=True, slider=True)
                if sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].offsety_in_parent:
                    row_45F65 = col_782B1.row(heading='', align=True)
                    row_45F65.alert = False
                    row_45F65.enabled = True
                    row_45F65.active = True
                    row_45F65.use_property_split = False
                    row_45F65.use_property_decorate = False
                    row_45F65.scale_x = 1.0
                    row_45F65.scale_y = 1.0
                    row_45F65.alignment = 'Expand'.upper()
                    row_45F65.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_45F65.label(text='Offset Y :', icon_value=0)
                    row_45F65.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'offset_y', text='', icon_value=0, emboss=True, slider=True)
                if sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].scalex_in_parent:
                    row_6FBBE = col_782B1.row(heading='', align=True)
                    row_6FBBE.alert = False
                    row_6FBBE.enabled = True
                    row_6FBBE.active = True
                    row_6FBBE.use_property_split = False
                    row_6FBBE.use_property_decorate = False
                    row_6FBBE.scale_x = 1.0
                    row_6FBBE.scale_y = 1.0
                    row_6FBBE.alignment = 'Expand'.upper()
                    row_6FBBE.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_6FBBE.label(text='Scale X :', icon_value=0)
                    row_6FBBE.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'offset_x', text='', icon_value=0, emboss=True, slider=True)
                if sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].scaley_in_parent:
                    row_8E90A = col_782B1.row(heading='', align=True)
                    row_8E90A.alert = False
                    row_8E90A.enabled = True
                    row_8E90A.active = True
                    row_8E90A.use_property_split = False
                    row_8E90A.use_property_decorate = False
                    row_8E90A.scale_x = 1.0
                    row_8E90A.scale_y = 1.0
                    row_8E90A.alignment = 'Expand'.upper()
                    row_8E90A.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_8E90A.label(text='Scale Y :', icon_value=0)
                    row_8E90A.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'offset_y', text='', icon_value=0, emboss=True, slider=True)
                col_7F8BD.separator(factor=0.20000000298023224)
                if bpy.context.scene.sna_manager_is_edit_mode:
                    row_C6C7C = col_7F8BD.row(heading='', align=True)
                    row_C6C7C.alert = False
                    row_C6C7C.enabled = True
                    row_C6C7C.active = True
                    row_C6C7C.use_property_split = False
                    row_C6C7C.use_property_decorate = False
                    row_C6C7C.scale_x = 1.2000000476837158
                    row_C6C7C.scale_y = 1.0
                    row_C6C7C.alignment = 'Expand'.upper()
                    row_C6C7C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    op = row_C6C7C.operator('sna.edit_glink_b1df3', text='Edit Link', icon_value=197, emboss=True, depress=False)
                    op.sna_action_name = action_name
                    op.sna_link_index = sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][1]
                    row_C6C7C.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'is_deactive', text='', icon_value=555, emboss=True, toggle=True)
                    row_12F7C = row_C6C7C.row(heading='', align=True)
                    row_12F7C.alert = False
                    row_12F7C.enabled = (not sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0].is_deactive)
                    row_12F7C.active = True
                    row_12F7C.use_property_split = False
                    row_12F7C.use_property_decorate = False
                    row_12F7C.scale_x = 1.0800000429153442
                    row_12F7C.scale_y = 1.0
                    row_12F7C.alignment = 'Expand'.upper()
                    row_12F7C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    row_12F7C.prop(sna_get_fcurve_tuple_0B099(fcurve_tuple, False)[5][i_832FB][0], 'pivot_frame', text='', icon_value=527, emboss=True, toggle=True)


def sna_glink_loop_9D621(layout_function, group_tuple, action_name, action_type, only_selected, is_filter, filter_list):
    if sna_get_group_tuple_B8DC3(group_tuple, only_selected)[5]:
        box_8B18E = layout_function.box()
        box_8B18E.alert = False
        box_8B18E.enabled = True
        box_8B18E.active = True
        box_8B18E.use_property_split = False
        box_8B18E.use_property_decorate = False
        box_8B18E.alignment = 'Expand'.upper()
        box_8B18E.scale_x = 1.0
        box_8B18E.scale_y = 1.0
        box_8B18E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_5DF8F = box_8B18E.column(heading='', align=False)
        col_5DF8F.alert = False
        col_5DF8F.enabled = True
        col_5DF8F.active = True
        col_5DF8F.use_property_split = False
        col_5DF8F.use_property_decorate = False
        col_5DF8F.scale_x = 1.0
        col_5DF8F.scale_y = 1.0
        col_5DF8F.alignment = 'Expand'.upper()
        col_5DF8F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_C1A4E = col_5DF8F.row(heading='', align=True)
        row_C1A4E.alert = False
        row_C1A4E.enabled = True
        row_C1A4E.active = True
        row_C1A4E.use_property_split = False
        row_C1A4E.use_property_decorate = False
        row_C1A4E.scale_x = 1.0
        row_C1A4E.scale_y = 0.8999999761581421
        row_C1A4E.alignment = 'Expand'.upper()
        row_C1A4E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_C1A4E.operator('sna.open_target_in_panel_f9e9b', text='', icon_value=(5 if sna_get_group_tuple_B8DC3(group_tuple, only_selected)[2] else 4), emboss=False, depress=False)
        op.sna_panel = 'Manager'
        op.sna_target = 'Group'
        op.sna_action = action_name
        op.sna_action_type = action_type
        op.sna_group = sna_get_group_tuple_B8DC3(group_tuple, only_selected)[0]
        op.sna_group_type = sna_get_group_tuple_B8DC3(group_tuple, only_selected)[1]
        op.sna_fc_path = ''
        op.sna_fc_index = 0
        op.sna_fc_type = ''
        row_C1A4E.label(text=sna_get_group_tuple_B8DC3(group_tuple, only_selected)[0], icon_value=string_to_icon(sna_get_group_tuple_B8DC3(group_tuple, only_selected)[1]))
        if bpy.context.scene.sna_manager_is_edit_mode:
            op = row_C1A4E.operator('sn.dummy_button_operator', text='', icon_value=21, emboss=True, depress=False)
        else:
            row_B623C = row_C1A4E.row(heading='', align=True)
            row_B623C.alert = False
            row_B623C.enabled = True
            row_B623C.active = True
            row_B623C.use_property_split = False
            row_B623C.use_property_decorate = False
            row_B623C.scale_x = 1.0
            row_B623C.scale_y = 1.0
            row_B623C.alignment = 'Expand'.upper()
            row_B623C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            op = row_B623C.operator('sn.dummy_button_operator', text='', icon_value=555, emboss=sna_get_group_tuple_B8DC3(group_tuple, only_selected)[4], depress=True)
        if (bpy.context.scene.sna_manager_open_all or sna_get_group_tuple_B8DC3(group_tuple, only_selected)[2]):
            if is_filter:
                for i_3AD52 in range(len(filter_list)):
                    layout_function = col_5DF8F
                    sna_fcurve_loop_47521(layout_function, sna_get_group_tuple_B8DC3(group_tuple, only_selected)[3][filter_list[i_3AD52]], action_name, action_type, sna_get_group_tuple_B8DC3(group_tuple, only_selected)[0], sna_get_group_tuple_B8DC3(group_tuple, only_selected)[1])
            else:
                for i_20073 in range(len(sna_get_group_tuple_B8DC3(group_tuple, only_selected)[3])):
                    layout_function = col_5DF8F
                    sna_fcurve_loop_47521(layout_function, sna_get_group_tuple_B8DC3(group_tuple, only_selected)[3][i_20073], action_name, action_type, sna_get_group_tuple_B8DC3(group_tuple, only_selected)[0], sna_get_group_tuple_B8DC3(group_tuple, only_selected)[1])


class SNA_MT_68936(bpy.types.Menu):
    bl_idname = "SNA_MT_68936"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=1)
        layout.operator_context = "INVOKE_DEFAULT"
        op = layout.operator('sna.set_manager_filter_daa48', text='Active Object', icon_value=13, emboss=True, depress=False)
        op.sna_filter = 'ACTIVE'
        op = layout.operator('sna.set_manager_filter_daa48', text='Selected Object', icon_value=256, emboss=True, depress=False)
        op.sna_filter = 'SELECTED'
        op = layout.operator('sna.set_manager_filter_daa48', text='Invalid Links', icon_value=55, emboss=True, depress=False)
        op.sna_filter = 'INVALID'
        layout.separator(factor=0.20000000298023224)
        op = layout.operator('sna.set_manager_filter_daa48', text='No Filter', icon_value=0, emboss=True, depress=False)
        op.sna_filter = 'NONE'


class SNA_OT_Set_Manager_Filter_Daa48(bpy.types.Operator):
    bl_idname = "sna.set_manager_filter_daa48"
    bl_label = "Set Manager Filter"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def sna_filter_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_filter: bpy.props.EnumProperty(name='Filter', description='', options={'HIDDEN'}, items=[('ACTIVE', 'ACTIVE', '', 0, 0), ('SELECTED', 'SELECTED', '', 0, 1), ('INVALID', 'INVALID', '', 0, 2), ('NONE', 'NONE', '', 0, 3)])

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        bpy.context.scene.sna_manager_filter = self.sna_filter
        bpy.context.scene.sna_manager_disable_filter = False
        filter = self.sna_filter
        is_child = bpy.context.scene.sna_manager_is_group_child
        index_list = []
        is_active_selected = False
        is_none = False
        is_active = False
        is_selected = False
        is_filter = False
        list = []
        if is_child:
            list = other_panels['sna_child_links']
        else:
            list = other_panels['sna_parent_links']
        if filter == 'ACTIVE':
            is_active = True
        elif filter == 'SELECTED':
            is_selected = True
        elif filter == 'INVALID':
            is_filter = True
        else:
            is_none = True
        for index in range(len(list)):
            action_tuple = list[index]
            (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
            (action_name, action_type) = (action_data[0], action_data[1])
            (obj_name, obj_type) = (obj_data[0], obj_data[1])
            if filter == 'INVALID':
                g_list = []
                if action_type == 'ERROR':
                    for g_index in range(len(group_list)):
                        group_tuple = group_list[g_index]
                        (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                        f_list = []
                        for f_index in range(len(fc_list)):
                                f_list.append(f_index)
                        g_list.append([g_index, f_list])
                    index_list.append([index, g_list])
                else:
                    for g_index in range(len(group_list)):
                        group_tuple = group_list[g_index]
                        (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
                        (group_name, group_type) = (group_data[0], group_data[1])
                        f_list = []
                        if group_type == 'ERROR':
                            for f_index in range(len(fc_list)):
                                f_list.append(f_index)
                            g_list.append([g_index, f_list])
                        else:
                            for f_index in range(len(fc_list)):
                                fcurve_tuple = fc_list[f_index]
                                (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                                (fc_path, fc_index, fc_label, fc_type) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3])
                                if fc_type == 'ERROR':
                                    f_list.append(f_index)
                            if len(f_list) != 0:
                                g_list.append([g_index, f_list])
                    if len(g_list) != 0:
                        index_list.append([index, g_list])
        nodetree['sna_filter_list'] = index_list
        nodetree['sna_is_active_filter'] = is_active
        nodetree['sna_is_selected_filter'] = is_selected
        nodetree['sna_is_none_filter'] = is_none
        nodetree['sna_is_filter'] = is_filter
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_MT_F8A8C(bpy.types.Menu):
    bl_idname = "SNA_MT_F8A8C"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=1)
        layout.operator_context = "INVOKE_DEFAULT"
        layout.prop(bpy.context.scene, 'sna_stop_addon', text='Stop Addon', icon_value=0, emboss=True)


class SNA_PT_GLINK_LIST_10E78(bpy.types.Panel):
    bl_label = 'GLink List'
    bl_idname = 'SNA_PT_GLINK_LIST_10E78'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'GLink'
    bl_order = 0
    bl_options = {'HIDE_HEADER'}
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.separator(factor=0.30000001192092896)
        col_76E63 = layout.column(heading='', align=True)
        col_76E63.alert = False
        col_76E63.enabled = True
        col_76E63.active = True
        col_76E63.use_property_split = False
        col_76E63.use_property_decorate = False
        col_76E63.scale_x = 1.0
        col_76E63.scale_y = 1.0
        col_76E63.alignment = 'Expand'.upper()
        col_76E63.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_AA8F6 = col_76E63.row(heading='', align=True)
        row_AA8F6.alert = False
        row_AA8F6.enabled = True
        row_AA8F6.active = True
        row_AA8F6.use_property_split = False
        row_AA8F6.use_property_decorate = False
        row_AA8F6.scale_x = 1.0
        row_AA8F6.scale_y = 1.0
        row_AA8F6.alignment = 'Expand'.upper()
        row_AA8F6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_AA8F6.prop(bpy.context.scene, 'sna_timeline_is_group_child', text='Parent', icon_value=0, emboss=True, toggle=True, invert_checkbox=True)
        row_AA8F6.prop(bpy.context.scene, 'sna_timeline_is_group_child', text='Children', icon_value=0, emboss=True, toggle=True)
        col_76E63.separator(factor=0.699999988079071)
        col_76E63.prop(bpy.context.scene, 'sna_timeline_show_select_fc', text='Selected FCurves', icon_value=0, emboss=True)
        col_76E63.separator(factor=0.5)
        row_D4D1D = col_76E63.row(heading='', align=True)
        row_D4D1D.alert = False
        row_D4D1D.enabled = True
        row_D4D1D.active = True
        row_D4D1D.use_property_split = False
        row_D4D1D.use_property_decorate = False
        row_D4D1D.scale_x = 1.100000023841858
        row_D4D1D.scale_y = 1.100000023841858
        row_D4D1D.alignment = 'Expand'.upper()
        row_D4D1D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_D4D1D.label(text='GLink List : ', icon_value=0)
        layout_function = row_D4D1D
        sna_track_and_refresh_464F5(layout_function, True)
        row_D4D1D.separator(factor=0.30000001192092896)
        row_D4D1D.prop(bpy.context.scene, 'sna_timeline_is_edit_mode', text='', icon_value=197, emboss=True)
        col_76E63.separator(factor=0.5)
        if (len(sna_t_filter_list_7CBB0(bpy.context.scene.sna_timeline_is_group_child, bpy.context.scene.sna_timeline_show_select_fc)) == 0):
            box_A3BB7 = col_76E63.box()
            box_A3BB7.alert = False
            box_A3BB7.enabled = True
            box_A3BB7.active = True
            box_A3BB7.use_property_split = False
            box_A3BB7.use_property_decorate = False
            box_A3BB7.alignment = 'Expand'.upper()
            box_A3BB7.scale_x = 1.0
            box_A3BB7.scale_y = 1.0
            box_A3BB7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_A3BB7.label(text='No Item to Show', icon_value=110)
        else:
            for i_D51D8 in range(len(sna_t_filter_list_7CBB0(bpy.context.scene.sna_timeline_is_group_child, bpy.context.scene.sna_timeline_show_select_fc))):
                for i_9EF79 in range(len(sna_t_filter_list_7CBB0(bpy.context.scene.sna_timeline_is_group_child, bpy.context.scene.sna_timeline_show_select_fc)[i_D51D8][1])):
                    layout_function = col_76E63
                    sna_glink_loop_9D621(layout_function, sna_get_action_tuple_6784A((other_panels['sna_child_links'] if bpy.context.scene.sna_timeline_is_group_child else other_panels['sna_parent_links'])[sna_t_filter_list_7CBB0(bpy.context.scene.sna_timeline_is_group_child, bpy.context.scene.sna_timeline_show_select_fc)[i_D51D8][0]], False, False)[5][sna_t_filter_list_7CBB0(bpy.context.scene.sna_timeline_is_group_child, bpy.context.scene.sna_timeline_show_select_fc)[i_D51D8][1][i_9EF79][0]], '', '', False, False, sna_t_filter_list_7CBB0(bpy.context.scene.sna_timeline_is_group_child, bpy.context.scene.sna_timeline_show_select_fc)[i_D51D8][1][i_9EF79][1])


def sna_get_action_tuple_6784A(action_tuple, only_active_obj, only_selected_obj):
    action_tuple = action_tuple
    only_active_obj = only_active_obj
    only_selected_obj = only_selected_obj
    action_name = None
    action_type = None
    object_name = None
    object_type = None
    action_is_open = None
    group_list = None
    is_act_deactive = None
    condition = None
    (action_data, obj_data, act_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
    (action_name, action_type) = (action_data[0], action_data[1])
    (object_name, object_type, obj) = obj_data
    action_is_open = act_is_open[0]
    is_act_deactive = act_is_open[1]
    condition = True
    if only_selected_obj:
        condition = obj.select_get()
    elif (only_active_obj and bpy.context.object is None) or (only_active_obj and object_name != bpy.context.object.name):
        condition = False
    return [action_name, action_type, object_name, object_type, action_is_open, group_list, is_act_deactive, condition]


def sna_get_group_tuple_B8DC3(group_tuple, only_selected):
    group_tuple = group_tuple
    only_selected = only_selected
    group_name = None
    group_type = None
    group_is_open = None
    fc_list = None
    is_grp_deactive = None
    condition = None
    (group_data, grp_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
    (group_name, group_type, group) = (group_data[0], group_data[1], group_data[2])
    group_is_open = grp_is_open[0]
    is_grp_deactive = grp_is_open[3]
    condition = True
    if only_selected:
        condition = group.select
    return [group_name, group_type, group_is_open, fc_list, is_grp_deactive, condition]


def sna_get_fcurve_tuple_0B099(fcurve_tuple, only_selected):
    fcurve_tuple = fcurve_tuple
    only_selected = only_selected
    fc_label = None
    fc_type = None
    fc_path = None
    fc_index = None
    fc_is_open = None
    link_list = None
    is_fc_deactive = None
    condition = None
    (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
    (fc_path, fc_index, fc_label, fc_type, fc) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3], fcurve_data[4])
    fc_is_open = fcurve_is_open[0]
    is_fc_deactive = fcurve_is_open[3]
    condition = True
    if only_selected:
        condition = fc.select
    return [fc_label, fc_type, fc_path, fc_index, fc_is_open, link_list, is_fc_deactive, condition]


def sna_t_filter_list_7CBB0(Is_Group_Child, Is_Selected_FC):
    is_child = Is_Group_Child
    is_selected_fc = Is_Selected_FC
    index_list = None
    index_list = []
    list = []
    if is_child:
        list = other_panels['sna_child_links']
    else:
        list = other_panels['sna_parent_links']
    for index in range(len(list)):
        action_tuple = list[index]
        (action_data, obj_data, action_is_open, group_list) = (action_tuple[0], action_tuple[1], action_tuple[2], action_tuple[3])
        (action_name, action_type) = (action_data[0], action_data[1])
        (obj_name, obj_type) = (obj_data[0], obj_data[1])
        g_list = []
        for g_index in range(len(group_list)):
            group_tuple = group_list[g_index]
            (group_data, group_is_open, fc_list) = (group_tuple[0], group_tuple[1], group_tuple[2])
            (group_name, group_type, group) = (group_data[0], group_data[1], group_data[2])
            f_list = []
            if group is not None:
                if not is_selected_fc:
                    if group.select:
                        for f_index in range(len(fc_list)):
                            f_list.append(f_index)
                        g_list.append([g_index, f_list])
                else:
                    for f_index in range(len(fc_list)):
                        fcurve_tuple = fc_list[f_index]
                        (fcurve_data, fcurve_is_open, link_list) = (fcurve_tuple[0], fcurve_tuple[1], fcurve_tuple[2])
                        (fc_path, fc_index, fc_label, fc_type, fc) = (fcurve_data[0], fcurve_data[1], fcurve_data[2], fcurve_data[3], fcurve_data[4])
                        if fc is not None and fc.select:
                            f_list.append(f_index)
                    if len(f_list) != 0:
                        g_list.append([g_index, f_list])
            if len(g_list) != 0:
                index_list.append([index, g_list])
    return index_list


class SNA_PT_CHILD_LINKS_A59E6(bpy.types.Panel):
    bl_label = 'Child Links'
    bl_idname = 'SNA_PT_CHILD_LINKS_A59E6'
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'GLink'
    bl_order = 0
    bl_options = {'HIDE_HEADER'}
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.separator(factor=0.30000001192092896)
        col_C757C = layout.column(heading='', align=True)
        col_C757C.alert = False
        col_C757C.enabled = True
        col_C757C.active = True
        col_C757C.use_property_split = False
        col_C757C.use_property_decorate = False
        col_C757C.scale_x = 1.0
        col_C757C.scale_y = 1.0
        col_C757C.alignment = 'Expand'.upper()
        col_C757C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_6B125 = col_C757C.row(heading='', align=True)
        row_6B125.alert = False
        row_6B125.enabled = True
        row_6B125.active = True
        row_6B125.use_property_split = False
        row_6B125.use_property_decorate = False
        row_6B125.scale_x = 1.0
        row_6B125.scale_y = 1.0
        row_6B125.alignment = 'Expand'.upper()
        row_6B125.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_6B125.prop(bpy.context.scene, 'sna_graph_is_group_child', text='Parent', icon_value=0, emboss=True, toggle=True, invert_checkbox=True)
        row_6B125.prop(bpy.context.scene, 'sna_graph_is_group_child', text='Children', icon_value=0, emboss=True, toggle=True)
        col_C757C.separator(factor=0.699999988079071)
        col_C757C.prop(bpy.context.scene, 'sna_graph_show_select_fc', text='Selected FCurves', icon_value=0, emboss=True)
        col_C757C.separator(factor=0.5)
        row_BE443 = col_C757C.row(heading='', align=True)
        row_BE443.alert = False
        row_BE443.enabled = True
        row_BE443.active = True
        row_BE443.use_property_split = False
        row_BE443.use_property_decorate = False
        row_BE443.scale_x = 1.100000023841858
        row_BE443.scale_y = 1.100000023841858
        row_BE443.alignment = 'Expand'.upper()
        row_BE443.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_BE443.label(text='GLink List : ', icon_value=0)
        layout_function = row_BE443
        sna_track_and_refresh_464F5(layout_function, True)
        row_BE443.separator(factor=0.30000001192092896)
        row_BE443.prop(bpy.context.scene, 'sna_graph_is_edit_mode', text='', icon_value=197, emboss=True)
        col_C757C.separator(factor=0.5)
        if (len(sna_t_filter_list_7CBB0(bpy.context.scene.sna_graph_is_group_child, bpy.context.scene.sna_graph_show_select_fc)) == 0):
            box_0783D = col_C757C.box()
            box_0783D.alert = False
            box_0783D.enabled = True
            box_0783D.active = True
            box_0783D.use_property_split = False
            box_0783D.use_property_decorate = False
            box_0783D.alignment = 'Expand'.upper()
            box_0783D.scale_x = 1.0
            box_0783D.scale_y = 1.0
            box_0783D.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_0783D.label(text='No Item to Show', icon_value=110)
        else:
            for i_9F714 in range(len(sna_t_filter_list_7CBB0(bpy.context.scene.sna_graph_is_group_child, bpy.context.scene.sna_graph_show_select_fc))):
                for i_9056F in range(len(sna_t_filter_list_7CBB0(bpy.context.scene.sna_graph_is_group_child, bpy.context.scene.sna_graph_show_select_fc)[i_9F714][1])):
                    layout_function = col_C757C
                    sna_glink_loop_9D621(layout_function, sna_get_action_tuple_6784A((other_panels['sna_child_links'] if bpy.context.scene.sna_graph_is_group_child else other_panels['sna_parent_links'])[sna_t_filter_list_7CBB0(bpy.context.scene.sna_graph_is_group_child, bpy.context.scene.sna_graph_show_select_fc)[i_9F714][0]], False, False)[5][sna_t_filter_list_7CBB0(bpy.context.scene.sna_graph_is_group_child, bpy.context.scene.sna_graph_show_select_fc)[i_9F714][1][i_9056F][0]], '', '', False, False, sna_t_filter_list_7CBB0(bpy.context.scene.sna_graph_is_group_child, bpy.context.scene.sna_graph_show_select_fc)[i_9F714][1][i_9056F][1])


class SNA_GROUP_sna_glink_group(bpy.types.PropertyGroup):
    link_id: bpy.props.IntProperty(name='Link Id', description='', default=0, subtype='NONE')
    is_deactive: bpy.props.BoolProperty(name='Is Deactive', description='', default=False)
    pivot_frame: bpy.props.EnumProperty(name='Pivot Frame', description='', items=[('Zero', 'Zero', '', 0, 0), ('First Keyframe', 'First Keyframe', '', 0, 1), ('Last Keyframe', 'Last Keyframe', 'Only if Range is Available', 0, 2), ('Range End', 'Range End', 'Only if Range is Custom', 0, 3)])
    pivot_value: bpy.props.EnumProperty(name='Pivot Value', description='', items=[('Zero', 'Zero', '', 0, 0), ('First Keyframe', 'First Keyframe', '', 0, 1), ('Last Keyframe', 'Last Keyframe', '', 0, 2)])
    range_options: bpy.props.EnumProperty(name='Range Options', description='', items=[('Available', 'Available', '', 0, 0), ('Custom', 'Custom', '', 0, 1)])
    border_key_range: bpy.props.BoolProperty(name='Border Key Range', description='', default=False)
    range_start: bpy.props.IntProperty(name='Range Start', description='', default=0, subtype='UNSIGNED')
    range_end: bpy.props.IntProperty(name='Range End', description='', default=250, subtype='UNSIGNED')
    flip_x_axis: bpy.props.BoolProperty(name='Flip X Axis', description='', default=False)
    flip_y_axis: bpy.props.BoolProperty(name='Flip Y Axis', description='', default=False)
    scale_x: bpy.props.FloatProperty(name='Scale X', description='', default=1.0, subtype='NONE', unit='NONE', soft_min=0.0, soft_max=2.0, step=3, precision=3)
    scale_y: bpy.props.FloatProperty(name='Scale Y', description='', default=1.0, subtype='NONE', unit='NONE', soft_min=0.0, soft_max=2.0, step=3, precision=3)
    offset_x: bpy.props.FloatProperty(name='Offset X', description='', default=0.0, subtype='NONE', unit='NONE', soft_min=-10.0, soft_max=10.0, step=3, precision=4)
    offset_y: bpy.props.FloatProperty(name='Offset Y', description='', default=0.0, subtype='NONE', unit='NONE', soft_min=-10.0, soft_max=10.0, step=3, precision=4)
    range_in_parent: bpy.props.BoolProperty(name='range_in_parent', description='', default=False)
    offsetx_in_parent: bpy.props.BoolProperty(name='offsetx_in_parent', description='', default=True)
    offsety_in_parent: bpy.props.BoolProperty(name='offsety_in_parent', description='', default=False)
    scalex_in_parent: bpy.props.BoolProperty(name='scalex_in_parent', description='', default=True)
    scaley_in_parent: bpy.props.BoolProperty(name='scaley_in_parent', description='', default=False)
    is_from_link_open: bpy.props.BoolProperty(name='Is From Link Open', description='', default=False)
    from_group: bpy.props.StringProperty(name='From Group', description='', default='', subtype='NONE', maxlen=0)
    from_data_path: bpy.props.StringProperty(name='From Data Path', description='', default='', subtype='NONE', maxlen=0)
    from_array_index: bpy.props.IntProperty(name='From Array Index', description='', default=0, subtype='NONE')
    is_to_link_open: bpy.props.BoolProperty(name='Is To Link Open', description='', default=False)
    to_action: bpy.props.StringProperty(name='To Action', description='', default='', subtype='NONE', maxlen=0)
    to_group: bpy.props.StringProperty(name='To Group', description='', default='', subtype='NONE', maxlen=0)
    to_data_path: bpy.props.StringProperty(name='To Data Path', description='', default='', subtype='NONE', maxlen=0)
    to_array_index: bpy.props.IntProperty(name='To Array Index', description='', default=0, subtype='NONE')
    is_batch_armature: bpy.props.BoolProperty(name='Is Batch Armature', description='', default=False)
    is_from_valid: bpy.props.BoolProperty(name='Is From Valid', description='', default=False)
    is_to_valid: bpy.props.BoolProperty(name='Is To Valid', description='', default=False)


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.utils.register_class(SNA_GROUP_sna_glink_group)
    bpy.types.Scene.sna_new_property = bpy.props.BoolProperty(name='New Property', description='', default=False)
    bpy.types.Scene.sna_new_property_001 = bpy.props.PointerProperty(name='New Property 001', description='', type=bpy.types.Object)
    bpy.types.Scene.sna_new_property_002 = bpy.props.StringProperty(name='New Property 002', description='', default='', subtype='NONE', maxlen=0)
    bpy.types.Scene.sna_new_property_003 = bpy.props.FloatProperty(name='New Property 003', description='', default=0.0, subtype='NONE', unit='NONE', soft_min=0.0, soft_max=20.0, step=3, precision=4)
    bpy.types.Action.sna_glink_collection = bpy.props.CollectionProperty(name='GLink Collection', description='', type=SNA_GROUP_sna_glink_group)
    bpy.types.Action.sna_editor_link_index = bpy.props.IntProperty(name='Editor Link Index', description='', default=0, subtype='NONE')
    bpy.types.Action.sna_editor_from_group = bpy.props.EnumProperty(name='Editor From Group', description='', items=sna_editor_from_group_enum_items, update=sna_update_sna_editor_from_group_A46E2)
    bpy.types.Action.sna_editor_from_fcurve = bpy.props.EnumProperty(name='Editor From FCurve', description='', items=sna_editor_from_fcurve_enum_items, update=sna_update_sna_editor_from_fcurve_E87BD)
    bpy.types.Action.sna_editor_to_group = bpy.props.EnumProperty(name='Editor To Group', description='', items=sna_editor_to_group_enum_items, update=sna_update_sna_editor_to_group_AD22C)
    bpy.types.Action.sna_editor_to_fcurve = bpy.props.EnumProperty(name='Editor To FCurve', description='', items=sna_editor_to_fcurve_enum_items, update=sna_update_sna_editor_to_fcurve_0505D)
    bpy.types.Action.sna_editor_to_action = bpy.props.PointerProperty(name='Editor To Action', description='', type=bpy.types.Action, update=sna_update_sna_editor_to_action_D53F1)
    bpy.types.Scene.sna_manager_is_group_child = bpy.props.BoolProperty(name='Manager Is Group Child', description='', default=False)
    bpy.types.Scene.sna_manager_is_edit_mode = bpy.props.BoolProperty(name='Manager Is Edit Mode', description='', default=False)
    bpy.types.Scene.sna_manager_filter = bpy.props.EnumProperty(name='Manager Filter', description='', items=[('ACTIVE', 'ACTIVE', '', 0, 0), ('SELECTED', 'SELECTED', '', 0, 1), ('INVALID', 'INVALID', '', 0, 2), ('NONE', 'NONE', '', 0, 3)])
    bpy.types.Scene.sna_manager_disable_filter = bpy.props.BoolProperty(name='Manager Disable Filter', description='', default=False)
    bpy.types.Scene.sna_manager_open_all = bpy.props.BoolProperty(name='Manager Open All', description='', default=False)
    bpy.types.Scene.sna_timeline_is_group_child = bpy.props.BoolProperty(name='Timeline Is Group Child', description='', default=False)
    bpy.types.Scene.sna_timeline_show_select_fc = bpy.props.BoolProperty(name='Timeline Show Select FC', description='', default=False)
    bpy.types.Scene.sna_timeline_is_edit_mode = bpy.props.BoolProperty(name='Timeline is Edit Mode', description='', default=False)
    bpy.types.Scene.sna_graph_is_group_child = bpy.props.BoolProperty(name='Graph Is Group Child', description='', default=False)
    bpy.types.Scene.sna_graph_show_select_fc = bpy.props.BoolProperty(name='Graph Show Select Fc', description='', default=False)
    bpy.types.Scene.sna_graph_is_edit_mode = bpy.props.BoolProperty(name='Graph Is Edit Mode', description='', default=False)
    bpy.types.Scene.sna_stop_addon = bpy.props.BoolProperty(name='Stop Addon', description='', default=False)
    bpy.types.Scene.sna_is_tracking = bpy.props.BoolProperty(name='is Tracking', description='', default=False)
    bpy.utils.register_class(SNA_OT_Open_Target_In_Panel_F9E9B)
    bpy.utils.register_class(SNA_OT_Remove_Glink_9Dfc2)
    bpy.utils.register_class(SNA_OT_Edit_Glink_B1Df3)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post_handler_82C62)
    bpy.utils.register_class(SNA_PT_GLINK_MANAGER_DD502)
    bpy.utils.register_class(SNA_OT_Create_Link_Aedf6)
    bpy.utils.register_class(SNA_PT_GLINK_CREATOR_76BD4)
    bpy.utils.register_class(SNA_OT_Refresh_Operator_C9416)
    bpy.utils.register_class(SNA_OT_Set_Selected_Fcurve_C68F3)
    bpy.utils.register_class(SNA_MT_68936)
    bpy.utils.register_class(SNA_OT_Set_Manager_Filter_Daa48)
    bpy.utils.register_class(SNA_MT_F8A8C)
    bpy.utils.register_class(SNA_PT_GLINK_LIST_10E78)
    bpy.utils.register_class(SNA_PT_CHILD_LINKS_A59E6)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_is_tracking
    del bpy.types.Scene.sna_stop_addon
    del bpy.types.Scene.sna_graph_is_edit_mode
    del bpy.types.Scene.sna_graph_show_select_fc
    del bpy.types.Scene.sna_graph_is_group_child
    del bpy.types.Scene.sna_timeline_is_edit_mode
    del bpy.types.Scene.sna_timeline_show_select_fc
    del bpy.types.Scene.sna_timeline_is_group_child
    del bpy.types.Scene.sna_manager_open_all
    del bpy.types.Scene.sna_manager_disable_filter
    del bpy.types.Scene.sna_manager_filter
    del bpy.types.Scene.sna_manager_is_edit_mode
    del bpy.types.Scene.sna_manager_is_group_child
    del bpy.types.Action.sna_editor_to_action
    del bpy.types.Action.sna_editor_to_fcurve
    del bpy.types.Action.sna_editor_to_group
    del bpy.types.Action.sna_editor_from_fcurve
    del bpy.types.Action.sna_editor_from_group
    del bpy.types.Action.sna_editor_link_index
    del bpy.types.Action.sna_glink_collection
    del bpy.types.Scene.sna_new_property_003
    del bpy.types.Scene.sna_new_property_002
    del bpy.types.Scene.sna_new_property_001
    del bpy.types.Scene.sna_new_property
    bpy.utils.unregister_class(SNA_GROUP_sna_glink_group)
    bpy.utils.unregister_class(SNA_OT_Open_Target_In_Panel_F9E9B)
    bpy.utils.unregister_class(SNA_OT_Remove_Glink_9Dfc2)
    bpy.utils.unregister_class(SNA_OT_Edit_Glink_B1Df3)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post_handler_82C62)
    bpy.utils.unregister_class(SNA_PT_GLINK_MANAGER_DD502)
    bpy.utils.unregister_class(SNA_OT_Create_Link_Aedf6)
    bpy.utils.unregister_class(SNA_PT_GLINK_CREATOR_76BD4)
    bpy.utils.unregister_class(SNA_OT_Refresh_Operator_C9416)
    bpy.utils.unregister_class(SNA_OT_Set_Selected_Fcurve_C68F3)
    bpy.utils.unregister_class(SNA_MT_68936)
    bpy.utils.unregister_class(SNA_OT_Set_Manager_Filter_Daa48)
    bpy.utils.unregister_class(SNA_MT_F8A8C)
    bpy.utils.unregister_class(SNA_PT_GLINK_LIST_10E78)
    bpy.utils.unregister_class(SNA_PT_CHILD_LINKS_A59E6)
