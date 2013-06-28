# coding: utf-8
import sys
from tempfile import mkdtemp
from time import sleep
from threading import Thread


CONSOLE_HELP_TEXT = '''After each step, a prompt will be shown.
On the prompt, you can just press Enter to continue to the next step.
But you can also have this commands:
(write the command you want to use and then press Enter)
* h: get help.
* g PATH_TO_PNG_IMAGE: create png with graph of the current state.
* e: run non-interactively to the end of the algorithm.
* s: show statistics of the execution (max fringe size, visited nodes).
* q: quit program.'''


class BaseViewer(object):
    def __init__(self, multiple_runs=False):
        self.multiple_runs = multiple_runs

        self.successor_color = '#DD4814'
        self.fringe_color = '#20a0c0'
        self.font_size = 11

        self.clean()

    def clean(self):
        self.last_event = '', ''
        self.events = []

        self.max_fringe_size = 0
        self.visited_nodes = 0

        self.current_fringe = []
        self.last_chosen = None
        self.last_is_goal = False
        self.last_expandeds = []
        self.last_successors = []

    def event(self, event, description):
        self.last_event = event, description
        self.events.append((event, description))

    def started(self):
        self.event('started', 'Algorithm just started.')

    def new_iteration(self, fringe):
        self.current_fringe = fringe
        self.max_fringe_size = max(self.max_fringe_size, len(fringe))

        description = 'New iteration with %i elements in the fringe:\n%s'
        description = description % (len(fringe), str(fringe))
        self.event('new_iteration', description)

    def chosen_node(self, node, is_goal=None):
        self.last_chosen, self.last_is_goal = node, is_goal
        self.visited_nodes += 1

        goal_text = 'Is goal!' if is_goal else 'Not goal'
        description = 'Chosen node: %s' % node
        if is_goal is not None:
            description += '\n' + goal_text
        self.event('chosen_node', description)

    def expanded(self, nodes, successors):
        self.last_expandeds, self.last_successors = nodes, successors

        description = 'Expanded %s\nSuccessors: %s'
        description = description % (nodes, successors)
        self.event('expanded', description)

    def finished(self, fringe, node, solution_type):
        self.current_fringe = fringe
        self.solution_node = node
        self.solution_type = solution_type

        if self.multiple_runs:
            description = 'Finished one of the runs of the inner algorithm returning %s\nSolution type: %s'
        else:
            description = 'Finished algorithm returning %s\nSolution type: %s'
        description = description % (node, solution_type)

        if node is not None and node.parent is not None:
            description += '\nPath from initial to goal: %s' % str(node.path())
        self.event('finished', description)

    def no_more_runs(self, node, solution_type):
        self.solution_node = node
        self.solution_type = solution_type

        description = 'Finished all of the runs of the inner algorithm returning %s\nSolution type: %s'
        description = description % (node, solution_type)

        if node is not None and node.parent is not None:
            description += '\nPath from initial to goal: %s' % str(node.path())
        self.event('no_more_runs', description)

    def create_graph(self, image_format, image_path):
        from pydot import Dot, Edge, Node

        graph = Dot(graph_type='digraph')

        graph_nodes = {}
        graph_edges = {}
        done = set()

        def add_node(node, expanded=False, chosen=False, in_fringe=False,
                     in_successors=False):
            node_id = id(node)
            if node_id not in graph_nodes:
                label = node.state_representation()
                if hasattr(node, 'cost'):
                    label += '\nCost: %s' % node.cost
                if hasattr(node, 'heuristic'):
                    label += '\nHeuristic: %s' % node.heuristic
                if hasattr(node, 'value'):
                    label += '\nValue: %s' % node.value

                new_g_node = Node(node_id,
                                  label=label,
                                  style='filled',
                                  shape='circle',
                                  fillcolor='#ffffff',
                                  fontsize=self.font_size)

                graph_nodes[node_id] = new_g_node

            g_node =  graph_nodes[node_id]

            if expanded or chosen:
                g_node.set_fillcolor(self.fringe_color)
            if in_fringe:
                g_node.set_color(self.fringe_color)
                g_node.set_penwidth(3)
            if in_successors:
                g_node.set_color(self.successor_color)
                g_node.set_fontcolor(self.successor_color)

            return g_node

        def add_edge_to_parent(node, is_successor=False, parent=None):
            if parent is None:
                parent = node.parent

            g_node = add_node(node, in_successors=is_successor)
            g_parent_node = add_node(parent)

            edge = Edge(g_parent_node,
                        g_node,
                        label=node.action_representation(),
                        fontsize=self.font_size)

            if is_successor:
                edge.set_color(self.successor_color)
                edge.set_labelfontcolor(self.successor_color)

            graph_edges[id(node), id(parent)] = edge

        if self.last_event[0] == 'chosen_node':
            add_node(self.last_chosen, chosen=True)

        if self.last_event[0] == 'expanded':
            for node, successors in zip(self.last_expandeds,
                                        self.last_successors):
                add_node(node, expanded=True)
                for successor_node in successors:
                    add_edge_to_parent(successor_node,
                                       is_successor=True,
                                       parent=node)

        for node in self.current_fringe:
            add_node(node, in_fringe=True)
            while node is not None and node not in done:
                if node.parent is not None:
                    add_edge_to_parent(node)
                else:
                    add_node(node)

                done.add(node)
                node = node.parent

        for node_id in sorted(graph_nodes.keys()):
            graph.add_node(graph_nodes[node_id])
        for node_id, parent_id in sorted(graph_edges.keys()):
            graph.add_edge(graph_edges[node_id, parent_id])

        method = getattr(graph, 'write_' + image_format)
        method(image_path)

