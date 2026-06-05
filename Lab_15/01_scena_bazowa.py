import bpy
import math

DLUGOSC_ULICY       = 200.0 
SZEROKOSC_JEZDNI    = 10.0
SZEROKOSC_CHODNIKA  = 3.0
WYSOKOSC_KRAWEZNIKA = 0.15
MOKROSC_ASFALTU     = 0.85
CZYSZCZ_SCENE       = True

SZEROKOSC_TERENU    = 500.0
DLUGOSC_TERENU      = 500.0
OFFSET_TERENU       = -0.005

def pobierz_lub_stworz_kolekcje(nazwa="Ulica"):
    if nazwa in bpy.data.collections:
        return bpy.data.collections[nazwa]
    kol = bpy.data.collections.new(nazwa)
    bpy.context.scene.collection.children.link(kol)
    return kol


def przenies_do_kolekcji(obj, kolekcja):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    kolekcja.objects.link(obj)

def wyczysc_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for blok in [bpy.data.meshes, bpy.data.materials,
                 bpy.data.lights, bpy.data.cameras]:
        for item in blok:
            blok.remove(item)


def obiekt_istnieje(nazwa):
    return nazwa in bpy.data.objects


def stworz_material_asfalt(nazwa="MAT_Asfalt"):
    if nazwa in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[nazwa])

    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output  = nodes.new("ShaderNodeOutputMaterial")
    pbsdf   = nodes.new("ShaderNodeBsdfPrincipled")
    tex_coord = nodes.new("ShaderNodeTexCoord")
    
    noise_puddles = nodes.new("ShaderNodeTexNoise")
    noise_puddles.inputs["Scale"].default_value = 2.5
    noise_puddles.inputs["Detail"].default_value = 10.0
    
    ramp_rough = nodes.new("ShaderNodeValToRGB")
    ramp_rough.color_ramp.elements[0].position = 0.45
    ramp_rough.color_ramp.elements[0].color = (0.02, 0.02, 0.02, 1)
    ramp_rough.color_ramp.elements[1].position = 0.65
    ramp_rough.color_ramp.elements[1].color = (0.15, 0.15, 0.15, 1)

    noise_grain = nodes.new("ShaderNodeTexNoise")
    noise_grain.inputs["Scale"].default_value = 150.0
    noise_grain.inputs["Detail"].default_value = 15.0
    
    bump_asphalt = nodes.new("ShaderNodeBump")
    bump_asphalt.inputs["Strength"].default_value = 0.1
    
    noise_rain = nodes.new("ShaderNodeTexNoise")
    noise_rain.inputs["Scale"].default_value = 500.0
    noise_rain.inputs["Detail"].default_value = 2.0
    
    bump_rain = nodes.new("ShaderNodeBump")
    bump_rain.inputs["Strength"].default_value = 0.05

    pbsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.025, 1.0)
    pbsdf.inputs["Specular IOR Level"].default_value = 0.55
    
    links.new(tex_coord.outputs["UV"], noise_puddles.inputs["Vector"])
    links.new(tex_coord.outputs["UV"], noise_grain.inputs["Vector"])
    links.new(tex_coord.outputs["UV"], noise_rain.inputs["Vector"])
    
    links.new(noise_puddles.outputs["Fac"], ramp_rough.inputs["Fac"])
    links.new(ramp_rough.outputs["Color"], pbsdf.inputs["Roughness"])
    
    links.new(noise_grain.outputs["Fac"], bump_asphalt.inputs["Height"])
    links.new(noise_rain.outputs["Fac"], bump_rain.inputs["Height"])
    links.new(bump_asphalt.outputs["Normal"], bump_rain.inputs["Normal"])
    links.new(bump_rain.outputs["Normal"], pbsdf.inputs["Normal"])
    
    links.new(pbsdf.outputs["BSDF"], output.inputs["Surface"])
    
    return mat


