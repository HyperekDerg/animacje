import bpy
import math

def _pobierz_lub_stworz_material(nazwa, typ_bazy, kolor, roughness=0.5, metallic=0.0):
    if nazwa in bpy.data.materials:
        return bpy.data.materials[nazwa]
        
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new("ShaderNodeOutputMaterial")
    
    if typ_bazy == 'EMISSION':
        node_shader = nodes.new("ShaderNodeEmission")
        node_shader.inputs["Color"].default_value = kolor
        node_shader.inputs["Strength"].default_value = 25.0
        mat.node_tree.links.new(node_shader.outputs["Emission"], out.inputs["Surface"])
    else:
        node_shader = nodes.new("ShaderNodeBsdfPrincipled")
        node_shader.inputs["Base Color"].default_value = kolor
        node_shader.inputs["Roughness"].default_value = roughness
        node_shader.inputs["Metallic"].default_value = metallic
        mat.node_tree.links.new(node_shader.outputs["BSDF"], out.inputs["Surface"])
        
    return mat


def zbuduj_latarnie(x, y, strona, kolekcja_cel):
    mat_metal = _pobierz_lub_stworz_material("MAT_Asset_Lampa_Metal", "PRINCIPLED", (0.05, 0.05, 0.05, 1.0), roughness=0.3, metallic=0.9)
    mat_zarowka = _pobierz_lub_stworz_material("MAT_Asset_Lampa_Zarowka", "EMISSION", (1.0, 0.75, 0.4, 1.0))

    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=5.5, location=(0, 0, 0))
    slup = bpy.context.active_object
    slup.name = f"Latarnia_Slup_{y:.1f}"
    bpy.ops.object.transform_apply(scale=True)
    slup.data.materials.append(mat_metal)
    slup.location = (x, y, 2.75)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.6, location=(0, 0, 0))
    ramiona = bpy.context.active_object
    ramiona.name = f"Latarnia_Ramiona_{y:.1f}"
    ramiona.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    ramiona.data.materials.append(mat_metal)
    ramiona.location = (x - strona * 0.4, y, 5.3)
    
    for obj in [slup, ramiona]:
        kolekcja_cel.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
    
    for offset_x in [-0.7, 0.7]:
        pos_x = (x - strona * 0.4) + offset_x
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(pos_x, y, 5.15))
        klosz = bpy.context.active_object
        klosz.name = f"Latarnia_Klosz_{y:.1f}_{'A' if offset_x < 0 else 'B'}"
        klosz.data.materials.append(mat_zarowka)
        
        kolekcja_cel.objects.link(klosz)
        bpy.context.scene.collection.objects.unlink(klosz)

        bpy.ops.object.light_add(type='POINT', location=(pos_x, y, 4.9))
        swiatlo = bpy.context.active_object
        swiatlo.name = f"Swiatlo_Fizyczne_{y:.1f}_{'A' if offset_x < 0 else 'B'}"
        swiatlo.data.color = (1.0, 0.78, 0.45)
        swiatlo.data.energy = 180.0
        swiatlo.data.shadow_soft_size = 0.4
        
        kolekcja_cel.objects.link(swiatlo)
        bpy.context.scene.collection.objects.unlink(swiatlo)


def zbuduj_lawke(x, y, strona, kolekcja_cel):
    mat_metal = _pobierz_lub_stworz_material("MAT_Asset_Lawka_Żeliwo", "PRINCIPLED", (0.04, 0.05, 0.04, 1.0), roughness=0.4, metallic=0.8)
    mat_drewno = _pobierz_lub_stworz_material("MAT_Asset_Lawka_Drewno", "PRINCIPLED", (0.16, 0.09, 0.05, 1.0), roughness=0.6)

    obiekty_lawki = []
    kat_obrotu = 0 if strona == 1 else math.radians(180)

    for offset_y in [-0.8, 0.8]:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        noga = bpy.context.active_object
        noga.name = f"Lawka_Noga_{y:.1f}"
        noga.scale = (0.3, 0.04, 0.25)
        bpy.ops.object.transform_apply(scale=True)
        noga.data.materials.append(mat_metal)
        
        noga.rotation_euler = (0, 0, kat_obrotu)
        noga.location = (x, y + offset_y, 0.25)
        obiekty_lawki.append(noga)

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    siedzisko = bpy.context.active_object
    siedzisko.name = f"Lawka_Siedzisko_{y:.1f}"
    siedzisko.scale = (0.28, 0.9, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    siedzisko.data.materials.append(mat_drewno)
    
    siedzisko.rotation_euler = (0, 0, kat_obrotu)
    siedzisko.location = (x, y, 0.45)
    obiekty_lawki.append(siedzisko)

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    oparcie = bpy.context.active_object
    oparcie.name = f"Lawka_Oparcie_{y:.1f}"
    oparcie.scale = (0.03, 0.9, 0.2)
    bpy.ops.object.transform_apply(scale=True)
    oparcie.data.materials.append(mat_drewno)
    
    oparcie.rotation_euler = (0, 0, kat_obrotu)
    oparcie.location = (x + strona * 0.26, y, 0.75)
    obiekty_lawki.append(oparcie)
    
    for obj in obiekty_lawki:
        kolekcja_cel.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)