# позволяет создавать именованные константы
import enum
# Модуль для запуска внешних команд и процессов
# вызов из Python терминальной команды dot, которая идёт с Graphviz
import subprocess
# typing Чтобы явно указывать типы аргументов и возвращаемых значений функций/методов
from typing import Dict, Hashable, Any, Optional, Iterator, Tuple

# there we use the enum library
# вместо обычных чисел или строк, просто чтобы в дальнейшем было удобно использовать
class GraphType(enum.Enum):
    """Graph orientation type: directed or undirected."""
    DIRECTED = 0
    UNDIRECTED = 1

# Edge Это ребро графа — то есть связь между двумя узлами (точками). 
class Edge:
    """Representation of an edge between two nodes with associated attributes."""

    def __init__(self, src: 'Node', dest: 'Node', attrs: Dict[str, Any]):
        """
        Initialize an edge from src_id to dest_id with given attributes.

        :param src: Source node identifier. Начальная точка
        :param dest: Destination node identifier. Конечная точка
        :param attrs: Dictionary of edge attributes. Словарь с атрибутами ребра (например, вес, тип и т. д.)
        """
        self.src = src
        self.dest = dest
        self._attrs = attrs

    # Получение именно атрибуты по ключу
    # key: str — ожидается, что ключ будет строкой.
    # -> Any — функция возвращает любой тип данных (может быть число, строка и т.д.).
    def __getitem__(self, key: str) -> Any:
        """Access edge attribute by key."""
        return self._attrs[key]

    # Изменение атрибута
    # -> None — функция ничего не возвращает, просто меняет значение.
    def __setitem__(self, key: str, val: Any) -> None:
        """Set edge attribute by key.
        Типа позволяет нам менять значения ребра в будущем, обращаясь к обьекту как к значению словаря по ключу"""
        self._attrs[key] = val

    # Как ребро выглядит при печати
    def __repr__(self):
        '''тут мы типа обращаемся сначала к целому классу edge и потом печатаем откуда куда и атрибуты связи'''
        return f"Edge({self.src.id}→{self.dest.id}, {self._attrs})"


