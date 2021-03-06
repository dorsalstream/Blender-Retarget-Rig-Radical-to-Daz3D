bl_info = {
    "name": "KeeMap Anicmation Transfer Tool",
    "description": "Tools for moving animation from one Rig To Another",
    "author": "Nick Keeline",
    "version": (0, 0, 0),
    "blender": (2, 83, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Transfer Animation"
}




import bpy
import math
import json
from os import path
import mathutils

def Update():
    #bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
     
    #bpy.context.view_layer.update()
    #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    
def SetBonePosition(SourceArmature, SourceBoneName, DestinationArmature, DestinationBoneName, DestinationTwistBoneName, WeShouldKeyframe):
    destination_bone =  DestinationArmature.pose.bones[DestinationBoneName]
    sourceBone = SourceArmature.pose.bones[SourceBoneName]
    
    WsPosition = sourceBone.matrix.translation
    matrix_final = SourceArmature.matrix_world @ sourceBone.matrix
    destination_bone.matrix.translation = matrix_final.translation
    #destination_bone.location = sourceBone.location
    Update()
    if (WeShouldKeyframe):
        currentFrame = bpy.context.scene.frame_current
        destination_bone.keyframe_insert(data_path='location',frame=currentFrame)

def GetBoneWSQuat(Bone, Arm):
    source_arm_matrix = Arm.matrix_world
    source_bone_matrix = Bone.matrix
    
    #get the source bones rotation in world space.
    source_bone_world_matrix = source_arm_matrix @ source_bone_matrix
    
    return source_bone_world_matrix.to_quaternion()
        
def SetBoneRotation(SourceArmature, SourceBoneName, DestinationArmature, DestinationBoneName, DestinationTwistBoneName, CorrectionQuat, WeShouldKeyframe, hastwistbone, xferAxis, Transpose):

    #Get the rotation of the bone in edit mode
#    SourceBoneEdit = SourceArmature.data.bones[SourceBoneName]
#    SourceBoneEditRotation = SourceBoneEdit.matrix_local.to_quaternion()
    
    #Get the rotation of the bone in edit mode
#    DestinationBoneEdit = DestinationArmature.data.bones[DestinationBoneName]
#    DestinationBoneEditRotation = DestinationBoneEdit.matrix_local.to_quaternion()
#    
#    DeltaSourceEditBoneandDestEditBone = DestinationBoneEditRotation.rotation_difference(SourceBoneEditRotation)
#    DeltaDestinationEditBoneandSourceEdit = SourceBoneEditRotation.rotation_difference(DestinationBoneEditRotation)
    
    #rotate the edit rotation quat first to armature rotation
    #ArmatureSpaceBoneEditPosition = RigArmature.rotation_quaternion * BoneEditRotation
    if(DestinationTwistBoneName == "" and hastwistbone):
        self.report({'ERROR'}, "You checked Twist Bone, but no name of bone entered!")
        hastwistbone = False
    elif hastwistbone:  
        TwistBone = DestinationArmature.pose.bones[DestinationTwistBoneName]
    destination_bone =  DestinationArmature.pose.bones[DestinationBoneName]
    sourceBone = SourceArmature.pose.bones[SourceBoneName]
    
    #Set Bone Position now that we've calculated it.
    destination_bone.rotation_mode = 'QUATERNION'
     
     #################################################
     ################## Get Source WS Quat ###########
     #################################################
    source_arm_matrix = SourceArmature.matrix_world
    source_bone_matrix = sourceBone.matrix
    
    #get the source bones rotation in world space.
    source_bone_world_matrix = source_arm_matrix @ source_bone_matrix
    
    SourceBoneRotWS = source_bone_world_matrix.to_quaternion()
    #print('Source Rotation WS Before:')
    #print(SourceBoneRotWS.to_euler())
     
     #################################################
     ################## Get Dest edit WS Quat ###########
     #################################################
    dest_arm_matrix = DestinationArmature.matrix_world
    dest_bone_matrix = destination_bone.matrix
    
    #get the DESTINATION bones rotation in world space.
    dest_bone_world_matrix = dest_arm_matrix @ dest_bone_matrix
    
    DestBoneRotWS = dest_bone_world_matrix.to_quaternion()
    #print('Destination Rotation WS Before:')
    #print(DestBoneRotWS.to_euler())
    
    DifferenceBetweenSourceWSandDestWS = DestBoneRotWS.rotation_difference(SourceBoneRotWS)
    #print('Difference Rotation')
    FinalQuat = destination_bone.rotation_quaternion.copy() @ DifferenceBetweenSourceWSandDestWS @ CorrectionQuat
    destination_bone.rotation_mode = 'XYZ'
    FinalEul = FinalQuat.to_euler()
    if Transpose == 'ZYX':
        destination_bone.rotation_euler.x = FinalEul.z
        destination_bone.rotation_euler.y = FinalEul.y
        destination_bone.rotation_euler.z = FinalEul.x
    elif Transpose == 'ZXY':
        destination_bone.rotation_euler.x = FinalEul.z
        destination_bone.rotation_euler.y = FinalEul.x
        destination_bone.rotation_euler.z = FinalEul.y
    elif Transpose == 'XZY':
        destination_bone.rotation_euler.x = FinalEul.x
        destination_bone.rotation_euler.y = FinalEul.z
        destination_bone.rotation_euler.z = FinalEul.y
    elif Transpose == 'YZX':
        destination_bone.rotation_euler.x = FinalEul.y
        destination_bone.rotation_euler.y = FinalEul.z
        destination_bone.rotation_euler.z = FinalEul.x
    elif Transpose == 'YXZ':
        destination_bone.rotation_euler.x = FinalEul.y
        destination_bone.rotation_euler.y = FinalEul.x
        destination_bone.rotation_euler.z = FinalEul.z
    else:
        destination_bone.rotation_euler = FinalEul
    
    if xferAxis == 'X':
        destination_bone.rotation_euler.y = 0
        destination_bone.rotation_euler.z = 0
    elif xferAxis == 'Y':
        destination_bone.rotation_euler.x = 0
        destination_bone.rotation_euler.z = 0
    elif xferAxis == 'Z':
        destination_bone.rotation_euler.x = 0
        destination_bone.rotation_euler.y = 0
    elif xferAxis == 'XY':
        destination_bone.rotation_euler.z = 0
    elif xferAxis == 'XZ':
        destination_bone.rotation_euler.y = 0
    elif xferAxis == 'YZ':
        destination_bone.rotation_euler.x = 0
        
    Update()
    
    if (hastwistbone):
        TwistBone.rotation_mode = 'XYZ'
        yrotation = destination_bone.rotation_euler.y
        destination_bone.rotation_euler.y = 0
        TwistBone.rotation_euler.y = math.degrees(yrotation)
        #print('Setting Twist Bone: ' + yrotation)
        #TwistBone.rotation_mode = 'QUATERNION'
        #destination_bone.rotation_mode = 'QUATERNION'
        
    Update()
    
    if (WeShouldKeyframe):
        currentFrame = bpy.context.scene.frame_current
        destination_bone.rotation_mode = 'XYZ'
        destination_bone.keyframe_insert(data_path='rotation_euler',frame=currentFrame)
        #print('keyframed' + str(currentFrame))
        if (hastwistbone):
            TwistBone.rotation_mode = 'XYZ'
            TwistBone.keyframe_insert(data_path='rotation_euler',frame=currentFrame)

def GetBoneEditRotationWorldSpace(arm, bonename):
    BoneEdit = arm.data.bones[bonename]
    BoneEditRotation = BoneEdit.matrix_local.to_quaternion()
    BoneEditWS = arm.rotation_quaternion*BoneEditRotation
    return BoneEditWS

class KeeMapSettings(bpy.types.PropertyGroup):

    start_frame_to_apply: bpy.props.IntProperty(
        name = "Starting Frame",
        description="Frame to Apply Motion Capture To",
        default = 0,
        min = 0,
        max = 10000
        )
        
    number_of_frames_to_apply: bpy.props.IntProperty(
        name = "Number of Samples",
        description="Number of Samples to read in and apply",
        default = 100,
        min = 0,
        max = 10000
        )


    keyframe_every_n_frames: bpy.props.IntProperty(
        name = "Mouth Keyframe Number",
        description="Frame to Apply a Keyframe to, 1 is every frame",
        default = 3,
        min = 1,
        max = 100
        )
    source_rig_name: bpy.props.StringProperty(
        name="Source Rig Name",
        description="Rig Name to Apply Capture To",
        default="",
        maxlen=1024
        )
    destination_rig_name: bpy.props.StringProperty(
        name="Destination Rig Name",
        description="Rig Name to Apply Capture To",
        default="",
        maxlen=1024
        )
        
    bone_mapping_file: bpy.props.StringProperty(
        name="Bone Mapping File to Read and Save",
        description="Select a File to Read In:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
        )
        
    keyframe_test: bpy.props.BoolProperty(
        name="KeyFrame Test",
        description="Use this checkbox to enable keyframing of this bone while testing.",
        default = False
        ) 
    
class KeeMapBoneMappingListItem(bpy.types.PropertyGroup): 
      #"""Group of properties representing a bone mapping from OpenPose to a Rig""" 
      
    name : bpy.props.StringProperty()
    label : bpy.props.StringProperty()
    description : bpy.props.StringProperty()

    SourceBoneName: bpy.props.StringProperty(
        name="Source Bone Name",
        description="This is the name for the rig bone name.",
        default="",
        maxlen=1024
        )

    DestinationBoneName: bpy.props.StringProperty(
        name="Destination Bone Name",
        description="This is the name for the rig bone name.",
        default="",
        maxlen=1024
        )
        
    keyframe_this_bone: bpy.props.BoolProperty(
        name="KeyFrame This Bone",
        description="Use this checkbox to disable keyframing of this bone for testing.",
        default = True
        ) 

    CorrectionFactor: bpy.props.FloatVectorProperty(
        name="Correction Rotation",
        description="After Setting the global position of the bone to the same as the source the script will rotate the bone by these angles afterwards to correct rotational differences between the sourc and destination bones.",
        subtype = 'EULER',
        unit = 'ROTATION',
        default = (0.0, 0.0, 0.0), 
        size = 3
        )

        
    has_twist_bone: bpy.props.BoolProperty(
        name="Has a Twist Bone",
        description="This will apply the twist along the y axis",
        default = False
        ) 
        

    TwistBoneName: bpy.props.StringProperty(
        name="Twist Bone Name",
        description="This is the name for the rig bone name.",
        default="",
        maxlen=1024
        )
        
    set_bone_position: bpy.props.BoolProperty(
        name="Set Position of Bone",
        description="This will set the bone position to the same position of the source bone.",
        default = False
        ) 
        
    set_bone_rotation: bpy.props.BoolProperty(
        name="Set Rotation of Bone",
        description="This will set the bone rotation to the same position of the source bone.",
        default = True
        ) 
        
      
    bone_rotation_application_axis: bpy.props.EnumProperty(
        name="Apply To Axis",
        description="Axis to Apply twist translation or rotation to, other axis will be left zero.",
        items=[ ('XYZ', "XYZ", ""),
                ('XY', "XY", ""),
                ('XZ', "XZ", ""),
                ('YZ', "YZ", ""),
                ('X', "X", ""),
                ('Y', "Y", ""),
                ('Z', "Z", "")
               ]
        )
      
    bone_transpose_axis: bpy.props.EnumProperty(
        name="Transpose Axis",
        description="Select Two Axis to swap when applying angle.",
        items=[ ('NONE', "NONE", ""),
                ('ZXY', "ZXY", ""),
                ('ZYX', "ZYX", ""),
                ('XZY', "XZY", ""),
                ('YZX', "YZX", ""),
                ('YXZ', "YXZ", ""),
                ('ZXY', "ZXY", "")
               ]
        )

####################################################################################
####################################################################################
####################################################################################
# Code for iteration through frames and applying positions and angles to rig
####################################################################################
####################################################################################
####################################################################################

class PerformAnimationTransfer(bpy.types.Operator):
    bl_idname = "wm.perform_animation_transfer"
    bl_label = "Read in OpenPose JSON Files and Apply to Character"

    def execute(self, context):
        scene = bpy.context.scene
        KeeMap = bpy.context.scene.keemap_settings 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        
        SourceArmName = KeeMap.source_rig_name
        DestArmName = KeeMap.destination_rig_name
        KeyFrame_Every_Nth_Frame = KeeMap.keyframe_every_n_frames
        NumberOfFramesToTransfer = KeeMap.number_of_frames_to_apply
        #StartFrame = scene.frame_current
        StartFrame = KeeMap.start_frame_to_apply


        print('')
        print('Start of Everything')
        print('')
        #SourcArm = bpy.context.selected_objects[SourcArmName]
        #DestArm  = bpy.context.selected_objects[DestArmName]
                    
        if SourceArmName == "":
            self.report({'ERROR'}, "Must Have a Source Armature Name Entered")
        elif DestArmName == "":
            self.report({'ERROR'}, "Must Have a Destination Armature Name Entered")
        else:
            SourceArm = bpy.data.objects[SourceArmName]
            DestArm  = bpy.data.objects[DestArmName]
            
            i=0
            while (i < NumberOfFramesToTransfer):
                #scene.frame_current = StartFrame + i
                bpy.context.scene.frame_set(StartFrame + i)
                Update()
                
                print('')
                CurrentFrame = scene.frame_current
                EndFrame =  StartFrame + NumberOfFramesToTransfer
                PercentComplete = ((CurrentFrame - StartFrame)/(EndFrame - StartFrame))*100
                print('Working On Frame: ' + str(scene.frame_current) + ' of ' + str(EndFrame) + ' ' + "{:.1f}".format(PercentComplete) + '%')
                print('')

                bpy.ops.wm.test_all_bones(keyframe = True)
                i = i + KeyFrame_Every_Nth_Frame

        return{'FINISHED'}
    
class KEEMAP_TestSetRotationOfBone(bpy.types.Operator): 
    """Maps a Single Bone on the Current Frame to Test Mapping""" 
    bl_idname = "wm.test_set_rotation_of_bone" 
    bl_label = "Test Bone Re-Targetting" 
    index2pose: bpy.props.IntProperty() 
    keyframe: bpy.props.BoolProperty(default = False) 
    
    def execute(self, context): 
        scene = bpy.context.scene
        if(self.index2pose == -1):
            index = scene.keemap_bone_mapping_list_index 
        else:
            index = self.index2pose
        KeeMap = bpy.context.scene.keemap_settings 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        
        #if the box is checked we're going to keyframe no matter what:
        if KeeMap.keyframe_test:
            self.keyframe = True
            
        #print('')
        #print('Test Pressed:')
        SourceArmName = KeeMap.source_rig_name
        DestArmName = KeeMap.destination_rig_name
                    
        if SourceArmName == "":
            self.report({'ERROR'}, "Must Have a Source Armature Name Entered")
        elif DestArmName == "":
            self.report({'ERROR'}, "Must Have a Destination Armature Name Entered")
        else:
            SourceArm = bpy.data.objects[SourceArmName]
            DestArm  = bpy.data.objects[DestArmName]
            
            SourceBoneName = bone_mapping_list[index].SourceBoneName
            DestBoneName = bone_mapping_list[index].DestinationBoneName
            
            xferAxis = bone_mapping_list[index].bone_rotation_application_axis
            xPose = bone_mapping_list[index].bone_transpose_axis
            
            if SourceBoneName == "":
                self.report({'ERROR'}, "Must Have a Source Bone Name Entered")
            elif DestBoneName == "":
                self.report({'ERROR'}, "Must Have a Destination Bone Name Entered")
            else:
                HasTwist = bone_mapping_list[index].has_twist_bone
                TwistBoneName = bone_mapping_list[index].TwistBoneName
                CorrectionVectorX = bone_mapping_list[index].CorrectionFactor.x
                #print(math.degrees(CorrectionVectorX))
                CorrectionVectorY = bone_mapping_list[index].CorrectionFactor.y
                #print(math.degrees(CorrectionVectorY))
                CorrectionVectorZ = bone_mapping_list[index].CorrectionFactor.z
                #print(math.degrees(CorrectionVectorZ))
                corrEul = mathutils.Euler((CorrectionVectorX, CorrectionVectorY, CorrectionVectorZ), 'XYZ')
                #print('correction Eul in:')
                #print(corrEul)
                CorrQuat = corrEul.to_quaternion()
                #print('correction in:')
                #print(CorrQuat.to_euler())
                if bone_mapping_list[index].set_bone_rotation:
                    SetBoneRotation(SourceArm, SourceBoneName, DestArm, DestBoneName, TwistBoneName, CorrQuat, self.keyframe, HasTwist, xferAxis,xPose)
                if bone_mapping_list[index].set_bone_position:
                    SetBonePosition(SourceArm, SourceBoneName, DestArm, DestBoneName, TwistBoneName, self.keyframe)
        return{'FINISHED'}
    
class KEEMAP_BoneSelectedOperator(bpy.types.Operator):
    bl_idname = "wm.bone_selected"
    bl_label = "Operator to Change Selection based on selected bone"

    @classmethod
    def poll(cls, context):
        return len(context.selected_pose_bones) > 0
    
    def execute(self, context):
        print('Checking')

        bone_mapping_list = context.scene.keemap_bone_mapping_list
        index = context.scene.keemap_bone_mapping_list_index 
        KeeMap = bpy.context.scene.keemap_settings 
        
        DestArmName = KeeMap.destination_rig_name
        if DestArmName != '':
            DestArm  = bpy.data.objects[DestArmName]
            if len(context.selected_pose_bones) > 0:
                bonename = context.selected_pose_bones[0].name
                i = 0
                for bone_settings in bone_mapping_list:
                    if bone_settings.DestinationBoneName == bonename:
                        context.scene.keemap_bone_mapping_list_index = i
                    i = i+1
        return {'FINISHED'}    
    
class KEEMAP_TestAllBones(bpy.types.Operator): 
    """Test All Bones to set there position""" 
    bl_idname = "wm.test_all_bones" 
    bl_label = "Test Set All Bone's Posiitoin"
    keyframe: bpy.props.BoolProperty(default = False) 

    def execute(self, context): 

        bone_mapping_list = context.scene.keemap_bone_mapping_list
        index = context.scene.keemap_bone_mapping_list_index 
        # CODE FOR SETTING BONE POSITIONS:
        i = 0
        for bone_settings in bone_mapping_list:
            index = i
            print(bone_settings.name)
            bpy.ops.wm.test_set_rotation_of_bone(index2pose = index,keyframe = self.keyframe)
            i = i+1
        return{'FINISHED'}
      
class KEEMAP_GetSourceBoneName(bpy.types.Operator): 
    """If a bone is selected, get the name and popultate""" 
    bl_idname = "wm.get_source_bone_name" 
    bl_label = "Get Source Bone Name" 

    def execute(self, context): 
        scene = bpy.context.scene
        index = scene.keemap_bone_mapping_list_index 
        KeeMap = bpy.context.scene.keemap_settings 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        if len(context.selected_objects) == 1:
            rigname = context.selected_objects[0].name
            bonename = context.selected_pose_bones[0].name
        elif len(context.selected_objects) == 2:
            bonename = context.selected_pose_bones[0].name
            rig1 = context.selected_objects[0]
            if rig1.pose.bones.find(bonename) == -1:
                rigname = context.selected_objects[1].name
            else:
                rigname = context.selected_objects[0].name
        if len(context.selected_pose_bones) == 1:
            if rigname == KeeMap.source_rig_name:
                bone_mapping_list[index].SourceBoneName = bonename
            if rigname == KeeMap.destination_rig_name:
                bone_mapping_list[index].DestinationBoneName = bonename
            if bone_mapping_list[index].name == '' and rigname == KeeMap.source_rig_name:
                bone_mapping_list[index].name = bonename
        return{'FINISHED'} 
    
class KEEMAP_AutoGetBoneCorrection(bpy.types.Operator): 
    """Auto Calculate the Bones Correction Number from calculated to current position.""" 
    bl_idname = "wm.get_bone_rotation_correction" 
    bl_label = "Auto Calc Correction" 

    def execute(self, context): 
        scene = bpy.context.scene
        index = scene.keemap_bone_mapping_list_index 
        KeeMap = bpy.context.scene.keemap_settings 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        
        print('')
        print('Calc Pressed:')
        SourceArmName = KeeMap.source_rig_name
        DestArmName = KeeMap.destination_rig_name
        
        if SourceArmName == "":
            self.report({'ERROR'}, "Must Have a Source Armature Name Entered")
        elif DestArmName == "":
            self.report({'ERROR'}, "Must Have a Destination Armature Name Entered")
        else:
            SourceArm = bpy.data.objects[SourceArmName]
            DestArm  = bpy.data.objects[DestArmName]
            
            SourceBoneName = bone_mapping_list[index].SourceBoneName
            DestBoneName = bone_mapping_list[index].DestinationBoneName
            
            xferAxis = bone_mapping_list[index].bone_rotation_application_axis
            xPose = bone_mapping_list[index].bone_transpose_axis
            
            if SourceBoneName == "":
                self.report({'ERROR'}, "Must Have a Source Bone Name Entered")
            elif DestBoneName == "":
                self.report({'ERROR'}, "Must Have a Destination Bone Name Entered")
            else:
                destBone = DestArm.pose.bones[DestBoneName]
                sourceBone = SourceArm.pose.bones[SourceBoneName]
                destBoneMode = 'XYZ'
                destBone.rotation_mode = destBoneMode
                
                StartingDestBoneWSQuat = GetBoneWSQuat(destBone, DestArm)
                print("Destination Bone Starting WS")
                print(StartingDestBoneWSQuat.to_euler())
                destBoneStartPosition = destBone.rotation_euler.copy()
                #print(destBoneStartPosition)
                
                HasTwist = bone_mapping_list[index].has_twist_bone
                if HasTwist:
                    TwistBoneName = bone_mapping_list[index].TwistBoneName
                    TwistBone = DestArm.pose.bones[TwistBoneName]
                    y =  TwistBone.rotation_euler.y
                else:
                    TwistBoneName = ''
                    
                CorrQuat =  mathutils.Quaternion((1,0,0,0))
                SetBoneRotation(SourceArm, SourceBoneName, DestArm, DestBoneName, TwistBoneName, CorrQuat, False, HasTwist, xferAxis,xPose)
                Update()
                
                ModifiedDestBoneWSQuat = GetBoneWSQuat(destBone, DestArm)
                print("Destination Bone After Modifying WS")
                print(ModifiedDestBoneWSQuat.to_euler())
                
                q = ModifiedDestBoneWSQuat.rotation_difference(StartingDestBoneWSQuat)
                print('Difference between before and After modification')
                print(q.to_euler())
                corrEuler = q.to_euler()
                print(math.degrees(corrEuler.x))
                print(math.degrees(corrEuler.y))
                print(math.degrees(corrEuler.z))
                print(corrEuler.to_quaternion())
                bone_mapping_list[index].CorrectionFactor.x = corrEuler.x
                bone_mapping_list[index].CorrectionFactor.y = corrEuler.y
                bone_mapping_list[index].CorrectionFactor.z = corrEuler.z
                
                destBone.rotation_euler = destBoneStartPosition
                if HasTwist:
                    TwistBone.rotation_euler.y = y
                    destBone.rotation_euler.y = 0
                print(destBoneStartPosition)
                
        return{'FINISHED'}
    
    
class KEEMAP_BONE_UL_List(bpy.types.UIList): 
    """Demo UIList.""" 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # We could write some code to decide which icon to use here... 
        custom_icon = 'BONE_DATA' 
        
        # Make sure your code supports all 3 layout types if 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            layout.label(text=item.name, icon = custom_icon) 
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon) 
            
       
class KEEMAP_LIST_OT_NewItem(bpy.types.Operator): 
    """Add a new item to the list.""" 
    bl_idname = "keemap_bone_mapping_list.new_item" 
    bl_label = "Add a new item" 

    def execute(self, context): 
        index = context.scene.keemap_bone_mapping_list_index 
        context.scene.keemap_bone_mapping_list.add() 
        index = len(context.scene.keemap_bone_mapping_list)
        return{'FINISHED'}       
    
