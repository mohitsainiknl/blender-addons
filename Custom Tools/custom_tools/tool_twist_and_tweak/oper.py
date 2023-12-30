import bpy
from bpy.types import EditBone
from mathutils import Matrix, Vector

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import ui, rig

class TW_Group():
    __target_name = ''
    __deform_name = ''
    __tweak_parent_name = ''
    __tweak_name = ''
    __leaf_name = ''
    target = None
    deform = None
    tweak = None
    tweak_parent = None
    leaf = None
    twist_influence = 0
    twist_position = 0

    def __str__(self):
        target = ((self.target if isinstance(self.target, str) or isinstance(self.target, list) else self.target.name) if self.target is not None else 'NONE')
        deform = ((self.deform if isinstance(self.deform, str) or isinstance(self.deform, list) else self.deform.name) if self.deform is not None else 'NONE')
        tweak_parent = ((self.tweak_parent if isinstance(self.tweak_parent, str) or isinstance(self.tweak_parent, list) else self.tweak_parent.name) if self.tweak_parent is not None else 'NONE')
        tweak = ((self.tweak if isinstance(self.tweak, str) or isinstance(self.tweak, list) else self.tweak.name) if self.tweak is not None else 'NONE')
        return f'(target {target.ljust(11)},deform {(deform.ljust(11) if isinstance(deform, str) else deform)},tweak_parent {tweak_parent.ljust(11)},tweak {tweak.ljust(11)},twist_influence {str(self.twist_influence).ljust(7)},twist_position {str(self.twist_position).ljust(2)})'

    def load_names(self):
        if self.target is not None:
            self.__target_name = self.target.name
        if self.deform is not None:
            self.__deform_name = self.deform.name
        if self.tweak is not None:
            self.__tweak_name = self.tweak.name
        if self.tweak_parent is not None:
            self.__tweak_parent_name = self.tweak_parent.name
        if self.leaf is not None:
            self.__leaf_name = self.leaf.name

    def load_mode_bones(self):
        bones = rig.get_mode_bones()
        if self.__target_name:
            self.target = bones[self.__target_name]
        if self.__deform_name:
            self.deform = bones[self.__deform_name]
        if self.__tweak_parent_name:
            self.tweak_parent = bones[self.__tweak_parent_name]
        if self.__tweak_name:
            self.tweak = bones[self.__tweak_name]
        if self.__leaf_name:
            self.leaf = bones[self.__leaf_name]

def load_names(tw_group_list):
    for g in tw_group_list:
        g.load_names()

def load_mode_bones(tw_group_list):
    for g in tw_group_list:
        g.load_mode_bones()

def __subdivide_matrix_data(bone, count, position):
    pos = count - position + 1
    avg = bone.length / count
    head_matrix = bone.matrix @ Matrix.Translation((0, (avg * (pos-1)), 0))
    tail_matrix = bone.matrix @ Matrix.Translation((0, (avg * (pos)), 0))
    return (head_matrix, tail_matrix)