class Node:
    """Representation of a graph node with attributes and outgoing edges."""

    def __init__(self, graph: 'Graph', node_id: Hashable, attrs: Dict[str, Any]):
        """
        Initialize a node with a given identifier and attributes.

        :param node_id: Unique identifier of the node. И тут Hashable значит превращать его в число для быстрого поиска
        :param attrs: Dictionary of node attributes.
        Все что в скобках сверху - входные данные, которые мы должны получить извне, когда создается узел
        """
        self.id = node_id
        self.graph = graph
        self._attrs = attrs
        self._neighbors: Dict[Hashable, Dict[str, Any]] = {}
        '''_neighbors внутренний словарь, который всегда должен начинаться пустым для нового узла, поэтому его нет вначале
        Типа этот параметр не обязателен лично для каждого узла, он создается уже внутри обьекта'''

    def __getitem__(self, item: str) -> Any:
        """Access node attribute by key. Как у ребер"""
        return self._attrs[item]
    '''Относительно разницы в функциях для ребер и узлов, а именно key/item: 
    В функциях __getitem__ и __setitem__ — имена параметров могут быть любыми, это просто переменные.'''

    def __setitem__(self, item: str, val: Any) -> None:
        """Set node attribute by key."""
        self._attrs[item] = val

    def to(self, dest: Hashable | 'Node') -> Edge:
        """
        Get the edge from this node to the specified destination node (к другому узлу!!!)

        :param dest_id: ID of the target node.
        dest: Hashable | 'Node' - можно по айди или просто по другому объект-узлу, just for flexibility

        :return: Edge instance representing the connection.
        :raises ValueError: If no such edge exists.
        """
        dest_id = dest.id if isinstance(dest, Node) else dest 
        # тут типа если по Node, то берем его айди, а если передали по айди, то просто dest

        # просто прописываем ошибку
        if dest_id not in self._neighbors:
            raise ValueError(f"No edge from {self.id} to {dest_id}")
        return Edge(self, self.graph.node(dest_id), self._neighbors[dest_id])
        '''создаём объект Edge от текущего узла (self) к узлу назначения (self.graph.node(dest_id))
        передаём также атрибуты ребра, которые хранились в _neighbors[dest_id] - атрибуты ребра между двумя узлами'''

    def connect_to(self,  dest: Hashable | 'Node', attrs: Optional[Dict[str, Any]] = None):
        '''создаем ребро между узлами
        attrs: Optional[Dict[str, Any]] = None - типа не обязательно иметь атрибуты, но если будут то по стандарту, а если нет то просто None
        '''
        dest = dest if isinstance(dest, Node) else self.graph.node(dest)
        '''Если dest уже объект Node, оставляем как есть.
        Если это просто ID, мы достаём соответствующий Node из графа: self.graph.node(dest)
        Потому что нам нужен именно обьект, а не просто айди как в других функциях'''

        # Убеждаемся, что оба узла находятся в одном графе.
        assert dest.graph == self.graph, f"Destination node {dest.id} is not in the same graph"
        # Убеждаемся, что узел назначения действительно есть в графе (по ID)
        assert dest.id in self.graph, f"Destination node {dest.id} is not in graph"
        # добавляем созданное ребро в граф
        self.graph.add_edge(self.id, dest.id, attrs if attrs is not None else {})

    def is_edge_to(self, dest: Hashable | 'Node') -> bool:
        """
        Check if this node has an edge to the given node.

        :param dest_id: ID of the target node.
        :return: True if edge exists, False otherwise.
        """
        dest_id = dest.id if isinstance(dest, Node) else dest # by id is staci

        return dest_id in self._neighbors
        '''Проверяем наличие ребра
        If yes - True, if there is no edge - False'''

    # Это специальный декоратор. 
    # превращает функцию в свойство, чтобы ты могла писать node.neighbor_ids, без скобок, как будто это обычное поле, а не функция.
    @property
    def neighbor_ids(self) -> Iterator[Hashable]:
        """Return an iterator(типа по одному обьекту получаем) over IDs of neighboring nodes.
        В целом жай возвращает список ID соседей! данного узла"""
        return iter(self._neighbors)

    @property
    def neighbor_nodes(self) -> Iterator['Node']:
        '''возвращаем не просто айди, а по Node'''
        for id in self.neighbor_ids:
            # Вместо того чтобы сразу вернуть все элементы списка, yield отдаёт по одному, когда его просят (например, в for-цикле)
            yield self.graph.node(id)

    @property
    def out_degree(self) -> int:
        """Return the number of outgoing edges. Возвращает число исходящих рёбер из этого узла."""
        return len(self._neighbors)
    
    # удобно печатает просто. Покажет ID и атрибуты
    def __repr__(self):
        return f"Node({self.id}, {self._attrs})"
    
    # Сравнение двух узлов. Если ID одинаковые, считаются равными.
    # Это встроенный метод __eq__, который отвечает за сравнение объектов через ==
    # Это важно, например, при обходе графа, чтобы не заходить дважды в один и тот же узел.
    def __eq__(self, other):
        # Проверяем, что второй объект (other) — действительно узел (Node).
        if not isinstance(other, Node):
            # if they are not same
            return False
        return self.id == other.id

    # просто хэшируем чтоб потом использовать этот айди в dict
    def __hash__(self):
        return hash(self.id)


