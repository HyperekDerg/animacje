import bpy
import math

NAZWA_MATERIALU = "Sci-Fi Panel 02"
NAZWA_NODE_EMISSION = "Sci-Fi Panel 02"

KLATKA_START = 1
KLATKA_KONIEC = 125
KLATKA_PAK_START = 30
KLATKA_PAK_KONIEC = 90

def znajdz_node(mat, nazwa, typ_zapasowy=None):
    """Zwraca węzeł po nazwie, fallback po typie. Czytelny błąd, jeśli nie ma."""
    node = mat.node_tree.nodes.get(nazwa)
    if node is None and typ_zapasowy:
        for n in mat.node_tree.nodes:
            if n.type == typ_zapasowy:
                print(f"Nie znaleziono '{nazwa}', używam '{n.name}' (typ {typ_zapasowy}).")
                return n
    if node is None:
        dostepne = [n.name for n in mat.node_tree.nodes]
        raise KeyError(f"Węzeł '{nazwa}' nie istnieje w '{mat.name}'. Dostępne: {dostepne}")
    return node


def wyczysc_animacje_materialu(mat):
    """Idempotencja: usuwa F-Curves z drzewa węzłów."""
    if mat.node_tree.animation_data and mat.node_tree.animation_data.action:
        mat.node_tree.animation_data.action = None

        
def pulsuj_emission(mat, min_str=0.2, max_str_bazowy=2.0, max_str_pik=6.0, okres=25):
    """
    Pulsowanie sinusoidalne Emission Strength przez całe 125 klatek.
    """
    emission = znajdz_node(mat, NAZWA_NODE_EMISSION)
    sciezka = f'nodes["{emission.name}"].inputs["Emission Strength"].default_value'

    for klatka in range(KLATKA_START, KLATKA_KONIEC + 1):
        if KLATKA_PAK_START <= klatka <= KLATKA_PAK_KONIEC:
            postep = (klatka - KLATKA_PAK_START) / (KLATKA_PAK_KONIEC - KLATKA_PAK_START)
            max_str = max_str_bazowy + (max_str_pik - max_str_bazowy) * postep
        elif klatka > KLATKA_PAK_KONIEC:
            max_str = max_str_pik
        else:
            max_str = max_str_bazowy

        srednia = (min_str + max_str) / 2.0
        amplituda = (max_str - min_str) / 2.0
        t = (klatka - KLATKA_START) * (2 * math.pi / okres)
        
        emission.inputs["Emission Strength"].default_value = srednia + amplituda * math.sin(t)
        mat.node_tree.keyframe_insert(data_path=sciezka, frame=klatka)

        
KOLOR_START = (0.0, 0.7, 1.0, 1.0)
KOLOR_KONIEC = (0.2, 1.0, 0.4, 1.0)

def animuj_kolor_emisji(mat):
    emission = znajdz_node(mat, NAZWA_NODE_EMISSION)
    sciezka = f'nodes["{emission.name}"].inputs["Emission Color"].default_value'

    emission.inputs["Emission Color"].default_value = KOLOR_START
    mat.node_tree.keyframe_insert(data_path=sciezka, frame=KLATKA_START)
    emission.inputs["Emission Color"].default_value = KOLOR_KONIEC
    mat.node_tree.keyframe_insert(data_path=sciezka, frame=KLATKA_KONIEC)

    
def main_materialy():
    mat = bpy.data.materials.get(NAZWA_MATERIALU)
    if mat is None:
        print(f"Brak materiału '{NAZWA_MATERIALU}'. Dostępne: {[m.name for m in bpy.data.materials]}")
        return
    
    wyczysc_animacje_materialu(mat)
    
    node = znajdz_node(mat, NAZWA_NODE_EMISSION)
    node.inputs["Base Color"].default_value = (0.100659, 0.0571271, 0.152534, 1.0)
    
    pulsuj_emission(mat)
    animuj_kolor_emisji(mat)
    print("Animacja materiału zakończona.")

main_materialy()