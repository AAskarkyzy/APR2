from diktyonphi import GraphType, Graph
from colorize import ColorGraph, set_node_color, colorize

# Функция для нахождения первого неиспользованного цвета
def first_not_used(colors):
    PALETTE = ["blue", "red", "green", "yellow", "orange", "purple", "pink"]
    for color in PALETTE:
        if color not in colors:
            return color
    return "black"  # fallback, если всё занято

# Новая версия set_node_color, учитывающая входящие и исходящие рёбра
def my_set_node_color(g, node_id):
    neighbors_colors = []

    # Исходящие рёбра (соседи, на которых указывает node_id)
    neighbors_colors += [g.node(n)["color"] for n in g.node(node_id).neighbor_ids]

    # Входящие рёбра (соседи, у которых есть ребро к node_id)
    for other_node_id in g.node_ids():
        if node_id in g.node(other_node_id).neighbor_ids:
            neighbors_colors.append(g.node(other_node_id)["color"])

    neighbors_colors = [c for c in neighbors_colors if c is not None]
    g.node(node_id)["color"] = first_not_used(neighbors_colors)

# Подменяем оригинальную функцию на локальную
import colorize
colorize.set_node_color = my_set_node_color

# Создаём направленный граф
g = ColorGraph(GraphType.DIRECTED)

# Добавляем узлы
for name in ["A", "B", "C", "D"]:
    g.add_node(name)["color"] = None

# Добавляем направленные рёбра
g.add_edge("A", "B")
g.add_edge("A", "C")
g.add_edge("B", "C")
g.add_edge("C", "D")

# Раскрашиваем граф
colorize.colorize(g)

# Экспортируем картинку
g.export_to_png("directed_example.png")