class KEEMAP_LIST_OT_DeleteItem(bpy.types.Operator): 
    """Delete the selected item from the list.""" 
    bl_idname = "keemap_bone_mapping_list.delete_item" 
    bl_label = "Deletes an item" 
    
    @classmethod 
    def poll(cls, context): 
        return context.scene.keemap_bone_mapping_list 
    
    def execute(self, context): 
        bone_mapping_list = context.scene.keemap_bone_mapping_list
        index = context.scene.keemap_bone_mapping_list_index 
        bone_mapping_list.remove(index) 
        index = min(max(0, index - 1), len(bone_mapping_list) - 1) 
        return{'FINISHED'}

class KEEMAP_LIST_OT_MoveItem(bpy.types.Operator): 
    """Move an item in the list.""" 
    bl_idname = "keemap_bone_mapping_list.move_item" 
    bl_label = "Move an item in the list" 
    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', ""),)) 

    @classmethod 
    def poll(cls, context): 
        return context.scene.keemap_bone_mapping_list 
    
    def move_index(self): 
        """ Move index of an item render queue while clamping it. """ 
        scene = bpy.context.scene	
        index = scene.keemap_bone_mapping_list_index 
        list_length = len(bpy.context.scene.keemap_bone_mapping_list) - 1 # (index starts at 0) 
        new_index = index + (-1 if self.direction == 'UP' else 1) 
        index = max(0, min(new_index, list_length)) 
    
    def execute(self, context): 
        bone_mapping_list = context.scene.keemap_bone_mapping_list 
        scene = context.scene	
        index = scene.keemap_bone_mapping_list_index 
        neighbor = index + (-1 if self.direction == 'UP' else 1) 
        bone_mapping_list.move(neighbor, index) 
        self.move_index() 
        return{'FINISHED'}
    
