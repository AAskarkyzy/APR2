# Импорт аннотаций типов, встроенная хуйня
from typing import Dict, List, Iterable
# Импорт графа и его типа из другого файла
from diktyonphi import Graph, GraphType
# Импорт работы с JSON-форматом
import json

# Класс ColorGraph наследуется от базового класса Graph
# и добавляет функциональность для раскрашивания узлов графа при визуализации в формате DOT
class ColorGraph(Graph):
    PALETTE = ["blue", "red", "green", "yellow", "orange", "purple", "pink"]


    def __init__(self, type: GraphType):
        '''super() - это встроенная функция Python, которая позволяет обратиться к родительскому классу
        __init__  - автоматически вызывается при создании нового объекта класса
        типа "Прежде чем делать свою инициализацию в классе ColorGraph, сначала выполни стандартную инициализацию из родительского класса Graph"
        типа нам в этой строке нужно именно создание типа графа'''
        super().__init__(type)
    

    def to_dot(self, label_attr:str ="label", weight_attr:str = "weight") -> str:
        #TODO převezmete kód z Graph a změníte
        # lines.append(f'    "{node_id}" [label="{label}"];')
        lines = []
        name = "G"
        connector = "->" if self.type == GraphType.DIRECTED else "--"

        lines.append(f'digraph {name} {{' if self.type == GraphType.DIRECTED else f'graph {name} {{')

        # Nodes
        for node_id in self.node_ids():
            node = self.node(node_id)
            label = node[label_attr] if label_attr in node._attrs else str(node_id)
            # THERE IS THE CHANGES !!!!!!!!!!!!!!!
            # Цвет заливки узла. Берётся из палитры PALETTE по индексу node['color'].
            # Например, если node['color'] = 1 → PALETTE[1] = "red".
            lines.append(f'''    "{node_id}" [label="{label}",style=filled, 
                                 fillcolor={ColorGraph.PALETTE[node['color']]}];''')

        # Edges
        seen = set()
        for node_id in self.node_ids():
            node = self.node(node_id)
            for dst_id in node.neighbor_ids:
                if self.type == GraphType.UNDIRECTED and (dst_id, node_id) in seen:
                    continue
                seen.add((node_id, dst_id))
                edge = node.to(dst_id)
                label = edge[weight_attr] if weight_attr in edge._attrs else ""
                lines.append(f'    "{node_id}" {connector} "{dst_id}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)

# загружает файл eu_sousede.json
# при входе даем название файла или  путь к JSON-файлу
# при выходе получаем словарь Ключ (str) — название штата, Значение (List[str]) — список названий соседних штатов
def load_preprocessing(filename: str) -> Dict[str, List[str]]:
    # Открывает файл в режиме чтения текста ("rt")
    with open(filename, "rt") as f:
        # Загружает JSON-данные в переменную data (будет словарём)
        data = json.load(f)

    # Фильтрация данных
    for state in data.keys():
        # if the state is in dict, we keep it in data
        # а если там стат которого нахуй нет в списке, то удаляем
        data[state] = [neighbour for neighbour in data[state]
                       if neighbour in data]
    return data

# превращает файл json в граф для раскраски
# data — словарь, где ключи (str) это названия штатов, а значения (List[str]) — списки их соседей
def make_graph(data: Dict[str, List[str]]) -> Graph:
    # Создаёт неориентированный граф (UNDIRECTED)
    # Выбрана реализация ColorGraph (наследник Graph), чтобы позже можно было раскрашивать узлы
    g = ColorGraph(GraphType.UNDIRECTED)

    # создаем Node
    for state in data.keys():
        # Добавляет узел с ID = название штата
        node = g.add_node(state)
        # Инициализирует атрибут цвета (пока не задан)
        node["color"] = None

    # добавление ребер
    for state in data.keys():
        for neighbour in data[state]:
            # is_edge_to является функцией в классе Node в файле diktyonphi.py
            if not g.node(state).is_edge_to(neighbour):
                g.add_edge(state, neighbour)
    return g

#FIXME: možná příliš brutal force
# Функция находит первый недостающий цвет (число) в переданном наборе colors.
# итерационно рассматриваем цвета
# на выходе получаем число
def first_not_used(colors: Iterable[int]) -> int:
    # Проверяем от 0 до N
    for i in range(len(colors) + 1):
        # Если числа нет в списке
        if i not in colors:
            return i

# Функция находит узел с максимальной степенью исхода (количество исходящих рёбер) среди заданного набора узлов графа.
# принимает  объект графа
# nodes: коллекция имён узлов (например, ["A", "B", "C"])
def get_max_degree_node(g: Graph, nodes: Iterable[str]) -> str:
    '''Функция max() ищет максимальный элемент в коллекции nodes, используя критерий из key.
       lambda - создаёт анонимную функцию
       state - принимает имя узла (например, "A")
       g.node(state) - получает объект узла из графа g
       .out_degree - свойство узла, возвращающее количество исходящих рёбер'''
    return max(nodes, key=lambda state: g.node(state).out_degree)

# назначает цвет узлу графа так, чтобы он отличался от цветов всех соседних узлов
# на входе передаем g — объект графа, node — имя узла, который нужно раскрасить
def set_node_color(g: Graph, node: str) -> None:
    '''Сбор цветов соседей, ИМЕННО ТУТ МЫ ПРИДУМЫВАЕМ ЦИФРЫ ЦВЕТАМ !!!!!!!!!!!!!!1
        Создаёт список color_of_neighbours, содержащий цвета всех соседних узлов
        g.node(node).neighbor_nodes — возвращает все соседние узлы для текущего node
        neighbor_nodes - является функцией из класса Node из файла dictyonphi.py
        
        Например, если узел "A" имеет соседей ["B", "C"] с цветами 1 и 0, то colors = [1, 0]'''
    color_of_neighbours = [neighbour_node["color"]  for neighbour_node
                             in g.node(node).neighbor_nodes]
    
    #Выбор уникального цвета
    # вызываем функцию first_not_used и передаем переменную color_of_neighbours
    g.node(node)["color"] = first_not_used(color_of_neighbours)

# THAT'S MINE. прямо проверяет «есть ли у соседей одинаковый цвет» или нет.
def check_coloring_conflicts(g: Graph) -> bool:
    for node_id in g.node_ids():
        node_color = g.node(node_id)["color"]
        for neighbor in g.node(node_id).neighbor_nodes:
            if node_color == neighbor["color"]:
                return False  # Есть конфликт — соседние узлы одного цвета
    return True  # Конфликтов нет

# это жадный алгоритм раскраски графа, где узлы раскрашиваются по одному, начиная с самых "связанных".
def colorize(g: Graph):
    # Создаётся множество colorless из ID всех узлов графа
    colorless = set(g.node_ids())
    # цикл выполняется пока все узлы не будут раскрашены
    while colorless:
        print(colorless)
        # Выбор узла для раскраски. Сверху расписана эта функция. Передаем g, созданный в функции make_graph, и само множество, созданное тут
        next_state = get_max_degree_node(g, colorless)
        set_node_color(g, next_state)
        print(next_state, g.node(next_state)["color"])
        # и сразу удаляем узел из списка 
        colorless.remove(next_state)

# для запуска кода отсюда
if __name__ == "__main__":
    # выше функция, которая работает с файлом json
    data = load_preprocessing("eu_sousede.json")
    # передаем файл json этой функции, которая превращает все в граф для раскраски
    g = make_graph(data)

    # ⬇️ Добавляем новую страну вручную
    atlantis = g.add_node("Atlantis")
    # подготавливает его для раскраски
    atlantis["color"] = None

    # Цикл по соседям — отличный способ аккуратно добавить рёбра, не дублируя уже существующие
    # is_edge_to(...) — хорошая защита от дубликатов
    for neighbor in ["Germany", "France"]:
        if not g.node("Atlantis").is_edge_to(neighbor):
            g.add_edge("Atlantis", neighbor)
    
    colorize(g)

    # от меня для функции выше по проверке цветов
    if check_coloring_conflicts(g):
        print("✅ No color conflicts found.")
    else:
        print("❌ There are color conflicts!")
    
    g.export_to_png("eu_sousede.png")