def stworz_material_chodnik(nazwa="MAT_Chodnik"):
    if nazwa in bpy.data.materials:
        return bpy.data.materials[nazwa]

    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    pbsdf  = nodes.new("ShaderNodeBsdfPrincipled")
    output.location = (400, 0)
    pbsdf.location  = (100, 0)

    pbsdf.inputs["Base Color"].default_value = (0.18, 0.17, 0.16, 1.0)
    pbsdf.inputs["Roughness"].default_value  = 0.92
    links.new(pbsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def stworz_material_kraweznik(nazwa="MAT_Kraweznik"):
    if nazwa in bpy.data.materials:
        return bpy.data.materials[nazwa]

    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    pbsdf  = nodes.new("ShaderNodeBsdfPrincipled")
    output.location = (400, 0)
    pbsdf.location  = (100, 0)

    pbsdf.inputs["Base Color"].default_value = (0.25, 0.24, 0.22, 1.0)
    pbsdf.inputs["Roughness"].default_value  = 0.85
    links.new(pbsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def stworz_material_teren(nazwa="MAT_Teren"):
    if nazwa in bpy.data.materials:
        return bpy.data.materials[nazwa]

    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    pbsdf  = nodes.new("ShaderNodeBsdfPrincipled")
    output.location = (400, 0)
    pbsdf.location  = (100, 0)

    pbsdf.inputs["Base Color"].default_value = (0.06, 0.05, 0.04, 1.0)
    pbsdf.inputs["Roughness"].default_value  = 0.97
    links.new(pbsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def przypisz_material(obj, material):
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def dodaj_plaszczyzne(nazwa, lokalizacja, skalowanie, material, kolekcja):
    if obiekt_istnieje(nazwa):
        print(f"  [pominięto] '{nazwa}' już istnieje.")
        return bpy.data.objects[nazwa]

    bpy.ops.mesh.primitive_plane_add(location=lokalizacja)
    obj = bpy.context.active_object
    obj.name = nazwa
    obj.scale = skalowanie
    bpy.ops.object.transform_apply(scale=True)
    przypisz_material(obj, material)
    przenies_do_kolekcji(obj, kolekcja)
    return obj


def stworz_kraweznik(strona, material, kolekcja):
    litera = 'P' if strona > 0 else 'L'
    nazwa  = f"Kraweznik_{litera}"

    if obiekt_istnieje(nazwa):
        print(f"  [pominięto] '{nazwa}' już istnieje.")
        return bpy.data.objects[nazwa]

    szerokosc_kraweznika = 0.12

    x_krawedz_jezdni = strona * (SZEROKOSC_JEZDNI / 2)
    x_srodek = x_krawedz_jezdni + strona * (szerokosc_kraweznika / 2)

    bpy.ops.mesh.primitive_cube_add(
        location=(x_srodek, 0, WYSOKOSC_KRAWEZNIKA / 2)
    )
    obj = bpy.context.active_object
    obj.name = nazwa

    obj.scale = (szerokosc_kraweznika / 2,
                 DLUGOSC_ULICY / 2,
                 WYSOKOSC_KRAWEZNIKA / 2)
    bpy.ops.object.transform_apply(scale=True)

    przypisz_material(obj, material)
    przenies_do_kolekcji(obj, kolekcja)
    return obj



def stworz_teren(material, kolekcja):
    nazwa = "Teren"
    if obiekt_istnieje(nazwa):
        print(f"  [pominięto] '{nazwa}' już istnieje.")
        return bpy.data.objects[nazwa]

    bpy.ops.mesh.primitive_plane_add(location=(0, 0, OFFSET_TERENU))
    obj = bpy.context.active_object
    obj.name = nazwa
    obj.scale = (SZEROKOSC_TERENU / 2, DLUGOSC_TERENU / 2, 1)
    bpy.ops.object.transform_apply(scale=True)
    przypisz_material(obj, material)
    przenies_do_kolekcji(obj, kolekcja)
    return obj


def ustaw_swiat_nocny():
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    bg  = nodes.new("ShaderNodeBackground")
    out = nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Color"].default_value    = (0.005, 0.005, 0.01, 1.0)
    bg.inputs["Strength"].default_value = 0.3
    links.new(bg.outputs["Background"], out.inputs["Surface"])

def main():
    if CZYSZCZ_SCENE:
        wyczysc_scene()

    kol_ulica = pobierz_lub_stworz_kolekcje("Ulica")
    mat_asfalt    = stworz_material_asfalt()
    mat_chodnik   = stworz_material_chodnik()
    mat_kraweznik = stworz_material_kraweznik()
    mat_teren     = stworz_material_teren()

    pol          = DLUGOSC_ULICY / 2
    pol_jezdni   = SZEROKOSC_JEZDNI / 2
    pol_chodnika = SZEROKOSC_CHODNIKA / 2

    stworz_teren(mat_teren, kol_ulica)
    dodaj_plaszczyzne(
        "Jezdnia",
        lokalizacja=(0, 0, 0),
        skalowanie=(pol_jezdni, pol, 1),
        material=mat_asfalt,
        kolekcja=kol_ulica,
    )

    for strona, litera in [(+1, "P"), (-1, "L")]:
        x_chodnik = strona * (pol_jezdni + pol_chodnika)
        dodaj_plaszczyzne(
            f"Chodnik_{litera}",
            lokalizacja=(x_chodnik, 0, WYSOKOSC_KRAWEZNIKA),
            skalowanie=(pol_chodnika, pol, 1),
            material=mat_chodnik,
            kolekcja=kol_ulica,
        )
        stworz_kraweznik(strona, mat_kraweznik, kol_ulica)
    ustaw_swiat_nocny()

if __name__ == "__main__":
    main()