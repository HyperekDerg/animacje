import bpy

def stworz_oswietlenie_nocne():
    if "Ksiezyc" in bpy.data.objects:
        obj = bpy.data.objects["Ksiezyc"]
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data.users == 0:
            bpy.data.lights.remove(data)

    light_data = bpy.data.lights.new(name="Ksiezyc_Data", type='SUN')
    ksiezyc = bpy.data.objects.new(name="Ksiezyc", object_data=light_data)
    bpy.context.scene.collection.objects.link(ksiezyc)
    

    light_data.energy = 2.5
    light_data.color = (0.65, 0.75, 1.0)
    light_data.angle = 0.1
    ksiezyc.rotation_euler = (0.85, 0, 0.6)

    if not bpy.context.scene.world:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    for node in nodes:
        if node.type in ['VOLUME_SCATTER', 'BACKGROUND']:
            nodes.remove(node)

    bg_node = nodes.new("ShaderNodeBackground")
    bg_node.inputs["Color"].default_value = (0.002, 0.002, 0.005, 1.0)
    bg_node.inputs["Strength"].default_value = 0.5

    vol_node = nodes.new("ShaderNodeVolumeScatter")
    vol_node.name = "Volume Scatter"
    vol_node.inputs["Density"].default_value = 0.015
    vol_node.inputs["Anisotropy"].default_value = 0.7
    
    output_node = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")

    links.new(bg_node.outputs["Background"], output_node.inputs["Surface"])
    links.new(vol_node.outputs["Volume"], output_node.inputs["Volume"])

def ustaw_exposure():
    bpy.context.scene.view_settings.exposure = -0.5
    
    try:
        bpy.context.scene.view_settings.look = 'AgX - High Contrast'
    except TypeError:
        bpy.context.scene.view_settings.look = 'None'
        print("Nie znaleziono profilu AgX - High Contrast, ustawiono na None.")

    if hasattr(bpy.context.scene, "eevee"):
        try:
            bpy.context.scene.eevee.use_bloom = True
        except:
            pass

if __name__ == "__main__":
    stworz_oswietlenie_nocne()
    ustaw_exposure()