class KEEMAP_LIST_OT_ReadInFile(bpy.types.Operator): 
    """Read in Bone Mapping File""" 
    bl_idname = "wm.keemap_read_file" 
    bl_label = "Read In Bone Mapping File" 

    def execute(self, context): 
        
        context.scene.keemap_bone_mapping_list_index = 0    
        bone_list = context.scene.keemap_bone_mapping_list
        bone_list.clear()
        
        KeeMap = bpy.context.scene.keemap_settings 
        filepath = bpy.path.abspath(KeeMap.bone_mapping_file)
        file = open(filepath, 'r')

        data = json.load(file)
        
        KeeMap.facial_capture = data['start_frame_to_apply']
        KeeMap.number_of_frames_to_apply = data['number_of_frames_to_apply']
        KeeMap.keyframe_every_n_frames = data['keyframe_every_n_frames']
        KeeMap.source_rig_name = data['source_rig_name']
        KeeMap.destination_rig_name = data['destination_rig_name']
        KeeMap.bone_mapping_file = data['bone_mapping_file']
        i = 0
        for p in data['bones']:
            bone_list.add()
            bone = bone_list[i]
            
            bone.name = p['name']
            bone.label = p['label']
            bone.description = p['description']
            bone.SourceBoneName = p['SourceBoneName']
            bone.DestinationBoneName = p['DestinationBoneName']
            bone.keyframe_this_bone = p['keyframe_this_bone']
            bone.CorrectionFactor.x = p['CorrectionFactorX']
            bone.CorrectionFactor.y = p['CorrectionFactorY']
            bone.CorrectionFactor.z = p['CorrectionFactorZ']
            bone.has_twist_bone = p['has_twist_bone']
            bone.TwistBoneName = p['TwistBoneName']
            bone.set_bone_position = p['set_bone_position']
            bone.set_bone_rotation = p['set_bone_rotation']
            bone.bone_rotation_application_axis = p['bone_rotation_application_axis']
            i = i + 1
        file.close()
        
        return{'FINISHED'}
     
