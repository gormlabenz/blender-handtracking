import bpy
import socket
import json
import time

scale_factor = 10
scale_sphere = 0.3

def receive_landmarks_from_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    message = "Request landmarks"
    client_socket.send(message.encode('utf-8'))

    response = client_socket.recv(4096)
    client_socket.close()

    return response.decode('utf-8')

def create_sphere(name, location):
    bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    sphere = bpy.context.active_object
    sphere.name = name
    sphere.scale = (scale_sphere, scale_sphere, scale_sphere)
    return sphere

def update_landmarks():
    host = "localhost"
    port = 12345
    landmark_data_str = receive_landmarks_from_server(host, port)

    # Process landmark data
    landmark_data = json.loads(landmark_data_str)

    # Iterate through landmarks and create/update spheres in Blender
    for index, landmark in enumerate(landmark_data):
        sphere_name = f"landmark_{index}"
        location = (
            landmark['x'] * scale_factor, 
            landmark['z'] * scale_factor,
            landmark['y'] * - scale_factor) 

        sphere = bpy.data.objects.get(sphere_name)
        if sphere is None:
            create_sphere(sphere_name, location)
        else:
            sphere.location = location

class TimerOperator(bpy.types.Operator):
    bl_idname = "wm.timer_operator"
    bl_label = "Timer Operator"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            update_landmarks()
            time.sleep(0.05)  # Add a small delay (50 milliseconds)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0 / 30.0, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

def menu_func(self, context):
    self.layout.operator(TimerOperator.bl_idname)

def register():
    bpy.utils.register_class(TimerOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(TimerOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()