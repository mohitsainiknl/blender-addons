import bpy
import math
import mathutils
from math import degrees, radians
from mathutils import Matrix, Vector
import re


direction_list = ([
    'Global X' , 'Global Y' , 'Global Z' ,
    'Global -X', 'Global -Y', 'Global -Z',
    'Local X'  , 'Local Y'  , 'Local Z'  ,
    'Local -X' , 'Local -Y' , 'Local -Z' ,
])

def split_direction(direction):
    """
        Return : (space, invert, axis)
        Space : ('Global'|'Local')
        Invert : (-1|1)
        axis : ('X'|'Y'|'Z')
    """
    ex = "^(Global|Local) (-)?(X|Y|Z)$"
    data = re.search(ex, direction)
    if direction == data.group():
        space = data.group(1)
        invert = (-1 if data.group(2) == '-' else 1)
        axis = data.group(3)
        return (space, invert, axis)


def matrix_replace(matrix, mat_or_vec, type):
    if isinstance(mat_or_vec, Vector):
        mat_or_vec = mat_or_vec.to_matrix().to_4x4()
    mat = mat_or_vec

    loc, rot, scale = matrix.decompose()
    T = mathutils.Matrix.Translation(loc)
    R = rot.to_matrix().to_4x4()
    S = mathutils.Matrix.Diagonal(scale.to_4d())
    if type.upper() == 'LOCATION':
        T = mathutils.Matrix.Translation(mat.to_translation())
    elif type.upper() == 'ROTATION':
        R = mat.to_euler().to_matrix().to_4x4()
    elif type.upper() == 'SCALE':
        S = mathutils.Matrix.Diagonal(mat.to_scale().to_4d())
    else: return None

    return T @ R @ S

def direction_matrix(matrix, direction):
    data = split_direction(direction)
    if data is not None:
        (space, invert, axis) = data
        matrix_space = matrix
        if space == 'Global':
            matrix_space = Matrix.Identity(4)
        invert = (180 if invert == -1 else 0)
        
        if axis == 'Y': return matrix_replace(matrix, matrix_space @ Matrix.Rotation(math.radians(invert + 00.0), 4, 'X'), 'ROTATION')
        if axis == 'X': return matrix_replace(matrix, matrix_space @ Matrix.Rotation(math.radians(invert + (-180) + 90.0), 4, 'Z'), 'ROTATION')
        if axis == 'Z': return matrix_replace(matrix, matrix_space @ Matrix.Rotation(math.radians(invert + 90.0), 4, 'X'), 'ROTATION')



# TODO get_mode_bones()
def get_mode_bones():
    """Return `Pose Bones` and `Edit Bones` according to respective `context.mode`"""
    mode = bpy.context.mode
    if mode == 'EDIT_ARMATURE':
        bones = bpy.context.object.data.edit_bones
    elif mode == 'POSE':
        bones = bpy.context.object.pose.bones
    else:
        bones = bpy.context.object.data.bones
    return bones

def get_parent_list(bone):
    """ Return Bone Parent list (without itself)"""
    if bone.parent is not None:
        return [bone.parent] + get_parent_list(bone.parent)
    else:
        return []


# TODO get_selected_bones()
def get_selected_bones():
    """Return `Pose Bones` and `Edit Bones` according to respective `context.mode`"""
    mode = bpy.context.mode
    if mode == 'EDIT_ARMATURE':
        return bpy.context.selected_editable_bones
    elif mode == 'POSE':
        return bpy.context.selected_pose_bones


# TODO split_prefix()
def split_prefix(name, check_recursive=True):
    """ Capitalized (1-4) characters before '.' or '_', will be treated as `Prefix`.

        Return : (name, prefix)

        Example : mixamo.NDL_2_PRNT_Name.L = ('Name.L', 'mixamo.NDL_2_PRNT_')
    """
    regex = r"^[A-Z]{1,4}(?:\.|_)((?:\d)+(?:\.|_))?"
    match = re.search(regex, name)
    prefix = ''
    if match is not None:
        prefix = match.group()
        name = name[len(prefix):]
    prefix_01 = prefix
    prefix = ''
    prefix_list =  ['MIXAMO']
    for p in prefix_list:
        if name.upper().startswith(p+'_') or name.upper().startswith(p+'.'):
            prefix_len = len(p) + 1
            prefix = name[:prefix_len]
            name = name[prefix_len:]
            break
    prefix = prefix_01 + prefix
    if prefix != '' and check_recursive:
        (name, new_prefix) = split_prefix(name)
        return (name, prefix + new_prefix)
    else:
        return (name, prefix)


# TODO split_numfix()
def split_numfix(name):
    """ Split any digits leading to '.' or '_' Example - .001, _02, etc
        Return : (name, numfix)
    """
    regex = r"(?:\.|_)\d+$"
    match = re.search(regex, name)
    numfix = ''
    if match is not None:
        numfix = match.group()
        name = name[:(len(name) - len(numfix))]
    return (name, numfix)


