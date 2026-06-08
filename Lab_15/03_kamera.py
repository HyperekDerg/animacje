import bpy
import math
import random

NAZWA_KAMERY    = "Camera_POV"
KLATKA_START    = 1
KLATKA_KONIEC   = 250
ZIARNO_LOSOWOSCI = 432

POZYCJA_START   = (-6.66103, 84.2059,  2.1489)
POZYCJA_KONIEC  = (-6.66103, 38.1941,  2.1489)
ROTACJA         = (math.radians(88.0233), math.radians(-0.000001), math.radians(180))
PREDKOSC_KROKU  = 0.18
WYSOKOSC_KROKU  = 0.2 
SZEROKOSC_KOLYSANIA = 0.04
SILA_DRGAN      = 0.14 
DRGANIE_ROTACJI = 0.004
WYSOKOSC_ODDECHU = 0.09
PREDKOSC_ODDECHU = 0.025

def gladki_skok(t):
    return t * t * (3.0 - 2.0 * t)

def gladki_szum(klatka, przesuniecie_ziarna, predkosc=0.07, oktawy=3):
    generator = random.Random(przesuniecie_ziarna + ZIARNO_LOSOWOSCI)
    suma, amplituda, czestotliwosc = 0.0, 1.0, predkosc
    for _ in range(oktawy):
        faza = generator.uniform(0, math.tau)
        suma += math.sin(klatka * czestotliwosc + faza) * amplituda
        amplituda *= 0.5
        czestotliwosc *= 2.1
    return suma

def pobierz_pole_widzenia(klatka):
    bazowe = math.radians(75)
    dryf = math.sin(klatka * 0.031 + 1.2) * math.radians(0.6)
    return bazowe + dryf

def iteruj_krzywe_f(akcja):
    for warstwa in akcja.layers:
        for pasek in warstwa.strips:
            for grupa_kanalow in pasek.channelbags:
                for fc in grupa_kanalow.fcurves:
                    yield fc

def generuj_animacje_pov():
    kamera = bpy.data.objects.get(NAZWA_KAMERY)
    if not kamera:
        print(f"Błąd: Kamera '{NAZWA_KAMERY}' nie została znaleziona.")
        return
    
    dane_kamery = kamera.data

    kamera.animation_data_clear()
    dane_kamery.animation_data_clear()

    dystans_y = POZYCJA_KONIEC[1] - POZYCJA_START[1]
    calkowity_czas = KLATKA_KONIEC - KLATKA_START

    for klatka in range(KLATKA_START, KLATKA_KONIEC + 1):
        bpy.context.scene.frame_set(klatka)

        t = gladki_skok((klatka - KLATKA_START) / calkowity_czas)
        bazowe_y = POZYCJA_START[1] + dystans_y * t

        faza_chodu = klatka * PREDKOSC_KROKU
        stapnie_z = math.sin(faza_chodu * 2.0) * WYSOKOSC_KROKU
        kolysanie_x = math.sin(faza_chodu) * SZEROKOSC_KOLYSANIA
        oddech_z = math.sin(klatka * PREDKOSC_ODDECHU) * WYSOKOSC_ODDECHU

        drganie_x = gladki_szum(klatka, 1) * SILA_DRGAN
        drganie_y = gladki_szum(klatka, 2) * SILA_DRGAN * 0.4
        drganie_z = gladki_szum(klatka, 3) * SILA_DRGAN * 0.6

        kamera.location = (
            POZYCJA_START[0] + kolysanie_x + drganie_x,
            bazowe_y + drganie_y,
            POZYCJA_START[2] + stapnie_z + oddech_z + drganie_z,
        )

        nachylenie_powiazane = -kolysanie_x * 0.18
        dryf_rot_x = gladki_szum(klatka, 4) * DRGANIE_ROTACJI
        dryf_rot_z = gladki_szum(klatka, 5) * DRGANIE_ROTACJI

        kamera.rotation_euler = (
            ROTACJA[0] + dryf_rot_x,
            ROTACJA[1] + nachylenie_powiazane,
            ROTACJA[2] + dryf_rot_z,
        )

        dane_kamery.angle = pobierz_pole_widzenia(klatka)

        kamera.keyframe_insert(data_path="location", frame=klatka)
        kamera.keyframe_insert(data_path="rotation_euler", frame=klatka)
        dane_kamery.keyframe_insert(data_path="lens", frame=klatka)

    for obiekt in [kamera, dane_kamery]:
        dane_anim = obiekt.animation_data
        if not (dane_anim and dane_anim.action):
            continue
        for fc in iteruj_krzywe_f(dane_anim.action):
            for punkt_kluczowy in fc.keyframe_points:
                punkt_kluczowy.interpolation = 'LINEAR'

generuj_animacje_pov()