class KEEMAP_LIST_OT_SaveToFile(bpy.types.Operator): 
    """Save Out Bone Mapping File""" 
    bl_idname = "wm.keemap_save_file" 
    bl_label = "Save Bone Mapping File" 

    def execute(self, context): 
        #context.scene.bone_mapping_list.clear() 
        KeeMap = bpy.context.scene.keemap_settings 
        filepath = bpy.path.abspath(KeeMap.bone_mapping_file)
        file = open(filepath, 'w+')
        
        rootParams = {
        "start_frame_to_apply":KeeMap.start_frame_to_apply,
        "number_of_frames_to_apply":KeeMap.number_of_frames_to_apply,
        "keyframe_every_n_frames":KeeMap.keyframe_every_n_frames,
        "source_rig_name":KeeMap.source_rig_name,
        "destination_rig_name":KeeMap.destination_rig_name,
        "bone_mapping_file":KeeMap.bone_mapping_file
        } 
        bone_list = context.scene.keemap_bone_mapping_list
        jsonbones = {}
        jsonbones['bones'] = []
        for bone in bone_list:
            jsonbones['bones'].append({
                'name': bone.name,
                'label': bone.label,
                'description': bone.description,
                'SourceBoneName': bone.SourceBoneName,
                'DestinationBoneName': bone.DestinationBoneName,
                'keyframe_this_bone': bone.keyframe_this_bone,
                'CorrectionFactorX': bone.CorrectionFactor.x,
                'CorrectionFactorY': bone.CorrectionFactor.y,
                'CorrectionFactorZ': bone.CorrectionFactor.z,
                'has_twist_bone': bone.has_twist_bone,
                'TwistBoneName': bone.TwistBoneName,
                'set_bone_position': bone.set_bone_position,
                'set_bone_rotation': bone.set_bone_rotation,
                'bone_rotation_application_axis': bone.bone_rotation_application_axis,
            })
        jsonbones.update(rootParams)
        print(jsonbones)
        json.dump(jsonbones, file)  
        file.close()
        return{'FINISHED'} 
    
