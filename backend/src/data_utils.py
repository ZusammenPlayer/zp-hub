import copy

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

def files_for_device(project, device_id):
    file_names = []
    for cuelist in project["cuelists"]:
        for cue in cuelist["cues"]:
            for mapping in cue["mappings"]:
                virtual_device = next((v for v in project["virtual_devices"] if v["id"] == mapping["virtual_device_id"]), None)
                scene = next((s for s in project["scenes"] if s["id"] == mapping["scene_id"]), None)
                if virtual_device is not None and scene is not None:
                    if device_id in virtual_device["device_ids"]:
                        if "instructions" in scene:
                            instructions = scene["instructions"].split(" ")
                            cmd = instructions[0]
                            if cmd == "play" or cmd == "show" or cmd == "playVid" or cmd == "playVidLoop" or cmd == "preloadFile":
                                file_names.append(instructions[1])
    files = []
    for m in project["media"]:
        if m["filename"] in file_names:
            file = copy.deepcopy(m)
            del file["file_path"]
            files.append(file)
    return files

def devices_for_project(project):
    device_ids = []
    for cuelist in project["cuelists"]:
        for cue in cuelist["cues"]:
            for mapping in cue["mappings"]:
                virtual_device = next((v for v in project["virtual_devices"] if v["id"] == mapping["virtual_device_id"]), None)
                scene = next((s for s in project["scenes"] if s["id"] == mapping["scene_id"]), None)
                if virtual_device is not None and scene is not None:
                    device_ids.append(virtual_device["device_ids"])

    # flatten list of list of device ids
    device_ids = [item for row in device_ids for item in row]

    return list(set(device_ids))
