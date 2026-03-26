import bpy
import bmesh
import math
import os
import random


TYPY_ROSLIN = {
    "drzewo": {
        "wysokosc": (3.5, 5.5),
        "liczba_lisci": (16, 35),
        "promien_lisci": (0.30, 0.45),
        "liczba_korzeni": (5, 13),
        "kolor_lodygi": (0.250, 0.03, 0.012),
        "kolor_lisci_pula": [(0.0009, 1, 0.84), (0.117, 0.48, 1)],
        "metallic_lodygi": 0.8,
        "roughness_lodygi": 0.2,
    },
    "krzew": {
        "wysokosc": (1.5, 2.2),
        "liczba_lisci": (5, 8),
        "promien_lisci": (0.20, 0.32),
        "liczba_korzeni": (4, 7),
        "kolor_lodygi": (0.43, 0.13, 0.109),
        "kolor_lisci_pula": [(1, 0.06, 0.059), (0.27, 0.0025, 0.058)],
        "metallic_lodygi": 0.5,
        "roughness_lodygi": 0.45,
    },
    "paproc": {
        "wysokosc": (0.5, 1.2),
        "liczba_lisci": (8, 12),
        "promien_lisci": (0.1, 0.22),
        "liczba_korzeni": (3, 5),
        "kolor_lodygi": (0.25, 0.19, 0.16),
        "kolor_lisci_pula": [(0.00, 1, 0.01), (0.435, 0.69, 0.178)],
        "metallic_lodygi": 0.3,
        "roughness_lodygi": 0.65,
    },
}

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
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
        u**3 * p0[2] + 3 * u**2 * t * p1[2] + 3 * u * t**2 * p2[2] + t**3 * p3[2],
    )


def bezier_styczna(p0, p1, p2, p3, t):
    u = 1 - t
    dx = 3 * (u**2 * (p1[0] - p0[0]) + 2 * u * t * (p2[0] - p1[0]) + t**2 * (p3[0] - p2[0]))
    dy = 3 * (u**2 * (p1[1] - p0[1]) + 2 * u * t * (p2[1] - p1[1]) + t**2 * (p3[1] - p2[1]))
    dz = 3 * (u**2 * (p1[2] - p0[2]) + 2 * u * t * (p2[2] - p1[2]) + t**2 * (p3[2] - p2[2]))
    dlugosc = math.sqrt(dx**2 + dy**2 + dz**2) or 1.0
    return (dx / dlugosc, dy / dlugosc, dz / dlugosc)


def prostopadly_uklad(styczna):
    tx, ty, tz = styczna
    pomocniczy = (1, 0, 0) if abs(tx) < 0.9 else (0, 1, 0)
    ux = ty * pomocniczy[2] - tz * pomocniczy[1]
    uy = tz * pomocniczy[0] - tx * pomocniczy[2]
    uz = tx * pomocniczy[1] - ty * pomocniczy[0]
    dl = math.sqrt(ux**2 + uy**2 + uz**2) or 1.0
    ux, uy, uz = ux / dl, uy / dl, uz / dl
    vx = ty * uz - tz * uy
    vy = tz * ux - tx * uz
    vz = tx * uy - ty * ux
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