class KeeMapToolsPanel(bpy.types.Panel):
    """Creates a Panel for the KeeMap animation retargetting rig addon"""
    bl_label = "KeeMap"
    bl_idname = "KEEMAP_PT_MAINPANEL"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"    
    bl_category = 'KeeMapRig'
    bl_context = "posemode"   

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene	
        row = layout.row() 
        row.label(text="KeeMap Script written by Nick Keeline")
        row = layout.row() 
        row.label(text="Subscribe to Checkered Bug on Youtube")
            
                            
class KeemapPanelOne(KeeMapToolsPanel, bpy.types.Panel):
    bl_idname = "KEEMAP_PT_TRANSFERSETTINGS"
    bl_label = "Transfer Settings"

    def draw(self, context):
        layout = self.layout
        KeeMap = bpy.context.scene.keemap_settings 
            
        #layout.label(text="Transfer Settings")
        layout.prop(KeeMap, "start_frame_to_apply")
        layout.prop(KeeMap, "number_of_frames_to_apply")
        layout.prop(KeeMap, "keyframe_every_n_frames")
        layout.prop(KeeMap, "source_rig_name")
        layout.prop(KeeMap, "destination_rig_name")
        layout.prop(KeeMap, "bone_mapping_file")
    
        row = layout.row()
        row.operator("wm.keemap_read_file")
        row.operator("wm.keemap_save_file")
        layout.operator("wm.perform_animation_transfer") 
          
