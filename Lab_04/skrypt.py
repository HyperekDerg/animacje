import bpy
import bmesh
import math
import os
import random


def wyczysc_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def nowy_material(nazwa, kolor, metallic=0.0, roughness=0.5, emisja=0.0):
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*kolor, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emisja > 0.0:
        bsdf.inputs["Emission Strength"].default_value = emisja
        bsdf.inputs["Emission Color"].default_value = (*kolor, 1.0)
    return mat


def bezier_punkt(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        u**3 * p0[0] + 3*u**2*t * p1[0] + 3*u*t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3*u**2*t * p1[1] + 3*u*t**2 * p2[1] + t**3 * p3[1],
        u**3 * p0[2] + 3*u**2*t * p1[2] + 3*u*t**2 * p2[2] + t**3 * p3[2],
    )

def bezier_styczna(p0, p1, p2, p3, t):
    u = 1 - t
    dx = 3*(u**2*(p1[0]-p0[0]) + 2*u*t*(p2[0]-p1[0]) + t**2*(p3[0]-p2[0]))
    dy = 3*(u**2*(p1[1]-p0[1]) + 2*u*t*(p2[1]-p1[1]) + t**2*(p3[1]-p2[1]))
    dz = 3*(u**2*(p1[2]-p0[2]) + 2*u*t*(p2[2]-p1[2]) + t**2*(p3[2]-p2[2]))
    dlugosc = math.sqrt(dx**2 + dy**2 + dz**2) or 1.0
    return (dx/dlugosc, dy/dlugosc, dz/dlugosc)


def prostopadly_uklad(styczna):
    tx, ty, tz = styczna
    if abs(tx) < 0.9:
        pomocniczy = (1, 0, 0)
    else:
        pomocniczy = (0, 1, 0)
    ux = ty * pomocniczy[2] - tz * pomocniczy[1]
    uy = tz * pomocniczy[0] - tx * pomocniczy[2]
    uz = tx * pomocniczy[1] - ty * pomocniczy[0]
    dl = math.sqrt(ux**2 + uy**2 + uz**2) or 1.0
    ux, uy, uz = ux/dl, uy/dl, uz/dl
    vx = ty*uz - tz*uy
    vy = tz*ux - tx*uz
    vz = tx*uy - ty*ux
    return (ux, uy, uz), (vx, vy, vz)


def pierscien_na_krzywej(bm, srodek, u_vec, v_vec, promien, n=8):
    verts = []
    for i in range(n):
        a = (2 * math.pi / n) * i
        c = math.cos(a) * promien
        s = math.sin(a) * promien
        x = srodek[0] + c * u_vec[0] + s * v_vec[0]
        y = srodek[1] + c * u_vec[1] + s * v_vec[1]
        z = srodek[2] + c * u_vec[2] + s * v_vec[2]
        verts.append(bm.verts.new((x, y, z)))
    return verts


def polacz_pierscienie(bm, ring_a, ring_b):
    n = len(ring_a)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ring_a[i], ring_a[j], ring_b[j], ring_b[i]])