def run(self, tool, context):
    bpy.ops.object.mode_set(mode='EDIT')

    all_bones = context.object.data.edit_bones
    excludes = []
    if tool.exclude_bones:
        excludes = [i.bone for i in tool.exclude_col]
    bones = [b for b in all_bones if b.name not in excludes]
    edit_bones = context.object.data.edit_bones

    twist_group_list = []
    for bone in bones:
        g = TW_Group()
        g.deform = bone
        twist_group_list.append(g)


    if tool.type == 'TWIST' or tool.type == 'BOTH':

        # Shifting and Adding Twist_Bones
        if tool.twist_type == 'CREATE':
            twist_targets = [i.bone for i in tool.twist_create_col]
            twist_counts = [i.count for i in tool.twist_create_col]
            new_twist_group_list = []

            for g in reversed(twist_group_list):
                if g.deform.name in twist_targets:
                    twist_count = twist_counts[twist_targets.index(g.deform.name)]
                    name_list = rig.create_name([g.deform.name]*twist_count, '@')
                    for idx, name in reversed(list(enumerate(list(reversed(name_list))))):
                        ng = TW_Group()
                        ng.target = g.deform    # shifing bone
                        ng.target.use_deform = False
                        ng.deform = edit_bones.new(name)
                        ng.deform.use_deform = True
                        # if idx == 0: ng.deform.use_connect = g.deform.use_connect
                        # else: ng.deform.use_connect = True
                        pos = idx + 1
                        ng.twist_influence = round((1 - pos / twist_count), 4)
                        ng.twist_position = pos
                        new_twist_group_list.append(ng)

                        # Calculating Matrix
                        (head_matrix, tail_matrix) = __subdivide_matrix_data(ng.target, twist_count, pos)
                        ng.deform.matrix = head_matrix
                        ng.deform.tail = tail_matrix.translation
                    twist_group_list.remove(g)
            twist_group_list += new_twist_group_list
        elif tool.twist_type == 'PICK':
            bone_chain_list = []

            # Creating Picked Bone_Chain_List
            for item in tool.twist_pick_col:
                bone_name_list = [i.strip() for i in item.bones.split(',')] # bone.name with NOT strip() get error
                bone_chain = rig.continuous_bone_chain(bone_name_list)
                if not isinstance(bone_chain, list):
                    error_message = 'In bone chain'
                    if isinstance(bone_chain, str):
                        error_message = bone_chain
                    self.report({'ERROR'}, message=f'Error : {error_message}')
                    return None
                bone_chain_list.append((item.name, [b.name for b in bone_chain]))

            # Calculating Twist_Target and Twist_Data with the help of Bone_Chain_List
            for g in twist_group_list:
                for (twist_name, bone_chain) in bone_chain_list:
                    if g.deform.name in bone_chain:
                        # Calculating Twist Data
                        pos = bone_chain.index(g.deform.name) + 1
                        twist_count = len(bone_chain)
                        g.twist_influence = round((1 - pos / twist_count), 4)
                        g.twist_position = pos

                        # Adding Target_Twist_Bone
                        target_list = [tg.target for tg in twist_group_list if isinstance(tg.target, EditBone)]
                        name_list = [t.name for t in target_list]
                        if twist_name not in name_list:
                            g.target = edit_bones.new(twist_name)
                            g.target.use_deform = False
                        else:
                            g.target = target_list[name_list.index(twist_name)]

                        # Calculating Matrix
                        if pos == 1:
                            g.target.tail = g.deform.tail
                        elif pos == twist_count:
                            g.target.matrix = g.deform.matrix


    # Creating Remaining Target_Bones For Both_Twist_And_Tweak
    for g in twist_group_list:

        # Creating Targets for Other_Bones
        if isinstance(g.deform, EditBone) and g.target is None:
            g.target = edit_bones.new(g.deform.name)
            g.target.use_deform = False

            # Calculating Matrix
            g.target.length = g.deform.length
            g.target.matrix = g.deform.matrix

    tgt_name_list = [g.target.name for g in twist_group_list]
    def_name_list = [g.deform.name for g in twist_group_list]

    # Fixing Deform_Parenting (disturbed by shifing and creating new bones)
    for g in twist_group_list:
        if g.deform.parent is None or g.deform.parent.name in tgt_name_list:

            # Twist_Head Bone Parenting
            if g.twist_influence == 0 and g.twist_position > 0:
                for g2 in twist_group_list:
                    if g2.deform is not None and g.target.parent.name == g2.deform.name:
                        g.deform.parent = g.target.parent
                        break
                    elif g2.target is not None and g.target.parent.name == g2.target.name and g2.twist_position <= 1:
                        g.deform.parent = g2.deform
                        break
                g.deform.use_connect = g.target.use_connect

            # Twist_Tail Bone Parenting
            elif g.deform.parent is not None and g.deform.parent.name in tgt_name_list:
                target = g.deform.parent.name
                pos = 1
                for cg in twist_group_list:
                    if cg.target.name == target and cg.twist_position == pos:
                        g.deform.parent = cg.deform
                        print(g.deform.name, '<--1')
                        g.deform.use_connect = True
                        break

            # Twist_Other Bone Parenting
            elif g.twist_position > 0:
                target = g.target.name
                pos = g.twist_position + 1
                for cg in twist_group_list:
                    if cg.target.name == target and cg.twist_position == pos:
                        g.deform.parent = cg.deform
                        print(g.deform.name, '<--2')
                        g.deform.use_connect = True
                        break

    # Need to calculate before renaming
    tweak_exclude_list = [g.bone for g in tool.tweak_col]
    print(tweak_exclude_list)
    tweak_group_list = [g for g in twist_group_list if g.deform.name not in tweak_exclude_list and g.target.name not in tweak_exclude_list]
    for g in tweak_group_list: print(g)


    # Fixing Parenting in Target_Bones
    for g in twist_group_list:
        if g.twist_influence == 0 and g.deform.parent is not None and g.deform.parent.name in def_name_list:
            def_parent_idx = def_name_list.index(g.deform.parent.name)
            g.target.parent = twist_group_list[def_parent_idx].target
            g.target.use_connect = g.deform.use_connect

    # Renaming Target_Bones With Target_Prefix
    target_list = [tg.target for tg in twist_group_list]
    name_list = rig.create_name([t.name for t in target_list], tool.target_prefix)
    for idx, target in enumerate(target_list):
        target.name = name_list[idx]

    # Renaming Deform_Bones With Deform_Prefix
    deform_list = [dg.deform for dg in twist_group_list]
    name_list = rig.create_name([d.name for d in deform_list], tool.deform_prefix)
    for idx, deform in enumerate(deform_list):
        deform.name = name_list[idx]

    tgt_name_list = [g.target.name for g in tweak_group_list]
    def_name_list = [g.deform.name for g in tweak_group_list]

    def child_type(g):
        """
            End_bones of group_list and disconnected_child in group_list

            Return 0: Child Not Found
            Return 1: Child Found
            Return 2: Child Found with Use_Connect
        """
        is_found = False
        print(def_name_list)
        for child in g.deform.children:
            if child.name in def_name_list:
                is_found = True
                break
        has_connect_child = False
        if context.mode == 'EDIT_ARMATURE':
            bones = context.object.data.edit_bones
        else:
            bones = context.object.data.bones
        for child in g.deform.children:
            if child.name in def_name_list and bones[child.name].use_connect:
                has_connect_child = True
                break
        return (0 if not is_found else (1 if not has_connect_child else 2))

    if tool.type == 'TWEAK' or tool.type == 'BOTH':
        avg_size = sum([g.deform.length for g in tweak_group_list]) / len(tweak_group_list)

        for g in tweak_group_list:
            g.tweak = edit_bones.new(g.deform.name)
            g.tweak.use_deform = False
            g.tweak.length = avg_size * 0.16
            g.tweak.matrix = g.deform.matrix

            g.tweak_parent = edit_bones.new(g.deform.name)
            g.tweak_parent.use_deform = False
            g.tweak_parent.length = avg_size * 0.092
            g.tweak_parent.matrix = g.tweak.matrix

            if child_type(g) != 2:

                # Creating Leaf_Bones
                g.leaf = edit_bones.new(g.deform.name)
                g.leaf.use_deform = False
                g.leaf.length = avg_size * 0.16
                matrix = rig.direction_matrix(g.tweak.matrix, 'Local -Y')    # <---- Leaf Direction
                g.leaf.matrix = matrix @ Matrix.Translation((0, -1 * g.deform.length, 0))

                # Leaf Parenting
                g.leaf.parent = g.target

        # Parenting Tweak_Bones And Tweak_Parent_Bones
        for g in tweak_group_list:
            g.tweak.use_connect = False
            g.tweak.parent = g.tweak_parent
            g.tweak_parent.use_connect = False
            g.tweak_parent.parent = g.target # <--- with target_bone

        # Renaming Tweak_Bones
        tweak_list = [g.tweak for g in tweak_group_list if g.tweak is not None]
        name_list = rig.create_name([t.name for t in tweak_list], tool.tweak_prefix)
        for idx, tweak in enumerate(tweak_list):
            tweak.name = name_list[idx]

        # Renaming Tweak_Parent_Bones
        tweak_parent_list = [g.tweak_parent for g in tweak_group_list if g.tweak_parent is not None]
        name_list = rig.create_name([t.name for t in tweak_parent_list], tool.tweak_parent_prefix)
        for idx, tweak_parent in enumerate(tweak_parent_list):
            tweak_parent.name = name_list[idx]

        # Renaming Leaf_Bones
        leaf_list = [g.leaf for g in tweak_group_list if g.leaf is not None]
        name_list = rig.create_name([l.name for l in leaf_list], tool.leaf_prefix)
        for idx, leaf in enumerate(leaf_list):
            leaf.name = name_list[idx]
    
    # Merge Same_Head_Tweak_Bones
    tweak_head_list =  [g.tweak.head for g in tweak_group_list]
    remove_list = []
    for idx, g in enumerate(tweak_group_list):
        if g.tweak.head in tweak_head_list and tweak_head_list.index(g.tweak.head) != idx:
            g2 = tweak_group_list[tweak_head_list.index(g.tweak.head)]
            eg = None
            yg = None

            parent_list  = rig.get_parent_list(g.deform)
            if g2.deform in parent_list:
                eg = g2
                yg = g
            else:
                parent_list  = rig.get_parent_list(g2.deform)
                if g.deform in parent_list:
                    eg = g
                    yg = g2

            if eg is not None and yg is not None:
                remove_list.append(yg.tweak)
                remove_list.append(yg.tweak_parent)
                yg.tweak = eg.tweak
                yg.tweak_parent = eg.tweak_parent
    for b in reversed(remove_list):
        edit_bones.remove(b)


    # Fixing Bone Freeze in Pose_Mode
    for b in all_bones:
        if b.parent is None:
            b.use_connect = False

    load_names(twist_group_list)
    bpy.ops.object.mode_set(mode='POSE')
    load_mode_bones(twist_group_list)


    if tool.type == 'TWIST':
        for g in twist_group_list:
            cnst = g.deform.constraints.new('COPY_TRANSFORMS')
            cnst.name = f'Copy ORG Transforms'
            cnst.target = context.object
            cnst.subtarget = g.target.name

            if g.twist_position > 0 and g.twist_influence > 0 and len(g.target.children) == 1:
                cnst = g.deform.constraints.new('COPY_ROTATION')
                cnst.name = f'Copy Twist Rotation'
                cnst.target = context.object
                cnst.subtarget = g.target.children[0].name
                cnst.use_x = False
                cnst.use_y = True
                cnst.use_z = False
                cnst.target_space = 'LOCAL'
                cnst.owner_space = 'LOCAL'
                cnst.influence = g.twist_influence

    if tool.type == 'BOTH':

        def get_group(deform_name):
            for g in twist_group_list:
                if g.deform.name == deform_name:
                    return g

        def get_twist_group(target_bone_name, pos):
            for g in twist_group_list:
                if g.target.name == target_bone_name:
                    if pos > 0 and g.twist_position == pos: return g
                    if pos == -1 and g.twist_position > 0 and g.twist_influence == 0: return g
                if pos == 0 and g.target.parent is not None and g.target.parent.name == target_bone_name:
                    return g


        for g in twist_group_list:
            if g not in tweak_group_list:

                # Deform_Bone COPY_TRANSFORMS Constraints
                cnst = g.deform.constraints.new('COPY_TRANSFORMS')
                cnst.name = f'Copy Target Transforms'
                cnst.target = context.object
                cnst.subtarget = g.target.name

            elif g.tweak is not None:

                # Deform_Bone COPY_TRANSFORMS Constraints
                cnst = g.deform.constraints.new('COPY_TRANSFORMS')
                cnst.name = f'Copy Tweak Transforms'
                cnst.target = context.object
                cnst.subtarget = g.tweak.name

                # Deform_Bone STRETCH_TO Constraints
                if child_type(g) != 2:
                    next_tweak = g.leaf
                else:
                    bones = context.object.data.bones
                    is_found = False
                    for child in g.deform.children:
                        if child.name in def_name_list and bones[child.name].use_connect:
                            is_found = True
                            break
                    if not is_found:
                        print('Error : next_tweak not found')
                        print('def_name_list : ', def_name_list)
                        print('g : ', g)
                        print('children : ', [b.name for b in g.deform.children])
                        print('')
                        return
                    ng = get_group(child.name)
                    next_tweak = ng.tweak
                cnst = g.deform.constraints.new('STRETCH_TO')
                cnst.name = f'Stretch To Next Tweak'
                cnst.target = context.object
                cnst.subtarget = next_tweak.name

                # Twist_Tweak_Parnet Constraints
                if g.twist_influence > 0:

                    # Twist_Head COPY_TRANSFORMS Constrants
                    g2 = get_twist_group(g.target.name, -1)  # twist_head twist_bone_group
                    cnst = g.tweak_parent.constraints.new('COPY_TRANSFORMS')
                    cnst.name = f'Copy Twist Head Transforms'
                    cnst.target = context.object
                    cnst.subtarget = g2.tweak.name

                    # Twist_Tail_Name Calculation
                    g2 = get_twist_group(g.target.name, 0)  # twist_tail twist_bone_group
                    if g2 is not None:
                        tweak_name = g2.tweak.name
                    else:
                        g2 = get_twist_group(g.target.name, 1)  # twist_pos_1 twist_bone_group
                        tweak_name = g2.leaf.name

                    # Twist_Tail  COPY_TRANSFORMS Constraint
                    cnst = g.tweak_parent.constraints.new('COPY_TRANSFORMS')
                    cnst.name = f'Copy Twist Tail Transforms'
                    cnst.target = context.object
                    cnst.subtarget = tweak_name
                    cnst.influence = g.twist_influence

                    # Twist_Tail  DAMPED_TRACK Constraint
                    cnst = g.tweak_parent.constraints.new('DAMPED_TRACK')
                    cnst.name = f'Damped Track Twist Tail'
                    cnst.target = context.object
                    cnst.subtarget = tweak_name

                else:
                    #### This require Root_Bones ####

                    # # Tweak_Parent COPY_SCALE Constraint
                    # cnst = g.tweak_parent.constraints.new('COPY_SCALE')
                    # cnst.name = f'Copy Root Scale'
                    # cnst.target = context.object
                    # cnst.subtarget = root_bone
                    pass


    print('---GROUP---')
    for g in twist_group_list: print(g)

