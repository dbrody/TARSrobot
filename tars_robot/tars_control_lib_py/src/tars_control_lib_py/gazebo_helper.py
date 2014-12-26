import rospy
from ros_helper import setupService
from gazebo_msgs.srv import GetWorldProperties, DeleteModel, DeleteModelRequest, SpawnModel, GetModelState, GetModelStateRequest

from controller_manager_msgs.srv import LoadController, SwitchController
from geometry_msgs.msg import Pose
from os import path

# Delete all objects in gazebo except for ground_plane
def gazebo_delete_all_objects():
	print "Deleting all objects:"

	print "  Setting up services...",
	get_world_properties = setupService('/gazebo/get_world_properties', GetWorldProperties)
	delete_model_service = setupService('/gazebo/delete_model', DeleteModel)
	try:
		world_properties = get_world_properties()
		for name in world_properties.model_names:
			# Dont delete ground plane object
			if name != 'ground_plane':
				print "   Deleting %s ..." % name,
				delete_model_service(DeleteModelRequest(name))	
				print "done."
	except rospy.ServiceException:
		print "Unable to delete all objects."
	return False


def gazebo_spawn_robot(robot_file, name, controllers):
	initial_pose = Pose()
	initial_pose.position.x = 0
	initial_pose.position.y = 0
	initial_pose.position.z = 0

	try:
		print "Opening file: %s" % robot_file
		model_urdf_f = open(robot_file, 'r')
	except:
		print "Unable to open file: %s" % robot_file
		return		
	model_urdf = model_urdf_f.read()

	spawn_model = setupService('/gazebo/spawn_urdf_model', SpawnModel)

	print "Spawning model..."
	try:
		spawn_model(name, model_urdf, name, initial_pose, "world")
	except Exception as err:
		print err
		return False

	print "Setting up controllers..."

	load_controller = setupService('/'+name+'/controller_manager/load_controller', LoadController)
	switch_controllers = setupService('/'+name+'/controller_manager/switch_controller', SwitchController)

	try:
		for controller in controllers:
			result = load_controller(controller)
			print "Load controller "+controller+": %s" % result
	except Exception as err:
		print err
		return False

	print "Enabling controllers..."
	try:
		switch_controllers(controllers, [], 2)
	except Exception as err:
		print err
		return False

	return True


def gazebo_spawn_object(name, sdf_file, x=0, y=0, z=0):
	initial_pose = Pose()
	initial_pose.position.x = x
	initial_pose.position.y = y
	initial_pose.position.z = z

	model_sdf_f = open(sdf_file, 'r')
	model_sdf = model_sdf_f.read()

	print "Adding %s @ (%.2f, %.2f, %.2f)" % (name, x, y, z)
	spawn_sdf_model = setupService('/gazebo/spawn_sdf_model', SpawnModel)

	try:
		spawn_sdf_model(name, model_sdf, name, initial_pose, "world")
	except Exception as err:
		print "Error loading cone: %s" % err


def gazebo_get_model_state(name, context='world'):
	get_model_state = setupService('/gazebo/get_model_state', GetModelState)
	return get_model_state(GetModelStateRequest(name, context))