def stworz_lodyge(wysokosc, offset_x, seed=None):
    if seed is not None:
        random.seed(seed)

    zagięcie_x = random.uniform(-wysokosc * 0.45, wysokosc * 0.45)
    zagięcie_y = random.uniform(-wysokosc * 0.30, wysokosc * 0.30)

    p0 = (0.0,  0.0,  0.0)
    p1 = (0.0,          0.0,          wysokosc * 0.30)
    p2 = (zagięcie_x,   zagięcie_y,   wysokosc * 0.70)
    p3 = (zagięcie_x * 0.7, zagięcie_y * 0.6, wysokosc)

    n_seg = 24
    n_ring = 10
    r_dol = 0.12
    r_gora = 0.035

    liczba_ciec = random.randint(2, 4)
    pozycje_ciec = sorted(random.uniform(0.15, 0.85) for _ in range(liczba_ciec))
    ciecia_set = set()
    for tc in pozycje_ciec:
        idx = int(tc * n_seg)
        ciecia_set.add(max(1, min(n_seg - 1, idx)))

    mesh = bpy.data.meshes.new("MeshLodyga")
    bm = bmesh.new()

    pierscienie = []
    t_values = [i / n_seg for i in range(n_seg + 1)]

    for idx, t in enumerate(t_values):
        srodek = bezier_punkt(p0, p1, p2, p3, t)
        styczna = bezier_styczna(p0, p1, p2, p3, t)
        u_vec, v_vec = prostopadly_uklad(styczna)
        promien = r_dol + (r_gora - r_dol) * t

        if idx in ciecia_set and 0 < idx < len(t_values) - 1:
            r_wciecie = promien * 0.52
            r_garb    = promien * 1.25

            r_przed = pierscienie[-1] if pierscienie else None
            ring_normal_1 = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, promien, n_ring)
            ring_wciecie  = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, r_wciecie, n_ring)
            ring_garb     = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, r_garb,    n_ring)
            ring_normal_2 = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, promien,   n_ring)

            if r_przed:
                polacz_pierscienie(bm, r_przed,      ring_normal_1)
            polacz_pierscienie(bm, ring_normal_1, ring_wciecie)
            polacz_pierscienie(bm, ring_wciecie,  ring_garb)
            polacz_pierscienie(bm, ring_garb,     ring_normal_2)

            pierscienie.append(ring_normal_2)
        else:
            ring = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, promien, n_ring)
            if pierscienie:
                polacz_pierscienie(bm, pierscienie[-1], ring)
            pierscienie.append(ring)

    bm.faces.new(pierscienie[0])
    bm.faces.new(list(reversed(pierscienie[-1])))

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(f"Lodyga_{offset_x}", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (offset_x, 0, 0)

    mat = nowy_material(f"MatLodyga_{offset_x}", (0.250, 0.0382, 0.020), metallic=0.8, roughness=0.2)
    obj.data.materials.append(mat)

    return obj, (p0, p1, p2, p3)


def zbuduj_mesh_liscia(dlugosc, szerokosc, grubosc):
    mesh = bpy.data.meshes.new("MeshLisc")
    bm = bmesh.new()
    b = szerokosc / 2
    g = grubosc / 2
    t = 0.005
    v0 = bm.verts.new((0,  b,  g))
    v1 = bm.verts.new((0, -b,  g))
    v2 = bm.verts.new((0, -b, -g))
    v3 = bm.verts.new((0,  b, -g))
    v4 = bm.verts.new((dlugosc,  t,  t))
    v5 = bm.verts.new((dlugosc, -t,  t))
    v6 = bm.verts.new((dlugosc, -t, -t))
    v7 = bm.verts.new((dlugosc,  t, -t))
    for f in [(v0,v1,v2,v3),(v4,v5,v6,v7),(v0,v1,v5,v4),(v2,v3,v7,v6),(v1,v2,v6,v5),(v0,v3,v7,v4)]:
        bm.faces.new(f)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def zbuduj_mesh_korzenia(kat):
    mesh = bpy.data.meshes.new("MeshKorzen")
    bm = bmesh.new()

    dx = math.cos(kat)
    dy = math.sin(kat)
    
    skala = random.uniform(0.5, 1.6)

    sekcje = [
        (dx * 0.10, dy * 0.10 ,  0.00, 0.055),
        (dx * 0.22 * skala, dy * 0.22 * skala, -0.06 * skala,  0.042),
        (dx * 0.38 * skala, dy * 0.38 , -0.22 * skala,  0.028),
        (dx * 0.48, dy * 0.48 * skala, -0.42 * skala,  0.016),
        (dx * 0.52 * skala, dy * 0.52 * skala, -0.60 * skala,  0.004),
    ]

    kierunek_korzenia = (dx, dy, -0.5)
    dl = math.sqrt(sum(c**2 for c in kierunek_korzenia)) or 1.0
    kierunek_korzenia = tuple(c / dl for c in kierunek_korzenia)
    uk, vk = prostopadly_uklad(kierunek_korzenia)

    n = 6

    def okrag_3d(bm, cx, cy, cz, r):
        verts = []
        for i in range(n):
            a = (2 * math.pi / n) * i
            x = cx + (math.cos(a) * uk[0] + math.sin(a) * vk[0]) * r
            y = cy + (math.cos(a) * uk[1] + math.sin(a) * vk[1]) * r
            z = cz + (math.cos(a) * uk[2] + math.sin(a) * vk[2]) * r
            verts.append(bm.verts.new((x, y, z)))
        return verts

    def polacz(bm, ring_a, ring_b):
        nn = len(ring_a)
        for i in range(nn):
            j = (i + 1) % nn
            bm.faces.new([ring_a[i], ring_a[j], ring_b[j], ring_b[i]])

    pierscienie = []
    for (cx, cy, cz, r) in sekcje[:-1]:
        pierscienie.append(okrag_3d(bm, cx, cy, cz, r))

    cx, cy, cz, _ = sekcje[-1]
    czubek = bm.verts.new((cx, cy, cz))

    for i in range(len(pierscienie) - 1):
        polacz(bm, pierscienie[i], pierscienie[i + 1])

    ostatni = pierscienie[-1]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ostatni[i], ostatni[j], czubek])

    bm.faces.new(pierscienie[0])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def stworz_liscie_na_krzywej(wysokosc, liczba_lisci, promien_lisci, offset_x, krzywa):
    p0, p1, p2, p3 = krzywa
    colors_list = [(0.0, 0.871, 1), (0.342, 1, 0.203)]
    mat = nowy_material(f"MatLisc_{offset_x}", random.choice(colors_list), metallic=0.7, roughness=0.3, emisja=0.5)
    for i in range(liczba_lisci):
        t = 0.30 + (i / max(liczba_lisci - 1, 1)) * 0.60
        poz = bezier_punkt(p0, p1, p2, p3, t)
        styczna = bezier_styczna(p0, p1, p2, p3, t)
        skala = promien_lisci * (0.6 + (1 - t) * 0.8)
        kat = i * math.radians(137.5)
        mesh = zbuduj_mesh_liscia(
            dlugosc=skala * 2.0,
            szerokosc=skala * 0.45,
            grubosc=skala * 0.12
        )
        obj = bpy.data.objects.new(f"Lisc_{offset_x}_{i}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (offset_x + poz[0], poz[1], poz[2])
        pitch = math.radians(40 + t * 25)
        obj.rotation_euler = (pitch, 0, kat)
        obj.data.materials.append(mat)


def stworz_korzenie(liczba_korzeni, offset_x):
    mat = nowy_material(f"MatKorzen_{offset_x}", (0.250, 0.0382, 0.020), metallic=0.5, roughness=0.65)
    for i in range(liczba_korzeni):
        kat = (2 * math.pi / liczba_korzeni) * i
        mesh = zbuduj_mesh_korzenia(kat)
        obj = bpy.data.objects.new(f"Korzen_{offset_x}_{i}", mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (offset_x, 0, 0.05)
        obj.data.materials.append(mat)


def stworz_rosline(wysokosc=2.0, liczba_lisci=3, promien_lisci=0.3,
                   liczba_korzeni=4, offset_x=0.0):
    _, krzywa = stworz_lodyge(wysokosc, offset_x, seed=random.seed())
    stworz_liscie_na_krzywej(wysokosc, liczba_lisci, promien_lisci, offset_x, krzywa)
    stworz_korzenie(liczba_korzeni, offset_x)


def ustaw_oswietlenie():
    bpy.ops.object.light_add(type='SUN', location=(4.3, -7, 7.5))
    slonce = bpy.context.active_object
    slonce.data.energy = 6.0
    slonce.rotation_euler = (math.radians(55), 0, math.radians(18))
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

def ustaw_kamere():
    bpy.ops.object.camera_add(location=(0.4, -15, 4.8))
    kamera = bpy.context.active_object
    kamera.rotation_euler = (math.radians(80), 0, 0)
    bpy.context.scene.camera = kamera
    bpy.context.scene.eevee.taa_render_samples = 1024
    bpy.context.scene.eevee.use_raytracing = True



def renderuj(sciezka="roslinabio.png"):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.filepath = os.path.abspath(sciezka)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    bpy.ops.render.render(write_still=True)
    print(f"Render zapisany: {sciezka}")

def shade_all():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.shade_smooth()

wyczysc_scene()

stworz_rosline(wysokosc=1.2, liczba_lisci=4, promien_lisci=0.18, liczba_korzeni=3, offset_x=-3.5)
stworz_rosline(wysokosc=2.2, liczba_lisci=6, promien_lisci=0.26, liczba_korzeni=4, offset_x=0.0)
stworz_rosline(wysokosc=3.5, liczba_lisci=8, promien_lisci=0.36, liczba_korzeni=6, offset_x=3.5)

ustaw_oswietlenie()
ustaw_kamere()
shade_all()
renderuj("roslinabio.png")