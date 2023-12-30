import bpy

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import interface, oper

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import ui


bl_info = {
    "name": "CST Twist and Tweak",
    "description": "Tool for creating twist and tweak bones for selected armature",
    "author": "MohitX",
    "version": (0, 0, 1),
    "blender": (2, 9, 0),
    "location": "View3D",
    "category": "Tool",
    "doc_url": "",
}

class CST_PT_twist_and_tweak(bpy.types.Panel):
    bl_label = 'Twist and Tweak'
    bl_idname = 'CST_PT_twist_and_tweak'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Tool'
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = ('CST_PT_main_custom_tools' if __name__ != '__main__' else '')
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return True
    
    # def draw_header(self, context):
    #     row = self.layout.row()
    #     row.alignment = 'RIGHT'
    #     op = row.operator('sn.dummy_button_operator', text='Reset', icon_value=0, emboss=True, depress=False)


    def draw(self, context):
        layout = self.layout.column(align=True)
        layout.use_property_split = True
        layout.use_property_decorate = False
        tool = context.scene.cst_tweak_twist
        interface.draw(layout, tool, context)

class CST_OT_create_twist_and_tweak(bpy.types.Operator):
    bl_idname = "cst.create_twist_and_tweak"
    bl_label = "Create Twist and Tweak"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def execute(self, context):
        tool = context.scene.cst_tweak_twist
        oper.run(self, tool, context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

classes = [
    CST_OT_create_twist_and_tweak,
    CST_PT_twist_and_tweak,
]

def register():
    interface.register()
    bpy.types.Scene.cst_tweak_twist = bpy.props.PointerProperty(name='Twist And Tweak', description='', type=interface.Tool_Group)
    ui.register_all(classes)

def unregister():
    ui.unregister_all(classes)
    del bpy.types.Scene.cst_tweak_twist
    interface.unregister()


if __name__ == "__main__":
    try: bpy.context.scene.mx.addon_unregister.append(unregister)
    except: pass
    register()