def zbuduj_mesh_liscia(dlugosc, szerokosc, grubosc):
    mesh = bpy.data.meshes.new("MeshLisc")
    bm = bmesh.new()
    b = szerokosc / 2
    g = grubosc / 2
    t = 0.005
    v0 = bm.verts.new((0,       b,  g))
    v1 = bm.verts.new((0,      -b,  g))
    v2 = bm.verts.new((0,      -b, -g))
    v3 = bm.verts.new((0,       b, -g))
    v4 = bm.verts.new((dlugosc, t,  t))
    v5 = bm.verts.new((dlugosc,-t,  t))
    v6 = bm.verts.new((dlugosc,-t, -t))
    v7 = bm.verts.new((dlugosc, t, -t))
    for f in [
        (v0, v1, v2, v3),
        (v4, v5, v6, v7),
        (v0, v1, v5, v4),
        (v2, v3, v7, v6),
        (v1, v2, v6, v5),
        (v0, v3, v7, v4),
    ]:
        bm.faces.new(f)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def zbuduj_mesh_korzenia(kat, skala_g):
    mesh = bpy.data.meshes.new("MeshKorzen")
    bm = bmesh.new()

    dx = math.cos(kat)
    dy = math.sin(kat)
    losowa_dlugosc = random.uniform(0.5, 1.6)
    r_start = -0.01

    sekcje = [
        (dx * r_start,                  dy * r_start,                  0.00,                    0.115 * skala_g),
        (dx * 0.22 * losowa_dlugosc,    dy * 0.22 * losowa_dlugosc,   -0.06 * losowa_dlugosc,   0.075 * skala_g),
        (dx * 0.38 * losowa_dlugosc,    dy * 0.38,                    -0.22 * losowa_dlugosc,   0.050 * skala_g),
        (dx * 0.48,                      dy * 0.48 * losowa_dlugosc,   -0.42 * losowa_dlugosc,   0.028 * skala_g),
        (dx * 0.52 * losowa_dlugosc,    dy * 0.52 * losowa_dlugosc,   -0.60 * losowa_dlugosc,   0.007 * skala_g),
    ]
    sekcje_scaled = [(sx * skala_g, sy * skala_g, sz * skala_g, r) for sx, sy, sz, r in sekcje]

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

    pierscienie = [okrag_3d(bm, cx, cy, cz, r) for cx, cy, cz, r in sekcje_scaled[:-1]]
    cx, cy, cz, _ = sekcje_scaled[-1]
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

