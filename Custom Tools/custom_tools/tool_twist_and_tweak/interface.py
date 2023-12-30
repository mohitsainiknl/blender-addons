import bpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import ui, rig

class CST_UL_display_bone_list(bpy.types.UIList):
    def draw_item(self, context, row, data, item, icon, active_data, active_propname, index):
        row.prop(item, 'bone', text='', icon_value=0, emboss=False)

class CST_UL_display_create_twist_list(bpy.types.UIList):
    def draw_item(self, context, row, data, item, icon, active_data, active_propname, index):
        row.prop(item, 'bone', text='', icon_value=0, emboss=False)
        row = row.row()
        row.alignment = 'RIGHT'
        row.prop(item, 'count', text='', icon_value=0, emboss=False)

class CST_UL_display_pick_twist_list(bpy.types.UIList):
    def draw_item(self, context, row, data, item, icon, active_data, active_propname, index):
        row.prop(item, 'bones', text='', icon_value=0, emboss=False)
        row = row.row()
        row.alignment = 'RIGHT'
        row.label(text=str(len(item.bones.split(', '))))
        row.separator(factor=1.0)

class Bone_Group(bpy.types.PropertyGroup):
    bone: bpy.props.StringProperty(name='Bone', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
class Twist_Group_Create(bpy.types.PropertyGroup):
    bone: bpy.props.StringProperty(name='Bone', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)
    count: bpy.props.IntProperty(name='Count', description='', options={'HIDDEN'}, default=2, subtype='NONE', min=2, max=10)
class Twist_Group_Pick(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', description='Name of Twist Bone', options={'HIDDEN'}, default='Bone_Twist', subtype='NONE', maxlen=0)
    bones: bpy.props.StringProperty(name='Bones', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)


class CST_OT_add_bones_to_col(bpy.types.Operator):
    bl_idname = "cst.add_bones_to_col"
    bl_label = "Add Selected Bones"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    type: bpy.props.StringProperty(name='Type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    def execute(self, context):
        tool = context.scene.cst_tweak_twist
        bones = rig.get_selected_bones()
        if self.type == 'TWIST_CREATE':
            collection = tool.twist_create_col
            active_idx = tool.twist_create_col_index
            for b in bones:
                item = collection.add()
                item.bone = b.name
            tool.twist_create_col_index = collection.values().index(item)
        elif self.type == 'TWIST_PICK':
            collection = tool.twist_pick_col
            active_idx = tool.twist_pick_col_index
            bone_chain = rig.continuous_bone_chain(bones)
            if not isinstance(bone_chain, list):
                error_message = 'In bone chain'
                if isinstance(bone_chain, str):
                    error_message = bone_chain
                self.report({'ERROR'}, message=f'Error : {error_message}')
            else:
                item = collection.add()
                name_list = [b.name for b in bones]
                joined_name = ', '.join(name_list)
                data = rig.extract_name(name_list)
                if data is not None:
                    (common_name, _, endfix) = data
                    item.name = common_name + endfix
                item.bones = joined_name
                tool.twist_pick_col_index = collection.values().index(item)
        elif self.type == 'TWEAK':
            collection = tool.tweak_col
            active_idx = tool.tweak_col_index
            for b in bones:
                item = collection.add()
                item.bone = b.name
            tool.tweak_col_index = collection.values().index(item)
        elif self.type == 'EXCLUDE':
            collection = tool.exclude_col
            active_idx = tool.exclude_col_index
            for b in bones:
                item = collection.add()
                item.bone = b.name
            tool.exclude_col_index = collection.values().index(item)
        return {"FINISHED"}

class CST_OT_remove_bones_from_col(bpy.types.Operator):
    bl_idname = "cst.remove_bones_from_col"
    bl_label = "Remove Collection Item"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    type: bpy.props.StringProperty(name='Type', description='', options={'HIDDEN'}, default='', subtype='NONE', maxlen=0)

    def execute(self, context):
        tool = context.scene.cst_tweak_twist
        bones = rig.get_selected_bones()
        if self.type == 'TWIST_CREATE':
            collection = tool.twist_create_col
            active_idx = tool.twist_create_col_index
            collection.remove(active_idx)
            if collection and len(collection) <= active_idx:
                tool.twist_create_col_index = len(collection) -1
        elif self.type == 'TWIST_PICK':
            collection = tool.twist_pick_col
            active_idx = tool.twist_pick_col_index
            collection.remove(active_idx)
            if collection and len(collection) <= active_idx:
                tool.twist_pick_col_index = len(collection) -1
        elif self.type == 'TWEAK':
            collection = tool.tweak_col
            active_idx = tool.tweak_col_index
            collection.remove(active_idx)
            if collection and len(collection) <= active_idx:
                tool.tweak_col_index = len(collection) -1
        elif self.type == 'EXCLUDE':
            collection = tool.exclude_col
            active_idx = tool.exclude_col_index
            collection.remove(active_idx)
            if collection and len(collection) <= active_idx:
                tool.exclude_col_index = len(collection) -1
        return {"FINISHED"}


class Tool_Group(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(name='Type', description='', options={'HIDDEN'}, items=[
        ('BOTH', 'Both Twist And Tweak', '', 0, 0),
        ('TWIST', 'Only Twist', '', 0, 1),
        ('TWEAK', 'Only Tweak', '', 0, 2),
    ])
    twist_type: bpy.props.EnumProperty(name='Twist Type', description='', options={'HIDDEN'}, items=[
        ('CREATE', 'Create', '', 0, 0),
        ('PICK', 'Pick', '', 0, 1),
    ])
    twist_create_col: bpy.props.CollectionProperty(name='Twist Create Collection', description='', options={'HIDDEN'}, type=Twist_Group_Create)
    twist_create_col_index: bpy.props.IntProperty(name='Twist Create Collection Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    twist_pick_col: bpy.props.CollectionProperty(name='Twist Pick Collection', description='', options={'HIDDEN'}, type=Twist_Group_Pick)
    twist_pick_col_index: bpy.props.IntProperty(name='Twist Pick Collection Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    tweak_direction: bpy.props.EnumProperty(name='Tweak Bones Direction', description='', default='Local Y', options={'HIDDEN'}, items=ui.get_enum_items(rig.direction_list))
    tweak_col: bpy.props.CollectionProperty(name='Tweak Collection', description='', options={'HIDDEN'}, type=Bone_Group)
    tweak_col_index: bpy.props.IntProperty(name='Tweak Collection Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')

    tweak_prefix: bpy.props.StringProperty(name='Tweak Bones Prefix', description='use @ to separate prefix and suffix', options={'HIDDEN'}, default='@_Tweak', subtype='NONE', maxlen=0)
    tweak_parent_prefix: bpy.props.StringProperty(name='Tweak Parent Prefix', description='use @ to separate prefix and suffix', options={'HIDDEN'}, default='PRNT_@_Tweak', subtype='NONE', maxlen=0)
    leaf_prefix: bpy.props.StringProperty(name='Leaf Bones Prefix', description='use @ to separate prefix and suffix', options={'HIDDEN'}, default='@_Leaf', subtype='NONE', maxlen=0)

    deform_prefix: bpy.props.StringProperty(name='Deform Bones Prefix', description='use @ to separate prefix and suffix', options={'HIDDEN'}, default='DEF_@', subtype='NONE', maxlen=0)
    target_prefix: bpy.props.StringProperty(name='Target Bones Prefix', description='', options={'HIDDEN'}, default='ORG_@', subtype='NONE', maxlen=0)

    exclude_bones: bpy.props.BoolProperty(name='Exclude Bones from Operation', description='', options={'HIDDEN'}, default=False)
    exclude_col: bpy.props.CollectionProperty(name='Exclude Collection', description='', options={'HIDDEN'}, type=Bone_Group)
    exclude_col_index: bpy.props.IntProperty(name='Exclude Collection Index', description='', options={'HIDDEN'}, default=0, subtype='NONE')


def draw(layout, tool, context):
    row = layout.row()
    row.alignment = 'RIGHT'
    op = row.operator('cst.reset_properties', text='Reset', icon_value=0, emboss=True, depress=False)
    op.data = 'bpy.context.scene.cst_tweak_twist'
    layout.separator(factor=0.5)
    row = layout.row()
    row.scale_y = 1.2
    row.prop(tool, 'type', text='', icon_value=0, emboss=True)

    if tool.type == 'TWIST' or tool.type == 'BOTH':
        layout.separator(factor=0.5)
        layout.label(text='Twist Settings:', icon_value=0)
        box = layout.box().column()
        row = box.row()
        row.use_property_split = False
        row.prop(tool, 'twist_type', text='Type', icon_value=0, emboss=True, expand=True)
        if tool.twist_type == 'CREATE':
            box.label(text='Create Twist Groups:', icon_value=0)
            row = box.row(heading='', align=True)
            coll_id = ui.display_collection_id('381C1', locals())
            row.template_list('CST_UL_display_create_twist_list', coll_id, tool, 'twist_create_col', tool, 'twist_create_col_index', rows=0)
            row.separator(factor=1.0)
            col = row.column(align=True)
            op = col.operator('cst.add_bones_to_col', text='', icon_value=256, emboss=True, depress=False)
            op.type = 'TWIST_CREATE'
            op = col.operator('cst.remove_bones_from_col', text='', icon_value=21, emboss=True, depress=False)
            op.type = 'TWIST_CREATE'
        elif tool.twist_type == 'PICK':
            box.label(text='Pick Twist Groups:', icon_value=0)
            row = box.row(heading='', align=True)
            coll_id = ui.display_collection_id('302D1', locals())
            row.template_list('CST_UL_display_pick_twist_list', coll_id, tool, 'twist_pick_col', tool, 'twist_pick_col_index', rows=0)
            row.separator(factor=1.0)
            col = row.column(align=True)
            op = col.operator('cst.add_bones_to_col', text='', icon_value=256, emboss=True, depress=False)
            op.type = 'TWIST_PICK'
            op = col.operator('cst.remove_bones_from_col', text='', icon_value=21, emboss=True, depress=False)
            op.type = 'TWIST_PICK'
            if tool.twist_pick_col:
                twist_group = tool.twist_pick_col[tool.twist_pick_col_index]
                box.prop(twist_group, 'name', text='Twist Name', icon_value=0, emboss=True)


    if tool.type == 'TWEAK' or tool.type == 'BOTH':
        layout.separator(factor=1.0)
        layout.label(text='Tweak Settings:', icon_value=0)
        box = layout.box().column()
        box.prop(tool, 'tweak_direction', text='Tweak Rotation', icon_value=0, emboss=True)
        box.prop(tool, 'tweak_prefix', text='Tweak Prefix', icon_value=0, emboss=True)
        box.prop(tool, 'tweak_parent_prefix', text='Parent Prefix', icon_value=0, emboss=True)
        box.prop(tool, 'leaf_prefix', text='Leaf Prefix', icon_value=0, emboss=True)
        layout.separator(factor=0.5)
        box.label(text='Head Diabled Tweak Bones:', icon_value=0)
        row = box.row(align=True)
        coll_id = ui.display_collection_id('77236', locals())
        row.template_list('CST_UL_display_bone_list', coll_id, tool, 'tweak_col', tool, 'tweak_col_index', rows=0)
        row.separator(factor=1.0)
        col = row.column(align=True)
        op = col.operator('cst.add_bones_to_col', text='', icon_value=256, emboss=True, depress=False)
        op.type = 'TWEAK'
        op = col.operator('cst.remove_bones_from_col', text='', icon_value=21, emboss=True, depress=False)
        op.type = 'TWEAK'

    layout.separator(factor=0.5)
    col = layout.column()
    col.prop(tool, 'deform_prefix', text='Deform Prefix', icon_value=0, emboss=True)
    col.prop(tool, 'target_prefix', text='Target Prefix', icon_value=0, emboss=True)
    col.prop(tool, 'exclude_bones', text='exclude bones', icon_value=0, emboss=True)
    if tool.exclude_bones:
        col.label(text='Exlude Bones:', icon_value=0)
        row = col.row(align=True)
        coll_id = ui.display_collection_id('782GB', locals())
        row.template_list('CST_UL_display_bone_list', coll_id, tool, 'exclude_col', tool, 'exclude_col_index', rows=0)
        row.separator(factor=1.0)
        col = row.column(align=True)
        op = col.operator('cst.add_bones_to_col', text='', icon_value=256, emboss=True, depress=False)
        op.type = 'EXCLUDE'
        op = col.operator('cst.remove_bones_from_col', text='', icon_value=21, emboss=True, depress=False)
        op.type = 'EXCLUDE'

    layout.separator(factor=1)
    col = layout.column()
    col.scale_y = 1.4
    op = col.operator('cst.create_twist_and_tweak', text='RUN TOOL', icon_value=0, emboss=True, depress=True)



classes = [
    CST_OT_add_bones_to_col,
    CST_OT_remove_bones_from_col,
    CST_UL_display_create_twist_list,
    CST_UL_display_pick_twist_list,
    CST_UL_display_bone_list,
    Twist_Group_Create,
    Twist_Group_Pick,
    Bone_Group,
    Tool_Group,
]

def register():
    ui.register_all(classes)

def unregister():
    ui.unregister_all(classes)


