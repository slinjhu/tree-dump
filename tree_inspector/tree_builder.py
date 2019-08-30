from tree_inspector.options import Options
from typing import Any, List, NamedTuple, Dict
import numpy
import enum


def get_type_name(o):
    short = o.__class__.__name__
    module = o.__class__.__module__
    if module == 'numpy' and short == 'void':
        return o.dtype, o.dtype
    else:
        return short, module + '.' + short


def is_primitive(obj: Any) -> bool:
    return obj is None \
           or issubclass(type(obj), enum.Enum) \
           or type(obj) in [str, float, int, bool, bytes, complex]


class TreeNode(NamedTuple):
    name: str
    short_type: str
    full_type: str
    value: str = 'value not given'
    children: List['TreeNode'] = []
    open: bool = False

    @staticmethod
    def simple(name: str, obj: Any) -> 'TreeNode':
        short_type, full_type = get_type_name(obj)
        return TreeNode(name=name, short_type=short_type, full_type=full_type, value=str(obj))



class TreeBuilder:
    def __init__(self, options: Options = Options()):
        self.options = options

    def _node_list(self, name: str, obj: List[Any]) -> TreeNode:
        if len(obj) == 0:
            return TreeNode.simple(name, obj)
        else:
            elm_short_type, elm_full_type = get_type_name(obj[0])
            return TreeNode(name=name,
                            short_type=f'list[{elm_short_type}]',
                            full_type=f'list[{elm_full_type}]',
                            children=[self.node(str(i), v) for i, v in enumerate(obj)
                                      if i < self.options.max_elements_to_show_in_list],
                            value=f'Length {len(obj)}')

    def _node_dict(self, name: str, obj: Dict[Any, Any]) -> TreeNode:
        if len(obj) == 0:
            return TreeNode.simple(name, obj)
        else:
            children = []
            cnt = 0
            for k, v in obj.items():
                cnt += 1
                children.append(self.node(str(k), v))
                if cnt >= self.options.max_elements_to_show_in_dict:
                    break
            return TreeNode(name=name, short_type='dict', full_type='dict',
                            value=f'Size {len(obj)}', children=children)

    def _node_class(self, name: str, obj: Any) -> TreeNode:
        if hasattr(obj, '__dict__'):
            short_type, full_type = get_type_name(obj)
            return TreeNode(name=name,
                            short_type=short_type,
                            full_type=full_type,
                            value=f'{len(obj.__dict__)} fields',
                            children=[self.node(str(k), v) for k, v in obj.__dict__.items()],
                            open=True)
        else:
            return TreeNode.simple(name, obj)

    def _node_numpy_ndarray(self, name: str, obj: numpy.ndarray) -> TreeNode:
        return TreeNode(name=name,
                        short_type=f'ndarray[{obj.dtype}]',
                        full_type=f'numpy.ndarray[{obj.dtype}]',
                        value=str(obj) if obj.size == 0 else f'Shape {obj.shape}',
                        children=[self.node(str(i), obj[i]) for i in range(0, obj.shape[0]) if i < self.options.max_elements_to_show_in_list])

    def node(self, name: str, obj: Any) -> TreeNode:
        """
        Render a Python object as html.
        :param obj: The object to be rendered; Could be of any type
        :param name: variable name or any string label for the given object
        :return: html string
        """
        if is_primitive(obj):
            return TreeNode.simple(name, obj)
        elif type(obj) == dict:
            return self._node_dict(name, obj)
        elif type(obj) == list:
            return self._node_list(name, obj)
        elif type(obj) == numpy.ndarray:
            return self._node_numpy_ndarray(name, obj)
        else:
            return self._node_class(name, obj)


