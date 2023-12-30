import bpy
from common import ui, rig


def draw(self, locals):
    cst = bpy.context.scene.cst
    layout = locals['box_main']
    if cst.is_main_open:
        # layout = layout.row(align=True)
        op = layout.operator('cst.parent_bones', text='Parent Bones', icon_value=0, emboss=True, depress=False)
        # op = layout.operator('cst.popup_parent_bones', text='', icon_value=46, emboss=True, depress=False)

# def draw_popup(self, layout):
#     layout.use_property_split = True
#     layout.use_property_decorate = False

#     layout.prop(bpy.context.scene, 'cst_pb_distance', text='Connect Distance', icon_value=0, emboss=True)
#     layout = layout.row(align=True)
#     layout.prop(bpy.context.scene, 'cst_pb_parent_to_nearest', text='Parent to Nearest', icon_value=0, emboss=True, expand=True)

class CST_OT_parent_bones(bpy.types.Operator):
    bl_idname = "cst.parent_bones"
    bl_label = "Parent Bones"
    bl_description = """Parent Selected Bones to their Nearest Bone"""
    bl_options = {"REGISTER", "UNDO"}

    distance: bpy.props.FloatProperty(name='Connect Distance', description='minimum distance for use_connect option', default=0.01, subtype='DISTANCE', unit='LENGTH', step=3, precision=6)
    parent_to_nearest: bpy.props.EnumProperty(name='Parent to Nearest', default='None', description='for Disconnect Bones Only', items=[('Head', 'Head', '', 0, 0), ('Tail', 'Tail', '', 0, 1), ('None', 'None', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def execute(self, context):
        min_connect_distance = self.distance
        parent_to = self.parent_to_nearest
        
        prev_mode = context.mode
        bpy.ops.object.mode_set(mode='EDIT')
        selected_bones = [b for b in bpy.context.selected_editable_bones if b.parent is None]
        all_bones = bpy.context.object.data.edit_bones.values()

        if selected_bones:
            def get_distance(from_bone, to_bone, check_prop=False):
                from_point = from_bone.head
                to_point = (to_bone.head if check_prop and parent_to == 'Head' else to_bone.tail)
                return abs((from_point - to_point).length)

            # Parenting Bones with Joints
            for bone in selected_bones:
                all_bones_copy = [b for b in all_bones if b.name != bone.name]
                is_done = False
                for bone2 in all_bones_copy:
                    distance = get_distance(bone, bone2)
                    if bone.name != bone2.name and distance <= min_connect_distance:
                        bone.use_connect = True
                        bone.parent = bone2
                        is_done = True
                        break
                if parent_to != 'None' and not is_done:
                    all_bones_copy_2 = all_bones_copy.copy()

                    nearest_bone = all_bones_copy_2.pop(0)
                    nearest_bone_distance = get_distance(bone, nearest_bone, True)

                    for bone2 in all_bones_copy_2:
                        distance = get_distance(bone, bone2, True)
                        if distance < nearest_bone_distance:
                            nearest_bone = bone2
                            nearest_bone_distance = distance
                    bone.use_connect = False
                    bone.parent = nearest_bone
            # self.report({'INFO'}, message='Parenting Done Successfully')
        else:
            self.report({'ERROR'}, message='No Bone Selected')

        bpy.ops.object.mode_set(mode=('EDIT' if prev_mode == 'EDIT_ARMATURE' else prev_mode))

        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

# import types
# class CST_OT_popup_parent_bones(bpy.types.Operator):
#     bl_idname = "cst.popup_parent_bones"
#     bl_label = "Parenting Options"
#     bl_options = {'REGISTER'}

#     def draw(self, context):
#         layout = self.layout.column()
#         layout.label(text='Parenting Options:')
#         draw_popup(self, layout)

#     def invoke(self, context, event):
#         wm = context.window_manager
#         wm.invoke_popup(self)
#         return {'RUNNING_MODAL'}
    
#     def execute(self, context):
#         return {'FINISHED'}

classes = [
    # CST_OT_popup_parent_bones,
    CST_OT_parent_bones,
]

def register():
    ui.register_all(classes)
    # bpy.types.Scene.cst_pb_distance = bpy.props.FloatProperty(name='Connect Distance', description='minimum distance for use_connect option', default=0.01, subtype='DISTANCE', unit='LENGTH', step=3, precision=6)
    # bpy.types.Scene.cst_pb_parent_to_nearest = bpy.props.EnumProperty(name='Parent to Nearest', default='Tail', description='for Disconnect Bones Only', items=[('Head', 'Head', '', 0, 0), ('Tail', 'Tail', '', 0, 1), ('None', 'None', '', 0, 2)])

def unregister():
    ui.unregister_all(classes)


if __name__ == "__main__":
    register()