# TODO output_enabled desaparecio

class ConsoleViewer(BaseViewer):
    def __init__(self, interactive=True):
        super(ConsoleViewer, self).__init__()
        self.interactive = interactive

    def event(self, event, description):
        super(ConsoleViewer, self).event(event, description)

        self.output('EVENT: %s' % event)
        self.output(description)

        self.pause()

    def started(self):
        self.output(CONSOLE_HELP_TEXT)
        super(ConsoleViewer, self).started()

    def pause(self):
        prompt = True
        while prompt and self.interactive:
            prompt = False
            option = raw_input('> ').strip()
            if option:
                if option == 'h':
                    self.output(CONSOLE_HELP_TEXT)
                    prompt = True
                elif option == 'e':
                    self.interactive = False
                elif option == 's':
                    self.output('Statistics:')
                    self.output('Max fringe size: %i' % self.max_fringe_size)
                    self.output('Visited nodes: %i' % self.visited_nodes)
                    prompt = True
                elif option == 'q':
                    sys.exit()
                elif option.startswith('g ') and len(option) > 2:
                    png_path = option[2:]
                    self.create_graph('png', png_path)
                    self.output('graph saved to %s' % png_path)
                    prompt = True
                else:
                    self.output('Incorrect command')
                    self.output(CONSOLE_HELP_TEXT)
                    self.pause()

    def output(self, text):
        print text

# TODO como frenar la ejecucion para que sea paso a paso?

class WebViewer(BaseViewer):
    def __init__(self, host='127.0.0.1', port=8000):
        super(WebViewer, self).__init__()
        self.host = host
        self.port = port
        self.tmp_folder = mkdtemp(prefix='simpleai_web_server_')
        self.status = 'paused'

    def event(self, event, description):
        super(WebViewer, self).event(event, description)
        self.create_graph('svg', 'graph.svg')

        if self.status == 'running_step':
            self.status = 'paused'

        while self.status == 'paused':
            sleep(0.5)

    def started(self):
        from web_viewer_server import get_server
        app = get_server(self)

        t = Thread(target=app.run, kwargs=dict(host=self.host, port=self.port))
        t.daemon = True
        t.start()

        super(WebViewer, self).started()
