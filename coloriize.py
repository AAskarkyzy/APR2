from diktyonphi import GraphType, Graph
from colorize import ColorGraph, GraphType, set_node_color, colorize, load_preprocessing, make_graph

# Новая версия set_node_color, учитывающая двусторонних соседей
def my_set_node_color(g, node_id):
    # собираем цвета всех соседей (и тех, у кого есть ребро к node_id, и кого node_id "видит")
    neighbors_colors = []

    # цвет соседей, на которых есть ребро из node_id
    neighbors_colors += [g.node(n)["color"] for n in g.node(node_id).neighbor_ids]

    # цвет соседей, у которых есть ребро к node_id (обратные ребра)
    for other_node_id in g.node_ids():
        if node_id in g.node(other_node_id).neighbor_ids:
            neighbors_colors.append(g.node(other_node_id)["color"])

    # выбираем первый неиспользованный цвет
    neighbors_colors = [c for c in neighbors_colors if c is not None]
    g.node(node_id)["color"] = first_not_used(neighbors_colors)

# Заменяем оригинальную функцию на нашу локальную
import colorize
colorize.set_node_color = my_set_node_color

# Загружаем данные и создаём граф, как обычно
data = load_preprocessing("eu_sousede.json")
g = make_graph(data)

'''
Создаю направленный граф
Почему все узлы, кроме B, имеют одинаковый цвет? 
    Потому что это ориентированный граф, и colorize() смотрит только на соседей по направлению.
'''

g = ColorGraph(GraphType.DIRECTED)

# добавляем узлы
g.add_node("A")["color"] = None
g.add_node("B")["color"] = None
g.add_node("C")["color"] = None
g.add_node("D")["color"] = None

# добавляем направленные рёбра
g.add_edge("A", "B")
g.add_edge("A", "C")
g.add_edge("B", "C")
g.add_edge("C", "D")

# раскрашиваем
#colorize(g)

# Используем colorize — теперь с нашей функцией раскраски
colorize.colorize(g)

# экспорт в PNG
g.export_to_png("directed_example.png")