class Graph:
    """Graph data structure supporting directed and undirected graphs."""

    def __init__(self, type: GraphType):
        """
        Initialize a graph with the given type.

        :param type: GraphType.DIRECTED or GraphType.UNDIRECTED
        """
        self.type = type # Тип графа: направленный или нет
        # _nodes — это словарь, где ключ — ID узла, а значение — объект Node.
        self._nodes: Dict[Hashable, Node] = {} # Все узлы графа, храним их в словаре

    def add_node(self, node_id: Hashable, attrs: Optional[Dict[str, Any]] = None) -> Node:
        """
        Add a new node to the graph.

        :param node_id: Unique node identifier.
        :param attrs: Optional dictionary of attributes.
        :raises ValueError: If the node already exists.
        """

        # we check if it is already in our dict of nodes of our graph
        if node_id in self._nodes:
            raise ValueError(f"Node {node_id} already exists")
        # если его нет, то создаем по айди, и добавляем атрибуты
        return self._create_node(node_id, attrs if attrs is not None else {})

    def add_edge(self, src_id: Hashable, dst_id: Hashable,
                 attrs: Optional[Dict[str, Any]] = None) -> Tuple[Node, Node]:
        """
        Add a new edge to the graph. Nodes are created automatically if missing.

        :param src_id: Source node ID.
        :param dst_id: Destination node ID.
        :param attrs: Optional dictionary of edge attributes.
        :raises ValueError: If the edge already exists.
        """

        # если атрибуты не были переданы, просто заменяем его на пустой словарь
        attrs = attrs if attrs is not None else {}

        # тут мы проверяем есть ли src_id/dst_id в self._nodes, если нет - просто создаем их
        if src_id not in self._nodes:
            self._create_node(src_id, {})
        if dst_id not in self._nodes:
            self._create_node(dst_id, {})

        # создаем ребро между узлами по их айдишкам энд атрибутов
        self._set_edge(src_id, dst_id, attrs)

        # Если граф ненаправленный, то для каждого ребра нужно сохранить его в обе стороны.
        if self.type == GraphType.UNDIRECTED:
            self._set_edge(dst_id, src_id, attrs)
        # Возвращает два объекта Node — исходный и целевой. Это может быть полезно, если ты хочешь сразу дальше с ними работать.
        return (self._nodes[src_id], self._nodes[dst_id])

    # __contains__ делает граф удобным для использования извне
    # типа чтобы люди извне могли искать узлы так: if "A" in g. Не прописывая название словаря и тд.
    def __contains__(self, node_id: Hashable) -> bool:
        """Check whether a node exists in the graph."""
        return node_id in self._nodes

    def __len__(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    def __iter__(self) -> Iterator[Node]:
        """Iterate over node IDs in the graph.
        __iter__ возвращает итератор по всем Node, хранящимся в словаре self._nodes
        Там сверху в классе Node мы возвращаем айди соседей узла в функции neighbor_ids"""
        return iter(self._nodes.values())

    # returns the IDs of nodes
    def node_ids(self) -> Iterator[Hashable]:
        return iter(self._nodes.keys())

    def node(self, node_id: Hashable) -> Node:
        """
        Get the Node instance! with the given ID.
        Ты просто передаёшь ID, и она сразу достаёт из словаря нужный Node без перебора и без лишней боли.
        А вот сверху в функциях __iter__, node_ids мы проходились по всему списку и получали инфу по всему словарю

        :param node_id: The ID of the node.
        :return: Node instance.
        :raises KeyError: If the node does not exist.
        """
        return self._nodes[node_id]

    def _create_node(self, node_id: Hashable, attrs: Optional[Dict[str, Any]] = None) -> Node:
        """Internal (внутренний) method to create a node. Работает только внутри данного класса Graph
        Короч, сверху мы вызываем эту функцию по созданию узла. Тут мы просто создали эту функцию
        Видишь, вот тут вот мы и вызываем класс Node"""
        node = Node(self, node_id, attrs)
        self._nodes[node_id] = node
        return node

    def _set_edge(self, src_id: Hashable, target_id: Hashable, attrs: Dict[str, Any]) -> None:
        """Internal method to create a directed edge.
        То же самое. Просто создаем функцию, которые мы выше вызывали внутри класса Graph"""

        # проверяем есть ли target_id в словаре соседей определенного узла
        # при создании Node, автоматический создается и словарь self._neighbors, так как мы прописали это в классе Node
        # поэтому тут мы можем ссылатсья на словарь, созданный в другом обьекте
        if target_id in self._nodes[src_id]._neighbors:
            raise ValueError(f"Edge {src_id}→{target_id} already exists")
        #  добавляет ребро (связь) из узла src_id в узел target_id, и при этом сохраняет атрибуты ребра в словаре.
        self._nodes[src_id]._neighbors[target_id] = attrs

    def __repr__(self):
        '''node.out_degree - ссылаемся на функцию out_degree, который был создан в классе node. Считает сколько ребер исходит из узла
          self._nodes.values() — берём все узлы графа.
          конкретно в нижней строке мы просто считаем общее количество всех рёбер в графе'''
        edges = sum(node.out_degree for node in self._nodes.values())

        # Если граф неориентированный, то делим количество рёбер пополам (убираем дубли)
        if self.type == GraphType.UNDIRECTED:
            edges //= 2

        # тут просто выводим в целом сколько узлов и ребер есть в graph
        return f"Graph({self.type}, nodes: {len(self._nodes)}, edges: {edges})"

    def to_dot(self, label_attr:str ="label", weight_attr:str = "weight") -> str:
        """
        Generate a simple Graphviz (DOT) representation of the graph. Generated by ChatGPT.

        label_attr: имя атрибута узла, которое будет отображаться как подпись (например, "label"), его типа тоже надо прописывать отдельно прям label деп
        weight_attr: имя атрибута ребра, которое будет отображаться как вес или подпись (например, "weight")

        :return: String in DOT language.
        """
        lines = []
        name = "G"
        # connector — символ связи
        connector = "->" if self.type == GraphType.DIRECTED else "--"

        lines.append(f'digraph {name} {{' if self.type == GraphType.DIRECTED else f'graph {name} {{')

        # Nodes
        for node_id in self.node_ids():
            node = self.node(node_id)
            # берем его label_attr, если есть, иначе просто по айди
            label = node[label_attr] if label_attr in node._attrs else str(node_id)
            lines.append(f'    "{node_id}" [label="{label}"];')

        # Edges
        # set — это множество в Python. Это неупорядоченная коллекция уникальных элементов.
        # нужна для того, чтобы не добавить одни и те же рёбра дважды, если граф неориентированный (UNDIRECTED).
        seen = set()
        for node_id in self.node_ids():
            node = self.node(node_id)
            for dst_id in node.neighbor_ids:
                # and (dst_id, node_id) - добавлено в обратном порядке
                if self.type == GraphType.UNDIRECTED and (dst_id, node_id) in seen:
                    continue
                # добавляем лишь в том случае, если при проверке вышло False
                seen.add((node_id, dst_id))
                # Получаем объект ребра
                edge = node.to(dst_id)
                # присваивает метку (label) ребру, если у этого ребра есть атрибут с нужным именем (по умолчанию это "weight").
                label = edge[weight_attr] if weight_attr in edge._attrs else ""
                # connector - прописали сверху, просто знак, указывающий DIRECTED OR NOT
                lines.append(f'    "{node_id}" {connector} "{dst_id}" [label="{label}"];')

        # just closing the list
        lines.append("}")
        # Склеиваем всё в одну строку
        return "\n".join(lines)


    def export_to_png(self, filename: str = None) -> None:
        """
        Export the graph to a PNG file using Graphviz (dot). Graphviz (https://graphviz.org/)
         must be installed.

        filename: str = None — значит, что параметр filename необязательный. Если не указать, будет просто None
        -> None означает, что функция ничего не возвращает (возвращает None).

        :param filename: Output PNG filename.
        :raises RuntimeError: If Graphviz 'dot' command fails.
        """

        # Генерируем текстовое описание графа в формате DOT
        # тут self, потому что обе функции находятся внутри одного класса и класс сам к себе обращается
        dot_data = self.to_dot()
        try:
            # there we use the library subprocess
            # that function is for сгенерировать изображение графа
            # Запускаем внешнюю программу Graphviz (команду dot), чтобы создать PNG-файл
            subprocess.run(
                ["dot", "-Tpng", "-o", filename], # Команда: dot, формат вывода PNG, файл вывода - filename
                input=dot_data, # Передаём описание графа в программу dot через стандартный ввод
                text=True, # Ввод/вывод как текст (а не байты)
                check=True  # Если команда вернёт ошибку — вызовет исключение
            )
        except subprocess.CalledProcessError as e:
            # Если команда dot не сработала (например, Graphviz не установлен или ошибка в dot_data)
            raise RuntimeError(f"Graphviz 'dot' command failed: {e}") from e

    def _repr_svg_(self):
        """
          Return SVG representation of the graph for Jupyter notebook (implementation
          of protocol of IPython).
          Короч у нас прописаны разные варианты отображения изображения, просто для удобства, мы не все их используем
        """
        # вызывает self.to_image() и возвращает .data — то есть SVG-данные для отображения.
        return self.to_image().data

    def to_image(self):
        """
            Return graph as SVG (usable in IPython notebook).
            IPython notebook - это просто Jupyter notebook чисто для пайтона
        """
        # Импортируем класс SVG для отображения картинок в Jupyter
        from IPython.display import SVG
        dot_data = self.to_dot()
        try:
            process = subprocess.run(
                ['dot', '-Tsvg'],
                input=dot_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return SVG(data=process.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Graphviz 'dot' command failed: {e} with stderr: {e.stderr.decode('utf-8')}") from e
        

"""
        from IPython.display import SVG
        def to_image(self):
            dot_data = self.to_dot()
            try:
                process = subprocess.run(
                    ['dot', '-Tsvg'],
                    input=dot_data,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                svg_data = process.stdout
                with open("graph.svg", "w", encoding="utf-8") as f:
                    f.write(svg_data)
                print("SVG файл сохранён как graph.svg")
                return "graph.svg"
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Graphviz 'dot' command failed: {e} with stderr: {e.stderr}") from e
"""

# блок кода, который выполняется только в случае запуска кода именно в этом файле
if __name__ == "__main__":
    # Create a directed graph
    g = Graph(GraphType.DIRECTED)

    # Add nodes with attributes
    # вот эта часть {"label": "Optional", "color": "blue"} отвечает за Any при создании словарей
    # "A" это ключ, айди, str, хз короч
    g.add_node("A", {"label": "Start", "color": "green"})
    g.add_node("B", {"label": "Middle", "color": "yellow"})
    g.add_node("C", {"label": "End", "color": "red"})
    g.add_node("D", {"label": "Optional", "color": "blue"})

    # Add edges with attributes
    # weight — вес ребра, числовое значение (например, расстояние, стоимость, сила связи)
    g.add_edge("A", "B", {"weight": 1.0, "type": "normal"})
    g.add_edge("B", "C", {"weight": 2.5, "type": "critical"})
    # необязательный, можно вообще не использовать
    g.add_edge("A", "D", {"weight": 0.8, "type": "optional"})
    # fallback - запасной вариант, аварийный, включается только если основной вариант не сработал
    g.add_edge("D", "C", {"weight": 1.7, "type": "fallback"})


    # Access and update node attribute
    print("Node A color:", g.node("A")["color"])
    # по скелету self._attrs[item] = val, который мы прописали в классе Node, фукнция def __setitem__
    g.node("A")["color"] = "darkgreen"

    # Access edge and modify its weight
    # ВОТ ТУТ МЫ ПОМЕНЯЛИ С 1.0 НА 1.1   !!!!!
    edge = g.node("A").to("B")
    print("Edge A→B weight:", edge["weight"])
    # the same по скелету self._attrs[key] = val, кот была прописана в классе Edge, функция def __setitem__ (встроенная если что)
    #edge["weight"] = 1.1

    # Iterate through the graph
    # Перебираем все узлы графа
    print("\nGraph structure:")
    for node_id in g.node_ids():
        node = g.node(node_id)
        # node.out_degree - количество исходящих рёбер
        print(f"Node {node.id}: label={node['label']}, out_degree={node.out_degree}")
        for neighbor_id in node.neighbor_ids:
            edge = node.to(neighbor_id)
            print(f"  → {neighbor_id} (weight={edge['weight']}, type={edge['type']})")

    print("-----------------")
    print(g.export_to_png("graph.png"))
    # g.to_image() возвращает объект для Jupyter, so that's why we don't need it
    #print(g.to_image())