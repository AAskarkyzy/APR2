# grafova_zkouska_priprava.py
# ✅ Témata a řešení typických úloh ke zkoušce z práce s grafy (API z diktyonphi.py)
# 🔴 Označení "(ZADÁNÍ OD UŽIVATELE)" znamená, že úloha pochází přímo z původního popisu uživatele.

from diktyonphi import Graph, GraphType

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 1: Počet uzlů a hran, výpis hran a jejich atributů (ZADÁNÍ OD UŽIVATELE)
# ─────────────────────────────────────────────────────────────

def pocet_uzlu(g):
    return len(g)

def pocet_hran(g):
    hrany = sum(node.out_degree for node in g)
    return hrany if g.type == GraphType.DIRECTED else hrany // 2


def vypis_hrany_s_atributy(g):
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            print(f"{node.id} -> {neighbor_id}: váha={edge['weight']}, typ={edge['type']}")


# Variace:
# - Seřaďte hrany podle váhy sestupně
# - Najděte hrany typu „critical“

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 2: Stupeň uzlů (ZADÁNÍ OD UŽIVATELE)
# ─────────────────────────────────────────────────────────────

def stupne_uzlu(g):
    for node in g:
        # типа сколько ребер исходит из каждого узла
        print(f"Uzel {node.id} má výstupní stupeň: {node.out_degree}")

# Variace:
# - Najděte uzly s nulovým stupněm (slepé konce)
# - Vypište průměrný výstupní stupeň všech uzlů

def uzly_s_nulovym_stupnem(g):
    return [node.id for node in g if node.out_degree == 0]

def prumerny_stupen(g):
    return sum(node.out_degree for node in g) / len(g)

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 3: Smyčky v grafu (ZADÁNÍ OD UŽIVATELE)
# ─────────────────────────────────────────────────────────────

def existuje_smycka(g):
    return any(node.is_edge_to(node.id) for node in g)

# Variace:
# - Vraťte seznam všech uzlů, které mají smyčku

def uzly_se_smyckou(g):
    return [node.id for node in g if node.is_edge_to(node.id)]
# it is node A

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 4: Záporné hrany (ZADÁNÍ OD UŽIVATELE)
# ─────────────────────────────────────────────────────────────

def existuje_zaporna_hrana(g):
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            if "weight" in edge._attrs and edge["weight"] < 0:
                return True
    return False

# Variace:
# - Najděte všechny záporné hrany a vypište je

def vsechny_zaporne_hrany(g):
    vysledky = []
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            # типа если есть вес в атрибутах, то посмотри меньше ли он нуля
            if "weight" in edge._attrs and edge["weight"] < 0:
                # если он меньше нуля, то в список добавляем айди узла, куда он идет и вес
                vysledky.append((node.id, neighbor_id, edge["weight"]))
    return vysledky

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 5: Lineární graf (ZADÁNÍ OD UŽIVATELE)
'''линейный значит все вершины имеют степень не более 2
и если степень ровно 1, тоже линейный, bc это конец линии'''
# ─────────────────────────────────────────────────────────────

def je_linearni(g):
    for node in g:
        # Вычисление степени, если граф направленный
        deg = node.out_degree
        # Если граф неориентированный, тогда степень — это кол-во соседей (так как каждое ребро учитывается один раз)
        if g.type == GraphType.UNDIRECTED:
            deg = len(list(node.neighbor_ids))
        if deg > 2:
            return False
    return True

# Variace:
# - Zjistěte, zda je graf cesta (každý uzel má stupeň 2 kromě krajních)
'''Функция je_cesta(g) проверяет, является ли неориентированный граф простой цепочкой (путём) 
— то есть линейной последовательностью без циклов'''

def je_cesta(g):
    # собираем список степеней всех вершин
    stupne = [len(list(node.neighbor_ids)) for node in g]
    # считаем, сколько вершин имеют степень 1 и 2
    pocet1 = stupne.count(1)
    pocet2 = stupne.count(2)
    # возвращаем True, если 2 вершины степени 1, а остальные — степени 2
    return pocet1 == 2 and pocet2 == len(stupne) - 2

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 6 (navíc): Vyhledání uzlů podle atributu (смотря на цвет)
# ─────────────────────────────────────────────────────────────

# barva задаем в конце в функции test()
def uzly_podle_barvy(g, barva):
    return [node.id for node in g if node["color"] == barva]

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 7 (navíc): Úprava váhy hran
# ─────────────────────────────────────────────────────────────

def zvysit_vahy_hran(g, o_kolik):
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            if "weight" in edge._attrs:
                edge["weight"] += o_kolik

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 8 (navíc): Odstranění hran určitého typu (logická simulace)
# ─────────────────────────────────────────────────────────────

def najdi_hrany_podle_typu(g, hledany_typ):
    vysledky = []
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            if edge["type"] == hledany_typ:
                vysledky.append((node.id, neighbor_id))
    return vysledky

# ─────────────────────────────────────────────────────────────
# 🔸 Testovací data a výpis výsledků
# ─────────────────────────────────────────────────────────────

def test():
    g = Graph(GraphType.DIRECTED)
    g.add_node("A", {"label": "Start", "color": "green"})
    g.add_node("B", {"label": "Middle", "color": "yellow"})
    g.add_node("C", {"label": "End", "color": "red"})
    g.add_edge("A", "B", {"weight": 1, "type": "normal"})
    g.add_edge("B", "C", {"weight": -5, "type": "critical"})
    g.add_edge("A", "A", {"weight": 0.5, "type": "loop"})  # Smyčka

    print("Počet uzlů:", pocet_uzlu(g))
    print("Počet hran:", pocet_hran(g))
    vypis_hrany_s_atributy(g)
    stupne_uzlu(g)
    print("Uzly s nulovým stupněm:", uzly_s_nulovym_stupnem(g))
    print("Průměrný výstupní stupeň:", prumerny_stupen(g))
    print("Obsahuje smyčku:", existuje_smycka(g))
    print("Uzly se smyčkou:", uzly_se_smyckou(g))
    print("Obsahuje zápornou hranu:", existuje_zaporna_hrana(g))
    print("Seznam záporných hran:", vsechny_zaporne_hrany(g))
    print("Je graf lineární:", je_linearni(g))
    print("Je graf cesta:", je_cesta(g))
    print("Uzly s barvou 'red':", uzly_podle_barvy(g, "red"))
    zvysit_vahy_hran(g, 1)
    print("Hrany typu 'loop':", najdi_hrany_podle_typu(g, "loop"))

if __name__ == "__main__":
    test()
