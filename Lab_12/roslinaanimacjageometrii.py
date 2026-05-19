import bpy
import math
import os

SCIEZKA_LAB07 = r"C:/Users/hyper/Desktop/animacje/Lab_07/lab07.blend"
NAZWA_KOLEKCJI = "Roslina_Hero"
KLATKA_START = 1
KLATKA_KONIEC = 125
FPS = 25

def importuj_rosline(sciezka_blend, nazwa_kolekcji):
    sciezka_kolekcji = os.path.join(sciezka_blend, "Collection", nazwa_kolekcji)
    bpy.ops.wm.append(
        filepath=sciezka_kolekcji,
        directory=os.path.join(sciezka_blend, "Collection"),
        filename=nazwa_kolekcji,
    )

def animuj_lisc(obj, faza, czestosc=0.05, amplituda=0.3, klatka_start=1, klatka_koniec=125):
    wyczysc_animacje(obj)
    rotacja_bazowa_y = obj.rotation_euler[1]
    for klatka in range(klatka_start, klatka_koniec + 1):
        kat = rotacja_bazowa_y + amplituda * math.sin(klatka * czestosc + faza)
        obj.rotation_euler[1] = kat
        obj.keyframe_insert(data_path="rotation_euler", frame=klatka, index=1)

def wyczysc_animacje(obj):
    if obj.animation_data and obj.animation_data.action:
        obj.animation_data.action = None

def animuj_wszystkie_liscie(prefix_nazwy="Roslina_Lisc"):
    liscie = [obj for obj in bpy.data.objects if obj.name.startswith(prefix_nazwy)]
    for i, lisc in enumerate(liscie):
        faza_lisc = i * (2 * math.pi / max(len(liscie), 1))
        animuj_lisc(lisc, faza=faza_lisc)
    print(f"Zaanimowano {len(liscie)} liści.")

def animuj_pak(nazwa_obj="Roslina_Pak", klatka_start=30, klatka_koniec=90,
               skala_min=0.001, skala_max=0.055):
    obj = bpy.data.objects.get(nazwa_obj)
    if obj is None:
        print(f"Obiekt '{nazwa_obj}' nie istnieje. Pomijam animację pąka.")
        print(f"Dostępne obiekty: {[o.name for o in bpy.data.objects]}")
        return
    wyczysc_animacje(obj)
    obj.scale = (skala_min, skala_min, skala_min)
    obj.keyframe_insert(data_path="scale", frame=KLATKA_START)
    obj.keyframe_insert(data_path="scale", frame=klatka_start)
    obj.scale = (skala_max, skala_max, skala_max)
    obj.keyframe_insert(data_path="scale", frame=klatka_koniec)
    obj.keyframe_insert(data_path="scale", frame=KLATKA_KONIEC)


def usun_istniejace(nazwy):
    """Usuwa obiekty o podanych nazwach, jeśli istnieją (idempotencja)."""
    for nazwa in nazwy:
        obj = bpy.data.objects.get(nazwa)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)


def dodaj_swiatla():
    usun_istniejace(["Key_Light", "Fill_Light", "Rim_Light"])

    bpy.ops.object.light_add(type='SUN', location=(4.0, -3.0, 6.0))
    key = bpy.context.object
    key.name = "Key_Light"
    key.data.energy = 3.0
    key.data.color = (1.0, 0.95, 0.75)
    key.rotation_euler = (math.radians(55), math.radians(0), math.radians(35))

    bpy.ops.object.light_add(type='AREA', location=(-5.0, -2.0, 3.0))
    fill = bpy.context.object
    fill.name = "Fill_Light"
    fill.data.energy = 200.0
    fill.data.size = 4.0 
    fill.data.color = (0.75, 0.90, 1.0)
    fill.rotation_euler = (math.radians(74), math.radians(3), math.radians(-44))

    bpy.ops.object.light_add(type='SPOT', location=(0.0, 5.0, 4.0))
    rim = bpy.context.object
    rim.name = "Rim_Light"
    rim.data.energy = 400.0
    rim.data.spot_size = math.radians(45)
    rim.data.spot_blend = 0.3
    rim.data.color = (0.9, 1.0, 0.85)
    rim.rotation_euler = (math.radians(-120), math.radians(172), math.radians(-30))

    print("Dodano 3 światła: Key_Light, Fill_Light, Rim_Light.")

def dodaj_kamere():
    import mathutils

    usun_istniejace(["Kamera_Roslina"])

    lokacja = mathutils.Vector((-0.77, -0.15, 2.1))
    cel     = mathutils.Vector((-2.05, 0.93, 2.1 ))

    bpy.ops.object.camera_add(location=lokacja)
    cam_obj = bpy.context.object
    cam_obj.name = "Kamera_Roslina"

    kierunek = cel - lokacja
    rot_quat = kierunek.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    cam = cam_obj.data
    cam.lens = 50
    cam.clip_start = 0.1
    cam.clip_end = 100.0

    bpy.context.scene.camera = cam_obj
    print("Dodano kamerę 'Kamera_Roslina' i ustawiono jako aktywną.")


def ustaw_scene():
    bpy.context.scene.frame_start = KLATKA_START
    bpy.context.scene.frame_end = KLATKA_KONIEC
    bpy.context.scene.render.fps = FPS
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.eevee.taa_render_samples = 512
    bpy.context.scene.eevee.use_raytracing = True
    bpy.context.scene.render.image_settings.media_type = 'VIDEO'
    bpy.context.scene.render.ffmpeg.codec = 'MPEG4'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'


if __name__ == "__main__" or True:
    ustaw_scene()
    if "Roslina_Hero" not in bpy.data.collections:
        importuj_rosline(SCIEZKA_LAB07, NAZWA_KOLEKCJI)
    animuj_wszystkie_liscie()
    animuj_pak()
    dodaj_swiatla()
    dodaj_kamere()
    print("Skrypt zakończony.")