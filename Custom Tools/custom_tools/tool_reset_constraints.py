import bpy
from common import ui, rig


def draw(self, locals):
    cst = bpy.context.scene.cst
    layout = locals['box_main']
    if cst.is_main_open:
        op = layout.operator('cst.reset_constraints', text='Reset Constraints', icon_value=0, emboss=True, depress=False)

class CST_OT_reset_constraints(bpy.types.Operator):
    bl_idname = "cst.reset_constraints"
    bl_label = "Reset Constraints"
    bl_description = """Fixing issues caused by constraints after applying armature scale
    1. clear transformations
    2. set all constraints influence to 0.0
    3. apply pose-as-rest-pose
    4. load constraint influence respectively
    """
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "ARMATURE"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.transforms_clear()

        all_constraints = []
        for bone in context.object.pose.bones: all_constraints += bone.constraints.values()

        cnst_inf_list = [(cnst, cnst.influence) for cnst in all_constraints]

        for (cnst, inf) in cnst_inf_list: cnst.influence = 0.0
        bpy.ops.pose.armature_apply(selected=False)
        for (cnst, inf) in cnst_inf_list: cnst.influence = inf

        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)

classes = [
    CST_OT_reset_constraints,
]

def register():
    ui.register_all(classes)

def unregister():
    ui.unregister_all(classes)


if __name__ == "__main__":
    register()