class KeemapPanelTwo(KeeMapToolsPanel, bpy.types.Panel):
    bl_idname = "KEEMAP_PT_BONEMAPPING"
    bl_label = "Bone Mapping"

    def draw(self, context):
        layout = self.layout    
        scene = context.scene	
        KeeMap = bpy.context.scene.keemap_settings            
        row = layout.row()
        row.template_list("KEEMAP_BONE_UL_List", "The_Keemap_List", scene, "keemap_bone_mapping_list", scene,"keemap_bone_mapping_list_index")#, type='COMPACT')#, "index")
        row = layout.row() 
        row.operator('keemap_bone_mapping_list.new_item', text='NEW') 
        row.operator('keemap_bone_mapping_list.delete_item', text='REMOVE') 
        row.operator('keemap_bone_mapping_list.move_item', text='UP').direction = 'UP' 
        row.operator('keemap_bone_mapping_list.move_item', text='DOWN').direction = 'DOWN'
        row = layout.row() 
        row.label(text="List MUST be ordered Parent->Child")
        
        if scene.keemap_bone_mapping_list_index >= 0 and scene.keemap_bone_mapping_list: 
            item = scene.keemap_bone_mapping_list[scene.keemap_bone_mapping_list_index] 
            layout = self.layout    
            box = layout.box()
            box.prop(item, "name") 
            box.prop(item, "SourceBoneName") 
            box.prop(item, "DestinationBoneName")
            box.operator('wm.get_source_bone_name', text='GET NAME') 
            box.operator('wm.bone_selected', text='SELECT') 
            box.prop(item, "keyframe_this_bone")    
            row = layout.row() 
            row.prop(item, "set_bone_rotation")
            if item.set_bone_rotation:
                box = layout.box()
                box.prop(item, "bone_rotation_application_axis")
                box.prop(item, "bone_transpose_axis")
                box.prop(item, "CorrectionFactor")   
                box.operator('wm.get_bone_rotation_correction', text='CALC CORRECTiON') 