def stworz_lodyge(
    wysokosc,
    offset_x,
    offset_y=0.0,
    kolor_lodygi=(0.250, 0.0382, 0.020),
    metallic=0.8,
    roughness=0.2,
):
    zagięcie_x = random.uniform(-wysokosc * 0.45, wysokosc * 0.45)
    zagięcie_y = random.uniform(-wysokosc * 0.30, wysokosc * 0.30)

    p0 = (0.0, 0.0, 0.0)
    p1 = (0.0, 0.0, wysokosc * 0.30)
    p2 = (zagięcie_x, zagięcie_y, wysokosc * 0.70)
    p3 = (zagięcie_x * 0.7, zagięcie_y * 0.6, wysokosc)

    n_seg  = 24
    n_ring = 10
    skala_g = wysokosc / 2.2
    r_dol   = 0.12 * skala_g
    r_gora  = 0.035 * skala_g

    liczba_ciec  = random.randint(2, 4)
    pozycje_ciec = sorted(random.uniform(0.15, 0.85) for _ in range(liczba_ciec))
    ciecia_set   = {max(1, min(n_seg - 1, int(tc * n_seg))) for tc in pozycje_ciec}

    mesh = bpy.data.meshes.new("MeshLodyga")
    bm   = bmesh.new()
    pierscienie = []

    for idx, t in enumerate(i / n_seg for i in range(n_seg + 1)):
        srodek  = bezier_punkt(p0, p1, p2, p3, t)
        styczna = bezier_styczna(p0, p1, p2, p3, t)
        u_vec, v_vec = prostopadly_uklad(styczna)
        promien = r_dol + (r_gora - r_dol) * t

        if idx in ciecia_set and 0 < idx < n_seg:
            r_wciecie = promien * 0.52
            r_garb    = promien * 1.25
            r_przed   = pierscienie[-1] if pierscienie else None
            rn1 = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, promien,    n_ring)
            rw  = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, r_wciecie,  n_ring)
            rg  = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, r_garb,     n_ring)
            rn2 = pierscien_na_krzywej(bm, srodek, u_vec, v_vec, promien,    n_ring)
            if r_przed:
                polacz_pierscienie(bm, r_przed, rn1)
            polacz_pierscienie(bm, rn1, rw)
            polacz_pierscienie(bm, rw,  rg)
            polacz_pierscienie(bm, rg,  rn2)
            pierscienie.append(rn2)
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

    nazwa = f"Lodyga_{offset_x:.1f}_{offset_y:.1f}"
    obj   = bpy.data.objects.new(nazwa, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (offset_x, offset_y, 0.0)
    mat = nowy_material(f"Mat_{nazwa}", kolor_lodygi, metallic=metallic, roughness=roughness)
    obj.data.materials.append(mat)

    return obj, (p0, p1, p2, p3), r_dol, skala_g


def stworz_liscie_na_krzywej(
    wysokosc,
    liczba_lisci,
    promien_lisci,
    offset_x,
    offset_y,
    krzywa,
    kolor_lisci=(0.0, 0.55, 0.10),
):
    p0, p1, p2, p3 = krzywa
    mat = nowy_material(
        f"MatLisc_{offset_x:.1f}_{offset_y:.1f}",
        kolor_lisci,
        metallic=0.7,
        roughness=0.3,
        emisja=0.5,
    )
    obiekty = []
    for i in range(liczba_lisci):
        t     = 0.30 + (i / max(liczba_lisci - 1, 1)) * 0.60
        poz   = bezier_punkt(p0, p1, p2, p3, t)
        skala = promien_lisci * (0.6 + (1 - t) * 0.8)
        kat   = i * math.radians(137.5)
        mesh  = zbuduj_mesh_liscia(
            dlugosc=skala * 2.0,
            szerokosc=skala * 0.45,
            grubosc=skala * 0.12,
        )
        nazwa = f"Lisc_{offset_x:.1f}_{offset_y:.1f}_{i}"
        obj   = bpy.data.objects.new(nazwa, mesh)
        bpy.context.collection.objects.link(obj)
        obj.location      = (offset_x + poz[0], offset_y + poz[1], poz[2])
        obj.rotation_euler = (math.radians(40 + t * 25), 0, kat)
        obj.data.materials.append(mat)
        obiekty.append(obj)
    return obiekty


def stworz_korzenie(
    liczba_korzeni,
    offset_x,
    offset_y,
    skala_g,
    kolor_lodygi=(0.250, 0.0382, 0.020),
    metallic=0.5,
    roughness=0.65,
):
    mat = nowy_material(
        f"MatKorzen_{offset_x:.1f}_{offset_y:.1f}",
        kolor_lodygi,
        metallic=metallic,
        roughness=roughness,
    )
    obiekty = []
    for i in range(liczba_korzeni):
        kat  = (2 * math.pi / liczba_korzeni) * i
        mesh = zbuduj_mesh_korzenia(kat, skala_g)
        nazwa = f"Korzen_{offset_x:.1f}_{offset_y:.1f}_{i}"
        obj   = bpy.data.objects.new(nazwa, mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (offset_x, offset_y, 0.0)
        obj.data.materials.append(mat)
        obiekty.append(obj)
    return obiekty


def stworz_rosline(
    wysokosc=2.0,
    liczba_lisci=3,
    promien_lisci=0.3,
    liczba_korzeni=4,
    offset_x=0.0,
    offset_y=0.0,
    kolor_lodygi=(0.250, 0.0382, 0.020),
    kolor_lisci=(0.0, 0.55, 0.10),
    metallic_lodygi=0.8,
    roughness_lodygi=0.2,
):
    obj_lodyga, krzywa, r_dol, skala_g = stworz_lodyge(
        wysokosc, offset_x, offset_y,
        kolor_lodygi=kolor_lodygi,
        metallic=metallic_lodygi,
        roughness=roughness_lodygi,
    )
    obj_liscie = stworz_liscie_na_krzywej(
        wysokosc, liczba_lisci, promien_lisci,
        offset_x, offset_y, krzywa,
        kolor_lisci=kolor_lisci,
    )
    obj_korzenie = stworz_korzenie(
        liczba_korzeni, offset_x, offset_y,
        skala_g=skala_g,
        kolor_lodygi=kolor_lodygi,
        metallic=metallic_lodygi * 0.6,
        roughness=min(roughness_lodygi + 0.2, 1.0),
    )
    return [obj_lodyga] + obj_liscie + obj_korzenie


def stworz_rosline_typ(x: float, y: float, typ: str) -> list:
    p = TYPY_ROSLIN[typ]
    return stworz_rosline(
        wysokosc=random.uniform(*p["wysokosc"]),
        liczba_lisci=random.randint(*p["liczba_lisci"]),
        promien_lisci=random.uniform(*p["promien_lisci"]),
        liczba_korzeni=random.randint(*p["liczba_korzeni"]),
        offset_x=x,
        offset_y=y,
        kolor_lodygi=p["kolor_lodygi"],
        kolor_lisci=random.choice(p["kolor_lisci_pula"]),
        metallic_lodygi=p["metallic_lodygi"],
        roughness_lodygi=p["roughness_lodygi"],
    )

def wybierz_typ_biomu(x: float, y: float, rozmiar_pola: float) -> str:
    pol  = rozmiar_pola / 2
    dist = max(abs(x) / pol, abs(y) / pol)
    if dist < 0.30:
        return "drzewo"
    elif dist < 0.70:
        return "krzew" if random.random() < 0.70 else "drzewo"
    else:
        return "paproc" if random.random() < 0.60 else "krzew"


def generuj_powierzchnie(rozmiar_pola: float = 10.0) -> None:
    bpy.ops.mesh.primitive_plane_add(
        size=rozmiar_pola,
        enter_editmode=False,
        align="WORLD",
        location=(0, 0, 0),
        scale=(1, 1, 1),
    )
    powierzchnia = bpy.context.active_object
    powierzchnia.name = "Powierzchnia_Planety"

    subsurf = powierzchnia.modifiers.new(name="Subdivide", type="SUBSURF")
    subsurf.levels            = 6
    subsurf.render_levels     = 6
    subsurf.subdivision_type  = "CATMULL_CLARK"

    displace  = powierzchnia.modifiers.new(name="Displace", type="DISPLACE")
    tekstura  = bpy.data.textures.new("Szum_Terenu", type="CLOUDS")
    tekstura.noise_scale  = 3.5
    tekstura.noise_depth  = 6
    displace.texture      = tekstura
    displace.strength     = 2.7
    displace.mid_level    = 0.5

    mat = nowy_material("Mat_powierzchnia", (0.0126, 0.006, 0.002), metallic=0.1, roughness=0.25)
    powierzchnia.data.materials.append(mat)


def _link_do_kolekcji(obj, kolekcja):
    kolekcja.objects.link(obj)
    for col in list(obj.users_collection):
        if col != kolekcja:
            col.objects.unlink(obj)


def generuj_las(liczba_roslin: int = 80, rozmiar_pola: float = 10.0, seed: int = 42) -> None:
    generuj_powierzchnie(rozmiar_pola * 1.9)
    random.seed(seed)

    kol_las = bpy.data.collections.new("Las")
    bpy.context.scene.collection.children.link(kol_las)

    podkolekcje = {}
    for nazwa_typ, nazwa_kol in [("drzewo", "Drzewa"), ("krzew", "Krzewy"), ("paproc", "Paprocie")]:
        pod = bpy.data.collections.new(nazwa_kol)
        kol_las.children.link(pod)
        podkolekcje[nazwa_typ] = pod

    for _ in range(liczba_roslin):
        x   = random.uniform(-rozmiar_pola / 2, rozmiar_pola / 2)
        y   = random.uniform(-rozmiar_pola / 2, rozmiar_pola / 2)
        typ = wybierz_typ_biomu(x, y, rozmiar_pola)
        obiekty = stworz_rosline_typ(x, y, typ)
        for obj in obiekty:
            _link_do_kolekcji(obj, podkolekcje[typ])

def wyczysc_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def ustaw_oswietlenie():
    bpy.ops.object.light_add(type="SUN", location=(16.1, -14, 6.8))
    slonce = bpy.context.active_object
    slonce.data.energy     = 12.5
    slonce.rotation_euler  = (math.radians(44.7), math.radians(63.5), math.radians(26.4))
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)


def ustaw_kamere():
    bpy.ops.object.camera_add(location=(13.4, -18, 5.5))
    kamera = bpy.context.active_object
    kamera.rotation_euler = (math.radians(70), 0, math.radians(30))
    bpy.context.scene.camera = kamera
    bpy.context.object.data.lens = 25
    bpy.context.scene.eevee.taa_render_samples = 1028
    bpy.context.scene.eevee.ray_tracing_options.resolution_scale = "2"
    bpy.context.object.data.dof.use_dof = True
    bpy.context.scene.eevee.use_raytracing = True


def shade_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.shade_smooth()


def renderuj(sciezka="roslinabio.png"):
    scene = bpy.context.scene
    scene.render.engine                    = "BLENDER_EEVEE"
    scene.render.filepath                  = os.path.abspath(sciezka)
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x             = 1200
    scene.render.resolution_y             = 800
    bpy.ops.render.render(write_still=True)
    print(f"Render zapisany: {sciezka}")

wyczysc_scene()
generuj_las(145, 30.0, 9876543214206969)
shade_all()
ustaw_oswietlenie()
ustaw_kamere()
renderuj("Las05.png")