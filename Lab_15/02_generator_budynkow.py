import bpy
import random
import math
import sys
import os

dir_path = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else ""
if dir_path and dir_path not in sys.path:
    sys.path.append(dir_path)

try:
    import assets_miejskie as assets
except ImportError:
    print("Nie znaleziono pliku 'assets_miejskie.py' w katalogu projektu!")


SEED_LOSOWOSCI        = 554
LICZBA_BUDYNKOW       = 10
MIN_SZEROKOSC_BUD    = 2.0
MAX_SZEROKOSC_BUD    = 12.0
MIN_WYSOKOSC_BUD     = 5.0
MAX_WYSOKOSC_BUD     = 25.0
ODLEGLOSC_OD_ULICY   = 12.0
PRZERWY_MIEDZY_BUD   = 5.2
GLEBOKOSC_BUDYNKU    = 5.0

random.seed(SEED_LOSOWOSCI)

KOLORY_ELEWACJI = [
    (0.08, 0.07, 0.10, 1.0),
    (0.06, 0.08, 0.10, 1.0),
    (0.10, 0.08, 0.06, 1.0),
    (0.05, 0.05, 0.05, 1.0),
    (0.12, 0.10, 0.08, 1.0),
]


def wyczysc_stara_kolekcje(nazwa_kolekcji):
    if nazwa_kolekcji in bpy.data.collections:
        kolekcja = bpy.data.collections[nazwa_kolekcji]
        
        for obj in list(kolekcja.objects):
            for slot in obj.material_slots:
                if slot.material:
                    if slot.material.name.startswith("MAT_Elev_"):
                        bpy.data.materials.remove(slot.material)
            
            if obj.type == 'LIGHT':
                bpy.data.lights.remove(obj.data)
            else:
                bpy.data.objects.remove(obj)
                
        bpy.data.collections.remove(kolekcja)


def stworz_material_elewacji(kolor, nazwa):
    mat = bpy.data.materials.new(name=nazwa)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    pbsdf  = nodes.new("ShaderNodeBsdfPrincipled")
    output.location = (400, 0)
    pbsdf.location  = (100, 0)

    pbsdf.inputs["Base Color"].default_value = kolor
    pbsdf.inputs["Roughness"].default_value  = random.uniform(0.6, 0.9)
    pbsdf.inputs["Metallic"].default_value   = random.uniform(0.0, 0.15)

    links.new(pbsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat


def stworz_budynek(nazwa, lokacja_y, szerokosc, wysokosc, strona, kolor):
    x_pos = strona * (ODLEGLOSC_OD_ULICY + GLEBOKOSC_BUDYNKU / 2)

    bpy.ops.mesh.primitive_cube_add(
        location=(x_pos, lokacja_y, wysokosc / 2)
    )
    obj = bpy.context.active_object
    obj.name = nazwa
    obj.scale = (GLEBOKOSC_BUDYNKU / 2, szerokosc / 2, wysokosc / 2)
    bpy.ops.object.transform_apply(scale=True)

    mat = stworz_material_elewacji(kolor, f"MAT_Elev_{nazwa}")
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return obj


def generuj_korytarz_budynkow():
    wyczysc_stara_kolekcje("Budynki")
    wyczysc_stara_kolekcje("Infrastruktura_Miejska")

    kol_budynki = bpy.data.collections.new("Budynki")
    bpy.context.scene.collection.children.link(kol_budynki)
    
    kol_infra = bpy.data.collections.new("Infrastruktura_Miejska")
    bpy.context.scene.collection.children.link(kol_infra)

    start_y = -35.0
    licznik = 0

    for strona, litera in [(+1, "P"), (-1, "L")]:
        y_kursor = start_y
        for i in range(LICZBA_BUDYNKOW):
            szerokosc = random.uniform(MIN_SZEROKOSC_BUD, MAX_SZEROKOSC_BUD)
            wysokosc  = random.uniform(MIN_WYSOKOSC_BUD, MAX_WYSOKOSC_BUD)
            kolor     = random.choice(KOLORY_ELEWACJI)
            nazwa     = f"Budynek_{litera}_{i+1:02d}"

            srodek_y  = y_kursor + szerokosc / 2
            bud = stworz_budynek(nazwa, srodek_y, szerokosc, wysokosc, strona, kolor)

            for col in bud.users_collection:
                col.objects.unlink(bud)
            kol_budynki.objects.link(bud)
            x_chodnika = strona * (ODLEGLOSC_OD_ULICY - 4.0)
            
            if i % 2 == 0 and 'assets' in globals():
                assets.zbuduj_latarnie(x_chodnika, srodek_y, strona, kol_infra)
            
            if i < LICZBA_BUDYNKOW - 1 and 'assets' in globals():
                srodek_przerwy_y = y_kursor + szerokosc + (PRZERWY_MIEDZY_BUD / 2)
                x_lawki = strona * (ODLEGLOSC_OD_ULICY - 1.5)
                assets.zbuduj_lawke(x_lawki, srodek_przerwy_y, strona, kol_infra)

            y_kursor += szerokosc + PRZERWY_MIEDZY_BUD
            licznik  += 1

    return licznik


def main():
    n = generuj_korytarz_budynkow()
    print(f"Wygenerowano {n} budynków wraz z infrastrukturą towarzyszącą.")


if __name__ == "__main__":
    main()