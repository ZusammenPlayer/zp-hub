

def get_scene(project, scene_id):
    scene = None
    for s in project['scenes']:
        if s['id'] == scene_id:
            scene = s
    return scene
            

def get_devices(connected_devices, project, virtual_device_id):
    devices = []
    virtual_device = None
    for vd in project['virtual_devices']:
        if vd['id'] == virtual_device_id:
            virtual_device = vd
    
    if virtual_device is None:
        return devices
    
    for d in virtual_device['device_ids']:
        for cd in connected_devices:
            if cd['uid'] == d:
                device = {'uid': d, 'sid': cd['sid']}
                devices.append(device)
    return devices
    