#                if not item.has_twist_bone: 
#                    box.operator('wm.get_bone_rotation_correction', text='CALC CORRECTiON') 
#                box.prop(item, "has_twist_bone")
#                if item.has_twist_bone:
#                    box.prop(item, "TwistBoneName")            
            row = layout.row() 
            row.prop(item, "set_bone_position")
            row = layout.row() 
            row.operator('wm.test_set_rotation_of_bone', text='TEST').index2pose = -1
            row.operator('wm.test_all_bones', text='TEST ALL').keyframe = KeeMap.keyframe_test
            layout.prop(KeeMap, "keyframe_test")
# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(KeemapPanelOne)
    bpy.utils.register_class(KeemapPanelTwo)
    bpy.utils.register_class(PerformAnimationTransfer)
    bpy.utils.register_class(KEEMAP_BONE_UL_List)
    bpy.utils.register_class(KEEMAP_GetSourceBoneName)
    bpy.utils.register_class(KeeMapToolsPanel)
    bpy.utils.register_class(KeeMapBoneMappingListItem)
    bpy.utils.register_class(KeeMapSettings)
    bpy.utils.register_class(KEEMAP_LIST_OT_NewItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_DeleteItem)
    bpy.utils.register_class(KEEMAP_LIST_OT_MoveItem)
    bpy.utils.register_class(KEEMAP_TestSetRotationOfBone)
    bpy.utils.register_class(KEEMAP_LIST_OT_ReadInFile)
    bpy.utils.register_class(KEEMAP_LIST_OT_SaveToFile)
    bpy.utils.register_class(KEEMAP_AutoGetBoneCorrection)
    bpy.utils.register_class(KEEMAP_TestAllBones)
    bpy.utils.register_class(KEEMAP_BoneSelectedOperator)
    bpy.types.Scene.keemap_bone_mapping_list_index = bpy.props.IntProperty()
    bpy.types.Scene.keemap_bone_mapping_list = bpy.props.CollectionProperty(type = KeeMapBoneMappingListItem) 
    bpy.types.Scene.keemap_settings = bpy.props.PointerProperty(type=KeeMapSettings)