# TODO split_endfix()
def split_endfix(name):
    """ - endfix_list = ['LEFT', 'RIGHT', 'CENTER', 'MIDDLE', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN', 'TOP', 'BOTTOM']
        - Also split any character after '.' or '_' Example - .R, .X, _L
        Return : (name, endfix, numfix)
    """

    (name, numfix) = split_numfix(name)
    if name[-2] == '.' or name[-2] == '_':
        endfix = name[-2:]
        name = name[:-2]
        return (name, endfix, numfix)
    endfix_list = ['LEFT', 'RIGHT', 'CENTER', 'MIDDLE', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN', 'TOP', 'BOTTOM']
    for endfix in endfix_list:
        if name.upper().endswith('.' + endfix) or name.upper().endswith('_' + endfix):
            endfix_len = len(name) - len(endfix) - 1
            endfix = name[endfix_len:]
            name = name[:endfix_len]
            return (name, endfix, numfix)
    return (name, '', numfix)
# print(split_endfix('name.top.02'))


# TODO split_suffix()
def split_suffix(name, check_recursive=True):
    """ suffix_list = ['_TWEAK', '_TWIST', '_DEFORM', '_TARGET', '_PARENT', '_NEEDLE', '_ORIGINAL', '_CONTROL', '_ROLL', '_CHILD', '_SUPER']
        Return : (name, suffix)
        Question with 'Name_01_Needle.L' and 'Name_Needle_01.L'
    """
    (name, numfix) = split_numfix(name)

    suffix_list = [
        '_TWEAK', '_TWIST', '_DEFORM', '_TARGET', '_PARENT', '_NEEDLE',
        '_ORIGINAL', '_CONTROL', '_ROLL', '_CHILD', '_SUPER'
    ]
    suffix = ''
    for suf in suffix_list:
        if name.upper().endswith(suf):
            suf_len = len(name) - len(suf)
            suffix = name[suf_len:]
            name = name[:suf_len]
            break
    if suffix != '' and check_recursive:
        (name, new_suffix) = split_suffix(name)
        return (name, new_suffix + suffix + numfix)
    else:
        return (name, suffix + numfix)
# print(split_suffix('NDL_2_Name_roll_parent_Needle_03'))

# TODO split_name()
def split_name(name):
    """ Only split `Prefix` and `Endfix`
        Return : (name, prefix, endfix, numfix)
    """
    (name, prefix) = split_prefix(name)
    (name, endfix, numfix) = split_endfix(name)
    return (name, prefix, endfix, numfix)
# print(split_name('NDL_2_Name_Needle_03.L.002'))


def extract_name(name_list):
    """ Extract name, only if diffrenciated by numfix, like - (.001, .002) or (_01, _02)
        Return : (common_name, common_prefix, common_suffix, common_endfix)
    """
    if isinstance(name_list, list) and name_list and isinstance(name_list[0], str):
        name = name_list.pop(0)
        (com_name, com_prefix, com_endfix, _) = split_name(name)
        (com_name, _) = split_numfix(com_name)
        if com_name != name:
            for name in name_list:
                (name, prefix, endfix, _) = split_name(name)
                (name, _) = split_numfix(name)
                if (
                    (name != com_name) or
                    (prefix != com_prefix) or
                    (endfix != com_endfix)
                ):
                    return None
            return (com_name, com_prefix, com_endfix)
        else:
            return None
    return None
# print(extract_name(['DEF_Thigh_Tweak_01.L', 'DEF_Thigh_Tweak_02.L', 'DEF_Thigh_Tweak_03.L']))


def split_pattern(pattern):
    if pattern.find('@') == -1:
        prefix = pattern
        suffix = ''
    else:
        pat = pattern.split('@')
        prefix = pat[0]
        suffix = pat[1]
    return (prefix, suffix)


def create_name(name, pattern):
    """ add numfix(like-`_02`) on prefix else suffix
        name : can be `name` or `name_list`
        Return : created_name or created_name_list
    """
    # print(name, pattern)
    bones = get_mode_bones().keys()
    # bones = ['DEF_Name_Needle.L', 'DEF_01_Name_Needle.L', '']
    # bones = ['']
    def __num(r, count, l):
        if count == 0: return ''
        else: return r + str(count).rjust(2, '0') + l
    def __enumerate(name, count=0):
        if isinstance(name, list):
            name_list = name
            e_name_list = []
            is_present = False
            for n in name_list:
                e_name = n.replace('@_', __num('', count, '_'))
                if e_name == n:
                    e_name = n.replace('_@', __num('_', count, ''))
                if e_name in bones:
                    is_present = True
                    break
                e_name_list.append(e_name)
            if is_present:
                count += 1
                return __enumerate(name_list, count)
            else:
                return e_name_list
        elif isinstance(name, str):
            e_name = name.replace('@_', __num('', count, '_'))
            if name == e_name:
                e_name = name.replace('_@', __num('_', count, ''))
            if e_name in bones:
                count += 1
                return __enumerate(name, count)
            else:
                return e_name
    def __create(name, pattern):
        if name and len(pattern.split('@')) <= 2:
            (prefix, suffix) = split_pattern(pattern)
            (name, _, endfix, _) = split_name(name)
            if name.upper().endswith(suffix.upper()):
                name = name[:len(name) - len(suffix)]
            if prefix:
                return (prefix + '@_' + name + suffix + endfix)
            else:
                return (prefix + name + suffix + '_@' + endfix)
        else:
            print(f'Error: in ({str(name)}) or in ({str(pattern)})')
    is_list_name = False
    if isinstance(name, list) and len(name) == 1:
        is_list_name = True
        name = name[0]
    if isinstance(name, list):
        name_list = name
        if len(set(name_list)) == 1:
            e_name = __create(name_list[0], pattern)
            b_name_list = []
            for i in range(len(name_list)):
                b_name = __enumerate(e_name, 1)
                b_name_list.append(b_name)
                bones.append(b_name)
            return b_name_list
        else:
            e_name_list = []
            for name in name_list:
                name = __create(name, pattern)
                e_name_list.append(name)
            return __enumerate(e_name_list)
    elif isinstance(name, str):
        e_name = __create(name, pattern)
        r_name = __enumerate(e_name)
        if is_list_name:
            r_name = [r_name]
        return r_name
    else:
        print(f'Error: in ({str(name)}) or in ({str(pattern)})')
# print(create_name(['DEF_Toe.L.003'], '@_Leaf'))
 


# TODO continuous_bone_chain()
def continuous_bone_chain(bone_chain, check_connected=False):
    """ Check whether bone in list connect in chain or not.
        Return: List of PoseBone or EditBone, where `Grand Child First` and `Grand Parent Last`"""

    mode = bpy.context.mode
    if isinstance(bone_chain, list) and bone_chain and (mode == 'POSE' or mode == 'EDIT_ARMATURE'):
        if isinstance(bone_chain[0], str):
            obj = bpy.context.object
            if mode == 'EDIT_ARMATURE':
                bones = obj.data.edit_bones
            elif mode == 'POSE':
                bones = obj.pose.bones
            new_bone_chain = [bones[b] for b in bone_chain if b in bones]
            if len(new_bone_chain) < len(bone_chain):
                defectives = list(set(bone_chain) - set(new_bone_chain))
                return f'Bones not found {defectives}'
            bone_chain = new_bone_chain
        leaf_bones = [b for b in bone_chain if not b.children or not (set(b.children) & set(bone_chain))]
        if len(leaf_bones) > 1 or len(leaf_bones) == 0:
            return 'Bones parenting is not linear'
        grand_child = leaf_bones[0]
        sorted_bone_chain = [grand_child]
        child = grand_child
        parent = grand_child.parent
        while parent in bone_chain:
            if check_connected and not parent.use_connect:
                return 'Disconnected bone chain'
            if not check_connected:
                distance = abs((child.head - parent.tail).length)
                if distance > 0.0001:
                    return f'Displaced bone {child.name}'
            sorted_bone_chain.append(parent)
            child = parent
            parent = child.parent
        return sorted_bone_chain




# TODO refresh_view()
def refresh_view():
    if bpy.context and bpy.context.screen:
        for a in bpy.context.screen.areas:
            a.tag_redraw()


# TODO get_bone(data)
def get_bone(data):
    def get_set(items):
        if len(items) == 2:
            armature = items[0]
            bone = items[1]
            return (armature, bone)
        elif len(items) > 2:
            return '`:` should not in name'
        return 'data is corrupted'

    items = data.split(' : ')
    bone_set = get_set(items)
    if isinstance(bone_set, str):
        self.report({"ERROR"}, bone_set)
    else:
        return bone_set
    return None

# TODO get_bone_set(data)
def get_bone_set(data):
    def get_set(items):
        if len(items) == 2:
            armature = items[0]
            bones = []
            try:
                bones = json.loads(items[1].replace("'", '"'))
            except:
                return '`bone_list` is corrupted'
            if armature != '' and isinstance(bones, list) and len(bones) > 0:
                return (armature, bones)
        elif len(items) > 2:
            return '`:` should not in name'
        return 'data is corrupted'

    items = data.split(' : ')
    bone_set = get_set(items)
    if isinstance(bone_set, str):
        self.report({"ERROR"}, bone_set)
    else:
        return bone_set
    return None



# TODO get_longest_chain(bone_list)
def get_longest_chain(bone_list):
    def get_chain(bone, bones):
        if bone.parent is not None and bone.parent in bones:
            return get_chain(bone.parent, bones) + [bone]
        else:
            return [bone]

    longest_chain = []
    for bone in bone_list:
        chain = get_chain(bone, bone_list)
        if len(chain) > len(longest_chain):
            longest_chain = chain
    return longest_chain


# TODO make_name(prefix, remove_prefix_list, name)
def make_name(prefix, remove_prefix_list, name):
    for r_prefix in remove_prefix_list:
        if r_prefix != '':
            is_found = True
            for idx in range(len(r_prefix)):
                if name[idx].upper() != r_prefix[idx].upper():
                    is_found = False
                    break
            if is_found:
                new_name = name[idx+1:]
                name = new_name
                break
    return prefix + name

# TODO make_bone_name(prefix, name, name_list, count=None)
def make_bone_name(prefix, name, name_list, count=None):
    remove_list = ['def_', 'tgt_', 'ndl_', 'ctl_', 'mech_', 'mch_', 'org_', 'rot_', 'prnt_', 'twk_', 'opp_']
    remove_list.append(prefix)
    new_prefix = prefix + ((str(count) + '_') if count is not None else '')
    new_name = make_name(new_prefix, remove_list, name)
    if new_name.upper() in name_list:
        if count is None:
            count = 1
        else:
            count = count + 1
        return make_bone_name(prefix, name, name_list, count)
    else:
        return new_name




# TODO get_nearest_axis(target_matrix, ref_matrix, axis)
def get_nearest_axis(target_matrix, ref_matrix, axis):
    import numpy as np

    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
        angle = degrees(angle)
        return min(angle, 180-angle, 360-angle)

    rot = (ref_matrix.inverted() @ target_matrix).to_euler()

    x_rotation = Matrix.Rotation(rot[0], 3, 'X')
    y_rotation = Matrix.Rotation(rot[1], 3, 'Y')
    z_rotation = Matrix.Rotation(rot[2], 3, 'Z')

    x_point = Vector((1, 0, 0))
    y_point = Vector((0, 1, 0))
    z_point = Vector((0, 0, 1))

    dir_point = Vector((0, 0, 0))
    dir_point[axis] = 1

    rotation = z_rotation @ y_rotation @ x_rotation

    trans_x = rotation @ x_point
    trans_y = rotation @ y_point
    trans_z = rotation @ z_point

    x = angle_between(dir_point, trans_x)
    y = angle_between(dir_point, trans_y)
    z = angle_between(dir_point, trans_z)

    min_value = min(x, y, z)

    if min_value == x:
        return (0, (1 if trans_x[axis] > 0 else -1), min_value)
    elif min_value == y:
        return (1, (1 if trans_y[axis] > 0 else -1), min_value)
    elif min_value == z:
        return (2, (1 if trans_z[axis] > 0 else -1), min_value)

# TODO normalize_inf
def normalize_inf(inf_list):
    def calc(lst, size=1):
        is_len_one = (len(lst) == 1)
        item = lst.pop(0)
        inf = round(item / size, 4)
        if is_len_one:
            return [inf]
        else:
            size -= item
            return calc(lst, size) + [inf]
    return calc(inf_list, sum([inf for inf in inf_list]))


# TODO do_trans(item_list, trans_tuple_list, return_type='')
def do_trans(item_list, trans_tuple_list, return_type=''):
    # def pre_checking():
    #     def check_tuple(t):
    #         if isinstance(t, tuple) and len(t) == 3:
    #             (space, refs, values) = t
    #             space_upper = space.upper()
    #             if space_upper == 'LOCAL' or space_upper == 'PARENT' or space_upper == 'GLOBAL' or space_upper == 'GLOBAL X90':
    #                 is_edit_bone = (str(type(refs)) == "<class 'bpy_types.EditBone'>")
    #                 if ((space_upper == 'LOCAL' or space_upper == 'PARENT') and is_edit_bone) or space_upper == 'GLOBAL' or space_upper == 'GLOBAL X90':
    #                     if values is None or (isinstance(values, tuple) and len(values) == 3):
    #                         return True
    #                     else:
    #                         return 'values must be a `Tuple` type with length 3 for x, y and z'
    #                 else:
    #                     return '`Parent` and `Local` space need a bone refrence'
    #             else:
    #                 return 'space must be `Local`, `Parent`, `Global` or `Global X90`'
    #         else:
    #             return 'item must be `Tuple` of len 3, for space, values and refrence'
    #     message = ''
    #     if armature is not None and armature.type == 'ARMATURE':
    #         if isinstance(name, str) and name != '':
    #             loc_check = check_tuple(loc_tuple)
    #             if isinstance(loc_check, bool) and loc_check == True:
    #                 rot_check = check_tuple(rot_tuple)
    #                 if rot_tuple is None or (isinstance(rot_check, bool) and rot_check == True):
    #                     return True
    #                 else:
    #                     message = 'Arg 4 : Roation ' + rot_check
    #             else:
    #                 message = 'Arg 3 : Location ' + loc_check
    #         else:
    #             message = 'Arg 2 : Name is not Correct'
    #     else:
    #         message = 'Arg1 : Must be a Armature Object'
    #     print('Error :', message)
    #     return False



        def get_aligned_matrix(target_matrix, ref_matrix):
            # Get Nearest Axes
            (d1_idx, d1_sign, _) = get_nearest_axis(target_matrix, ref_matrix, 0)
            (d2_idx, d2_sign, _) = get_nearest_axis(target_matrix, ref_matrix, 1)
            (d3_idx, d3_sign, _) = get_nearest_axis(target_matrix, ref_matrix, 2)

            # Create the rotation matrix
            rotation_matrix = mathutils.Matrix.Identity(3)
            rotation_matrix[0] = mathutils.Vector((d1_idx == 0, d1_idx == 1, d1_idx == 2)) * d1_sign
            rotation_matrix[1] = mathutils.Vector((d2_idx == 0, d2_idx == 1, d2_idx == 2)) * d2_sign
            rotation_matrix[2] = mathutils.Vector((d3_idx == 0, d3_idx == 1, d3_idx == 2)) * d3_sign

            return ref_matrix @ rotation_matrix.to_euler().to_matrix().to_4x4()




        def matrix_rotation(source_item, target_matrix, transform_type, protect_list=[]):
            if not isinstance(target_matrix, mathutils.Matrix):
                return 'Error: target_matrix should be a mathutils.Matrix'

            rad_x, rad_y, rad_z = 0, 0, 0

            if isinstance(source_item, mathutils.Matrix):
                source_rotation = source_item.to_euler()
                rad_x = source_rotation.x
                rad_y = source_rotation.y
                rad_z = source_rotation.z
            elif isinstance(source_item, Vector):
                rad_x = source_item.x
                rad_y = source_item.y
                rad_z = source_item.z
            elif isinstance(source_item, tuple) and len(source_item) == 3:
                rad_x = math.radians(source_item[0])
                rad_y = math.radians(source_item[1])
                rad_z = math.radians(source_item[2])
            else:
                return 'Error: Unsupported Source Item'

            type_upper = transform_type.upper()
            t_loc, t_rot, t_scale = target_matrix.decompose()
            t_rot = target_matrix.to_euler()

            if type_upper == 'REPLACE':
                if 'X' not in protect_list:
                    t_rot.x = rad_x
                if 'Y' not in protect_list:
                    t_rot.y = rad_y
                if 'Z' not in protect_list:
                    t_rot.z = rad_z
                new_t_rot = mathutils.Euler((t_rot.x, t_rot.y, t_rot.z), 'XYZ')
            elif type_upper == 'ADD':
                rotation_matrix = mathutils.Euler((rad_x, rad_y, rad_z), 'XYZ')
                new_t_rot = (target_matrix.to_euler().to_matrix() @ rotation_matrix.to_matrix()).to_euler('XYZ')
            elif type_upper == 'SUBTRACT':
                rotation_matrix = mathutils.Euler((rad_x, rad_y, rad_z), 'XYZ')
                new_t_rot = (target_matrix.to_euler().to_matrix() @ rotation_matrix.to_matrix().inverted()).to_euler('XYZ')
            
            if new_t_rot is None:
                new_t_rot = t_rot
            
            # T = mathutils.Matrix.Translation(t_loc)
            # R = t_rot.to_matrix().to_4x4()
            # S = mathutils.Matrix.Diagonal(t_scale.to_4d())

            # return T @ R @ S
            return mathutils.Matrix.LocRotScale(t_loc, new_t_rot, t_scale)


        def matrix_location(source_item, target_matrix, transform_type, protect_list=[]):
            if not isinstance(target_matrix, mathutils.Matrix):
                return 'Error: target_matrix should be a mathutils.Matrix'

            loc_x, loc_y, loc_z = 0, 0, 0

            if isinstance(source_item, mathutils.Matrix):
                source_loc = source_item.translation
                loc_x = source_loc.x
                loc_y = source_loc.y
                loc_z = source_loc.z
            elif isinstance(source_item, Vector):
                loc_x = source_item.x
                loc_y = source_item.y
                loc_z = source_item.z
            elif isinstance(source_item, tuple) and len(source_item) == 3:
                loc_x = source_item[0]
                loc_y = source_item[1]
                loc_z = source_item[2]
            else:
                return 'Error: Unsupported Source Item' + type(source_item)

            type_upper = transform_type.upper()
            t_loc, t_rot, t_scale = target_matrix.decompose()

            if type_upper == 'REPLACE':
                new_t_loc = t_loc
                if 'X' not in protect_list:
                    new_t_loc.x = loc_x
                if 'Y' not in protect_list:
                    new_t_loc.y = loc_y
                if 'Z' not in protect_list:
                    new_t_loc.z = loc_z
            elif type_upper == 'ADD':
                vec = mathutils.Vector((loc_x, loc_y, loc_z))
                inv = target_matrix.inverted()
                new_t_loc = t_loc + (vec @ inv)
            elif type_upper == 'MULTIPLY':
                vec = mathutils.Vector((loc_x, loc_y, loc_z))
                inv = target_matrix.inverted()
                new_t_loc = t_loc * (vec @ inv)
            elif type_upper == 'SUBTRACT':
                vec = mathutils.Vector((loc_x, loc_y, loc_z))
                inv = target_matrix.inverted()
                new_t_loc = t_loc - (vec @ inv)
            
            if new_t_loc is None:
                new_t_loc = t_loc
            
            # T = mathutils.Matrix.Translation(t_loc)
            # R = t_rot.to_matrix().to_4x4()
            # S = mathutils.Matrix.Diagonal(t_scale.to_4d())

            # return T @ R @ S
            return mathutils.Matrix.LocRotScale(new_t_loc, t_rot, t_scale)
        
        def get_matrix_world(item):
            if item.parent is not None and item.parent.matrix_local is not None:
                return get_matrix_world(item.parent) @ item.matrix_local
            else:
                return item.matrix_local
        
        def get_armature_obj(bone):
            for obj in bpy.data.objects:
                if obj.data is not None and obj.data.name == bone.id_data.name:
                    return obj
            return None

        def get_matrix_parent(item): # give parent space matrix
            if (str(type(item)) == "<class 'bpy_types.EditBone'>"):
                return get_matrix_world(get_armature_obj(item))
            elif (str(type(item)) == "<class 'bpy_types.Object'>"):
                if item.parent is not None:
                    return get_matrix_world(item.parent)
                else:
                    return Matrix.Identity(4)

        def get_item_matrix(item, matrix_type):
            matrix_type_upper = matrix_type.upper()
            if (str(type(item)) == "<class 'bpy_types.EditBone'>"):
                armature = get_armature_obj(item)
                if matrix_type_upper == 'LOCAL':
                    return item.matrix.copy()
                elif matrix_type_upper == 'PARENT':
                    if item.parent is not None and item.parent.matrix is not None:
                        return item.parent.matrix.copy()
                    else:
                        return '`EditBone` has no `Parent` bone'
                elif matrix_type_upper == 'GLOBAL':
                    return get_matrix_world(armature)
                elif matrix_type_upper == 'WORLD':
                    return get_matrix_world(armature) @ item.matrix
                return 'Unsupported type ' + matrix_type

            elif (str(type(item)) == "<class 'bpy_types.Object'>"):
                if matrix_type_upper == 'LOCAL':
                    return item.matrix_local.copy()
                elif matrix_type_upper == 'PARENT':
                    if item.parent is not None and item.parent.matrix_local is not None:
                        return item.parent.matrix_local.copy()
                    else:
                        return '`Object` has no `Parent`'
                elif matrix_type_upper == 'GLOBAL' or matrix_type_upper == 'WORLD':
                    return get_matrix_world(item)
                return 'Unsupported type ' + matrix_type
            return 'Unsupported Item ' + str(type(item))

        def set_item_matrix(item, matrix_item):
            if (str(type(item)) == "<class 'bpy_types.EditBone'>"):
                item.matrix = matrix_item
            elif (str(type(item)) == "<class 'bpy_types.Object'>"):
                item.matrix_local = matrix_item

        # is_okay = pre_checking()
        # if is_okay:
        if True:

            # Rotate.axis -by- global (rotate axis near to global X)
            # Rotate -of- global.axis (rotate global X)
            # Rotate.align -to- global (align to nearest global axis)

            # Move -on- global.axis
            # Move.flip global.X (Flip Global X axis)
            def get_special_matrix(type, space_list, subtype, values, refs, target_matrix, matrix_parent):
                # print('Working...', type, subtype, space_list, values)
                if type.upper() == 'ROTATE':
                    if subtype.upper() == 'ALIGN' and len(space_list) == 1:
                        space = space_list[0]
                        ref_matrix = get_item_matrix(refs, space)
                        tgt_matrix_world = matrix_parent @ target_matrix

                        rslt_matrix_world = get_aligned_matrix(tgt_matrix_world, ref_matrix)
                        rslt_matrix = matrix_parent.inverted() @ rslt_matrix_world
                        return (rslt_matrix, True, True)

                    if len(space_list) == 2 and space_list[1] == 'AXIS':
                        if isinstance(values, tuple) and len(values) == 3:
                            space = space_list[0]
                            ref_matrix = get_item_matrix(refs, space)
                            tgt_matrix_world = matrix_parent @ target_matrix

                            x_rotation = Matrix.Rotation(radians(values[0]), 4, 'X')
                            y_rotation = Matrix.Rotation(radians(values[1]), 4, 'Y')
                            z_rotation = Matrix.Rotation(radians(values[2]), 4, 'Z')
                            rotation = z_rotation @ y_rotation @ x_rotation

                            matrix_relative = ref_matrix.inverted() @ tgt_matrix_world
                            rslt_matrix = ref_matrix @ (rotation @ matrix_relative)

                            rslt_matrix = matrix_parent.inverted() @ rslt_matrix
                            return (rslt_matrix, False, False)

                    if subtype.upper() == 'AXIS' and len(space_list) == 1:
                        if isinstance(values, tuple) and len(values) == 3:
                            space = space_list[0]
                            ref_matrix = get_item_matrix(refs, space)
                            tgt_matrix_world = matrix_parent @ target_matrix

                            x_rotation = Matrix.Rotation(radians(values[0]), 4, 'X')
                            y_rotation = Matrix.Rotation(radians(values[1]), 4, 'Y')
                            z_rotation = Matrix.Rotation(radians(values[2]), 4, 'Z')
                            rotation = z_rotation @ y_rotation @ x_rotation

                            matrix_relative = ref_matrix.inverted() @ tgt_matrix_world

                            t_loc, t_rot, t_sca = matrix_relative.decompose()

                            T = mathutils.Matrix.Translation(t_loc)
                            R = t_rot.to_matrix().to_4x4()
                            S = mathutils.Matrix.Diagonal(t_sca.to_4d())

                            rslt_relative = T @ (rotation @ R) @ S
                            rslt_matrix = ref_matrix @ rslt_relative

                            rslt_matrix = matrix_parent.inverted() @ rslt_matrix
                            return (rslt_matrix, False, False)

                elif type.upper() == 'MOVE':
                    if len(space_list) == 2 and space_list[1] == 'AXIS':
                        if isinstance(values, tuple) and len(values) == 3:
                            space = space_list[0]
                            ref_matrix = get_item_matrix(refs, space)
                            tgt_matrix_world = matrix_parent @ target_matrix

                            matrix_relative = ref_matrix.inverted() @ tgt_matrix_world
                            t_loc, t_rot, t_sca = matrix_relative.decompose()

                            T = mathutils.Matrix.Translation(t_loc)
                            R = t_rot.to_matrix().to_4x4()
                            S = mathutils.Matrix.Diagonal(t_sca.to_4d())

                            trans = Matrix.Translation(Vector(values))
                            rslt_relative = T @ (trans @ R) @ S
                            rslt_matrix = ref_matrix @ rslt_relative

                            rslt_matrix = matrix_parent.inverted() @ rslt_matrix
                            return (rslt_matrix, False, False)


            # This handles the 'Self', 'Self.' and 'Origin' types
            def get_space_matrix(type, space, subtype, values, refs, target_matrix, matrix_parent):
                space_upper = space.upper()

                space_list = space_upper.split('.')
                if subtype != '' or ((len(space_list) == 2 or len(space_list) == 3) and (space_list[1].upper() == 'AXIS')):
                    return get_special_matrix(type, space_list, subtype, values, refs, target_matrix, matrix_parent)
                else:
                    is_add_self = False
                    space_type = None
                    if len(space_list) == 1:
                        if space_list[0] == 'SELF':
                            is_add_self = True
                        else:
                            space_type = space_list[0]
                    elif len(space_list) == 2:
                        if space_list[0] == 'SELF':
                            is_add_self = True
                        space_type = space_list[1]

                    if is_add_self and (space_type is None or space_type == 'ORIGIN'):
                        return (target_matrix, True, True)
                    elif space_type is not None:
                        if space_type == 'ORIGIN':
                            return (mathutils.Matrix.Identity(4), True, True)
                        item_matrix = get_item_matrix(refs, space_type)
                        if isinstance(item_matrix, mathutils.Matrix):
                            if is_add_self:
                                return ((target_matrix @ item_matrix), True, True)
                            else:
                                return (item_matrix, True, True)
                        elif isinstance(item_matrix, str):
                            print("Error : " + item_matrix)
                            return None
                    print("Error : " + 'Unsupported space type' + space)
                    return None

            # This is the main Engine of this function
            def make_transform(trans_tuple, target_matrix, trans_type, subtype, matrix_parent):
                if isinstance(trans_tuple, tuple) and len(trans_tuple) == 3:
                    (trans_space, trans_refs, trans_values) = trans_tuple
                    trans_space_upper = trans_space.upper()
                    trans_type_upper = trans_type.upper()
                    return_data = get_space_matrix(trans_type, trans_space, subtype, trans_values, trans_refs, target_matrix.copy(), matrix_parent)
                    if isinstance(return_data, tuple) and len(return_data) == 3:
                        (space_matrix, is_conform_trans, is_add_values) = return_data

                        # Rest Code is mainly for `trans_values`
                        if space_matrix is not None:
                            if isinstance(space_matrix, mathutils.Matrix):
                                result_matrix = space_matrix
                                if trans_type_upper == 'ROTATE':
                                    if isinstance(trans_values, tuple) and len(trans_values) == 3 and is_add_values:
                                        space_matrix = matrix_rotation(trans_values, space_matrix.copy(), 'Add')
                                    if is_conform_trans:
                                        result_matrix = matrix_rotation(space_matrix, target_matrix, 'REPLACE')
                                elif trans_type_upper == 'MOVE':
                                    if isinstance(trans_values, tuple) and len(trans_values) == 3 and is_add_values:
                                        space_matrix = matrix_location(trans_values, space_matrix.copy(), 'Add')
                                    if is_conform_trans:
                                        result_matrix = matrix_location(space_matrix, target_matrix, 'REPLACE')
                                
                                if result_matrix is not None:
                                    return result_matrix
                            elif isinstance(space_matrix, str):
                                print("Error : " + space_matrix)
                                return None
                return None
            
            def get_trans_type_data(type):
                def all_values(type, protect_list):
                    data = type.split('.')
                    if len(data) == 2:
                        return (data[0], data[1], protect_list)
                    return (type, '', protect_list)

                type2 = type.replace(' ', '')
                data = type2.split('-')
                if len(data) == 2:
                    if len(data[1]) > 0:
                        d_list = data[1].upper().split('&')
                        return all_values(data[0], d_list)
                    else:
                        return all_values(data[0], [])
                elif len(data) == 1:
                    return all_values(data[0], [])
                return all_values(type, [])
            
            
            def protect_direction(old_matrix, result_matrix, trans_type, protect_list):
                has_loc = False
                loc_list = []
                has_rot = False
                rot_list = []
                for item in protect_list:
                    if item == 'ROT':
                        has_rot = True
                        rot_list = ['X', 'Y', 'Z']
                    elif item == 'LOC':
                        has_loc = True
                        loc_list = ['X', 'Y', 'Z']
                    elif len(item) > 3:
                        if item[:3] == 'ROT':
                            rots = item[3:]
                            has_rot = True
                            rot_list = [d for d in rots]
                        elif item[:3] == 'LOC':
                            locs = item[3:]
                            has_loc = True
                            loc_list = [d for d in locs]
                # print('Loc :', has_loc, loc_list)
                # print('Rot :', has_rot, rot_list)
                d_list = ['X', 'Y', 'Z']
                if has_loc:
                    transfer_list = [d for d in d_list if d not in loc_list]
                    return matrix_location(old_matrix, result_matrix, 'REPLACE', transfer_list)
                if has_rot:
                    transfer_list = [d for d in d_list if d not in rot_list]
                    return matrix_rotation(old_matrix, result_matrix, 'REPLACE', transfer_list)
                print('Error: Unknown list', protect_list)
                return result_matrix

            if not isinstance(item_list, list):
                item_list = [item_list]
            return_as_matrix = (return_type.upper().replace('_', ' ').replace('-', ' ') == 'AS MATRIX')
            result_list = []
            for item in item_list:

                ########################## START ##########################
                item_matrix = get_item_matrix(item, 'Local')

                if item_matrix is not None:
                    result_matrix = item_matrix
                    for (trans_type, trans_tuple) in trans_tuple_list:
                        (trans_type, trans_subtype, protect_directions) = get_trans_type_data(trans_type)
                        new_matrix = make_transform(trans_tuple, result_matrix.copy(), trans_type, trans_subtype, get_matrix_parent(item))
                        if new_matrix is not None:
                            if len(protect_directions) > 0:
                                result_matrix = protect_direction(result_matrix, new_matrix, trans_type, protect_directions)
                            else:
                                result_matrix = new_matrix
                    if return_as_matrix:
                        result_list.append(result_matrix)
                    else:
                        set_item_matrix(item, result_matrix)

            if len(result_list) > 0:
                if len(result_list) == 1:
                    return result_list[0]
                else:
                    return result_list



# # armature = bpy.context.active_object
# # new_bone = armature.data.edit_bones.new('temp.bone')
# # new_bone.length = 1
# bone = bpy.context.active_bone
# empty = bpy.data.objects['Empty']
# ref = bpy.data.objects['ref']
# #bone = bpy.context.object.data.edit_bones['TGT_Spine.005']



# empty.matrix_local = do_trans(empty, [
# #    (
# #        'Rotate.align',
# #        ('world', ref, None)
# #    ),
#    (
#        'Rotate - rotx',
#        ('self', ref, (10, 10, 10))
#    ),
#        # Rotate, Move

#        # Rotate.axis -by- global (rotate axis near to global X)
#        # Rotate -of- global.axis (rotate global X)
#        # Rotate.align -to- global (align to nearest global axis)

#        # Move -on- global.axis
#        # Move.flip global.XY (Same as Rotate-Rot -of- global.axis X=180)

#        # Move-LocX, Move-LocXY (Move without XY axes, X axis of old_matrix will be replaced with X axis of new_matrix)
#        # Move - Loc & RotX (Space will be remove before calc)
#        # Move-Loc&RotXYZ
#        # Self, Local, Parent, Global, World, Origin
#        # Self.Local, Self.Parent, Self.Global, Self.World (with `self` result will be added to old_matrix)

#        # for `Bone` Global is Armature and World is 3D View
#        # for `Object` Global and World is Same

# ], 'As Matrix') # <--- Return Result_Matrix

# # r = matrix.to_euler()
# # r.x, r.y, r.z

# # q = matrix.to_quaternion()
# # q.w, q.x, q.y, q.z

# # t = matrix.translation
# # t.x, t.y, t.z



# TODO get_change(item, new_matrix)
def get_change(item, new_matrix):
    if (str(type(item)) == "<class 'bpy_types.EditBone'>"):
        old_matrix = item.matrix
    elif (str(type(item)) == "<class 'bpy_types.Object'>"):
        old_matrix = item.matrix_local
    elif isinstance(item, Matrix):
        old_matrix = item
    else:
        print('Unknown Item', type(item), 'for get_change()')
    
    if isinstance(old_matrix, Matrix) and isinstance(new_matrix, Matrix):
        rot_change = (old_matrix.inverted() @ new_matrix).to_euler()
        loc_change = (old_matrix.translation - new_matrix.translation)
        return (loc_change, rot_change)

# TODO apply_change(change, item)
def apply_change(change, item):
    if (str(type(item)) == "<class 'bpy_types.EditBone'>"):
        matrix = item.matrix
    elif (str(type(item)) == "<class 'bpy_types.Object'>"):
        matrix = item.matrix_local
    elif isinstance(item, Matrix):
        matrix = item
    else:
        print('Unknown Item', type(item), 'for apply_change()')
        
    if isinstance(change, tuple) and len(change) == 2 and isinstance(matrix, Matrix):
        (loc_change, rot_change) = change
        loc, rot, sca = matrix.decompose()

        T = mathutils.Matrix.Translation(loc - loc_change)
        R = rot.to_matrix().to_4x4() @ rot_change.to_matrix().to_4x4()
        S = mathutils.Matrix.Diagonal(sca.to_4d())

        rslt_matrix = T @ R @ S

        if (str(type(item)) == "<class 'bpy_types.EditBone'>"):
            item.matrix = rslt_matrix
        elif (str(type(item)) == "<class 'bpy_types.Object'>"):
            item.matrix_local = rslt_matrix
        elif isinstance(item, Matrix):
            return rslt_matrix



# TODO make_needles(bone_list, size_fec, prefix)
def make_needles(bone_list, size_fec, prefix):
    if isinstance(bone_list, list) and len(bone_list) > 0:
        armature = bone_list[0].id_data
        name_list = [bone.name.upper() for bone in armature.edit_bones]
        needle_list = []
        for idx, bone in enumerate(bone_list):
            new_bone = armature.edit_bones.new(make_bone_name(prefix, bone.name, name_list))
            new_bone.use_deform = False
            new_bone.length = bone.length * size_fec
            do_trans(new_bone, [
                (
                    'Move',
                    ('Local', bone, None)
                )
            ])

            if bone.parent is not None:
                new_bone.use_connect = bone.use_connect
                new_bone.parent = bone.parent

            bone.use_connect = False
            bone.parent = new_bone
            needle_list.append(new_bone)
        return needle_list