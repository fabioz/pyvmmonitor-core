import io

from pyvmmonitor_core.nodes_tree import NodesTree, Node


def test_nodes_tree():
    nodes_tree = NodesTree()
    node = nodes_tree.add_child(Node(1))
    node2 = node.add_child(Node(2))
    node2.add_child(Node(3))
    nodes_tree.add_child(Node(4))

    stream = io.StringIO()
    stream.write(u'\n')
    nodes_tree.print_rep(stream=stream)
    assert stream.getvalue() == u'''
int: 1
  int: 2
    int: 3
int: 4
'''.replace('\r\n', '\n').replace('\r', '\n')

    assert len(nodes_tree) == 4