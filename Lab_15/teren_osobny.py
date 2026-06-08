import bpy

SZEROKOSC_TERENU = 200.0
DLUGOSC_TERENU   = 200.0
OFFSET_TERENU    = -0.1
NAZWA_KOLEKCJI   = "Teren"

def obiekt_istnieje(nazwa):
    return nazwa in bpy.data.objects

def pobierz_lub_stworz_kolekcje(nazwa):
    if nazwa in bpy.data.collections:
        return bpy.data.collections[nazwa]
    kol = bpy.data.collections.new(nazwa)
    bpy.context.scene.collection.children.link(kol)
    return kol

def przenies_do_kolekcji(obj, kolekcja):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    kolekcja.objects.link(obj)

def przypisz_material(obj, material):
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

def stworz_material_terenu(nazwa="MAT_Teren"):
    if nazwa in bpy.data.materials:
        return bpy.data.materials[nazwa]

    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nt    = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out      = nodes.new("ShaderNodeOutputMaterial")
    bsdf     = nodes.new("ShaderNodeBsdfPrincipled")

    out.location  = (400, 0)
    bsdf.location = (0,   0)

    bsdf.inputs["Base Color"].default_value  = (0.35, 0.32, 0.28, 1.0)
    bsdf.inputs["Roughness"].default_value   = 0.85
    bsdf.inputs["Metallic"].default_value    = 0.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.08

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def stworz_teren(material, kolekcja):
    nazwa = "Teren"
    if obiekt_istnieje(nazwa):
        print(f"  [pominięto] '{nazwa}' już istnieje.")
        return bpy.data.objects[nazwa]

    bpy.ops.mesh.primitive_plane_add(location=(0, 0, OFFSET_TERENU))
    obj = bpy.context.active_object
    obj.name = nazwa
    obj.scale = (SZEROKOSC_TERENU / 2, DLUGOSC_TERENU / 2, 1)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.transform_apply(scale=True)

    przypisz_material(obj, material)
    przenies_do_kolekcji(obj, kolekcja)
    return obj

def main():
    kol = pobierz_lub_stworz_kolekcje(NAZWA_KOLEKCJI)
    mat = stworz_material_terenu()
    stworz_teren(mat, kol)
    bpy.context.view_layer.update()

if __name__ == "__main__":
    main()