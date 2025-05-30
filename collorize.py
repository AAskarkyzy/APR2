from colorize import ColorGraph, GraphType, load_preprocessing, make_graph, colorize, first_not_used

'''Направленная версия грфа со странами
Мы здесь ничего не импортируем с главного файла, потому что в колорайз уже импортировано все из него.'''

# Новая локальная функция раскраски с учётом двунаправленных соседей
def my_set_node_color(g, node_id):
    neighbors_colors = []

    # Цвета соседей, на которых есть ребро из node_id (в прямом направлении)
    # Эта строка добавляет в список neighbors_colors цвета всех соседних узлов текущего узла с id node_id
    neighbors_colors += [g.node(n)["color"] for n in g.node(node_id).neighbor_ids]

    # Цвета соседей, у которых есть ребро к node_id (обратное направление)
    # просто типа смотрим соседи ли, если да, то добавляем его в список neighbors_colors и красим
    for other_node_id in g.node_ids():
        if node_id in g.node(other_node_id).neighbor_ids:
            neighbors_colors.append(g.node(other_node_id)["color"])

    # Убираем None (ещё не раскрашенных)
    # Создаётся новый список, в который войдут только те элементы из neighbors_colors, которые НЕ равны None
    neighbors_colors = [c for c in neighbors_colors if c is not None]

    # Выбираем первый свободный цвет
    g.node(node_id)["color"] = first_not_used(neighbors_colors)

# Перезаписываем функцию в модуле(файл) colorize локальной
import colorize
# заменяем функцию которая там на нашу которая тут расписана
colorize.set_node_color = my_set_node_color

if __name__ == "__main__":
    # Загружаем данные из json (без изменений)
    data = load_preprocessing("eu_sousede.json")

    # Создаём направленный граф
    g = ColorGraph(GraphType.DIRECTED)

    # Добавляем узлы и ребра из данных
    for state in data.keys():
        node = g.add_node(state)
        node["color"] = None
    for state in data.keys():
        for neighbor in data[state]:
            if not g.node(state).is_edge_to(neighbor):
                g.add_edge(state, neighbor)

    # Раскрашиваем граф с учётом новой функции set_node_color
    colorize.colorize(g)

    # Сохраняем результат в PNG
    g.export_to_png("eu_sousede_directed_colored.png")
