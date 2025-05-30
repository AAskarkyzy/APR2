# grafova_zkouska_rozsireni.py
# ✅ Rozšířené úlohy ke zkoušce – variace na práci s API z diktyonphi.py

from diktyonphi import Graph, GraphType

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 9: Uzly s výstupním stupněm větším než 2
# Úkol: Najděte všechny uzly, které mají více než 2 sousedy.
# ─────────────────────────────────────────────────────────────
def uzly_s_vysokym_stupnem(g, hranice=2):
    return [node.id for node in g if node.out_degree > hranice]

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 10: Najděte všechny cesty mezi dvěma uzly (bez cyklů)
# Úkol: Vraťte seznam všech necyklických cest mezi dvěma uzly.
# ─────────────────────────────────────────────────────────────
'''Найти все возможные маршруты (пути) от начального узла start_id до конечного узла end_id.
Возвращает список путей, где каждый путь — это список узлов, через которые мы прошли.'''

# path изначально None, чтобы можно было создавать новый пустой список при первом вызове
def najdi_vsechny_cesty(g, start_id, end_id, path=None):
    path = path or []
    # Создаём новый список пути, добавляя текущий узел start_id в конец.
    # создаёт новую копию списка, которая содержит все старые элементы плюс новый
    path = path + [start_id]

    # Если текущий узел совпал с конечным — значит, мы нашли путь.
    # Обратите внимание: возвращаем именно список путей
    if start_id == end_id:
        return [path]
    
    # Если узла start_id нет в графе g — возвращаем пустой список (пути не существует).
    if start_id not in g:
        return []
    
    # Создаём пустой список для накопления всех найденных путей.
    paths = []
    for neighbor in g.node(start_id).neighbor_ids:
        # Проверяем, чтобы не заходить в узлы, которые уже были в текущем пути (чтобы избежать циклов/зацикливания).
        if neighbor not in path:
            # Рекурсивно вызываем функцию для соседа, передавая обновлённый путь path.
            nove = najdi_vsechny_cesty(g, neighbor, end_id, path)
            # Добавляем все найденные пути из рекурсивного вызова к нашему списку путей paths
            paths.extend(nove)
    return paths

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 11: Detekce obecného cyklu v grafu
# Úkol: Zjistěte, zda graf obsahuje libovolný cyklus.
# ─────────────────────────────────────────────────────────────
def existuje_cyklus(g):
    visited = set()
    stack = set()

    def dfs(node_id):
        visited.add(node_id)
        stack.add(node_id)
        for neighbor_id in g.node(node_id).neighbor_ids:
            if neighbor_id not in visited:
                if dfs(neighbor_id):
                    return True
            elif neighbor_id in stack:
                return True
        stack.remove(node_id)
        return False

    for node in g:
        if node.id not in visited:
            if dfs(node.id):
                return True
    return False

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 12: Počet hran určitého typu
# Úkol: Spočítejte, kolik hran má daný typ.
# ─────────────────────────────────────────────────────────────
def pocet_hran_typu(g, typ):
    count = 0
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            if edge['type'] == typ:
                count += 1
    return count

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 13: Obrácení hran v grafu (reverse graph)
# Úkol: Vytvořte nový graf, kde budou hrany obrácené.
# ─────────────────────────────────────────────────────────────
def obratit_graf(g):
    g_rev = Graph(GraphType.DIRECTED)
    for node in g:
        g_rev.add_node(node.id, node._attrs.copy())
    for node in g:
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            g_rev.add_edge(neighbor_id, node.id, edge._attrs.copy())
    return g_rev

# ─────────────────────────────────────────────────────────────
# 🔹 Téma 14: Zjištění izolovanosti uzlu
# Úkol: Určete, zda je uzel izolovaný (bez výstupních hran).
# ─────────────────────────────────────────────────────────────
def je_izolovany(g, uzel_id):
    return g.node(uzel_id).out_degree == 0

# ─────────────────────────────────────────────────────────────
# 🔸 Testovací příklad
# ─────────────────────────────────────────────────────────────
def test():
    g = Graph(GraphType.DIRECTED)
    g.add_node("A", {"label": "A", "color": "green"})
    g.add_node("B", {"label": "B", "color": "blue"})
    g.add_node("C", {"label": "C", "color": "red"})
    g.add_node("D", {"label": "D", "color": "yellow"})

    g.add_edge("A", "B", {"weight": 1, "type": "normal"})
    g.add_edge("B", "C", {"weight": 2, "type": "critical"})
    g.add_edge("C", "A", {"weight": 3, "type": "loop"})
    g.add_edge("A", "D", {"weight": 4, "type": "optional"})

    print("Uzly s vysokým stupněm:", uzly_s_vysokym_stupnem(g))
    print("Cesty z A do C:", najdi_vsechny_cesty(g, "A", "C"))
    print("Obsahuje graf cyklus:", existuje_cyklus(g))
    print("Počet hran typu 'critical':", pocet_hran_typu(g, "critical"))
    print("Je uzel D izolovaný:", je_izolovany(g, "D"))
    g_rev = obratit_graf(g)
    print("Obrácený graf má tyto hrany:")
    for node in g_rev:
        for neighbor_id in node.neighbor_ids:
            print(f"{node.id} -> {neighbor_id}")

if __name__ == "__main__":
    test()