def unregister():
    bpy.utils.unregister_class(PerformAnimationTransfer)
    bpy.utils.unregister_class(KEEMAP_BONE_UL_List)
    bpy.utils.unregister_class(KeeMapSettings)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_NewItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_DeleteItem)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_MoveItem)
    bpy.utils.unregister_class(KEEMAP_GetSourceBoneName)
    bpy.utils.unregister_class(KeeMapToolsPanel)
    bpy.utils.unregister_class(KeemapPanelOne)
    bpy.utils.unregister_class(KeemapPanelTwo)
    bpy.utils.unregister_class(KeeMapBoneMappingListItem)
    bpy.utils.unregister_class(KEEMAP_TestSetRotationOfBone)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_ReadInFile)
    bpy.utils.unregister_class(KEEMAP_LIST_OT_SaveToFile)
    bpy.utils.unregister_class(KEEMAP_AutoGetBoneCorrection)
    bpy.utils.unregister_class(KEEMAP_TestAllBones)
    bpy.utils.unregister_class(KEEMAP_BoneSelectedOperator)
    del bpy.types.Scene.keemap_bone_mapping_list
    del bpy.types.Scene.keemap_bone_mapping_list_index
    del bpy.types.Scene.keemap_settings
    

if __name__ == "__main__":
    register()
