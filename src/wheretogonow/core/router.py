"""Implemenation of routing algorithm.

We assume that evaluation of each node and time of each node & each edge
is given. Currently, 'point' of the path is given as

point = sum of (eval of v) * weight_eval_nodes for nodes v in P
      + sum of (time of v) * weight_time_nodes for nodes v in P
      + sum of (time of e) * weight_time_edges for edges e in P
"""

import heapq
from operator import attrgetter

infinity_pos = float('inf')
infinity_neg = float('-inf')


# ============================================================

class Graph(object):
    def __init__(self, num_nodes):
        """Constructor."""
        # Nodes: V = {0, 1, ..., (num_nodes - 1)}
        # Edges: E = {i, j in V | (i -> j)}
        self.num_nodes = num_nodes
        self.time_nodes = [0] * self.num_nodes
        self.eval_nodes = [0] * self.num_nodes

        # If we initialize the 2D list like A = [[x] * w] * h,
        # every row points to the same object ([x] * w) and we're screwed.
        # (Changing an element of any row will affect other rows too.)
        self.time_edges = [[0] * self.num_nodes
                           for _ in range(self.num_nodes)]


# ============================================================

class Path(object):
    def __init__(self, graph, nodes, initialize=True):
        """Constructor."""
        self.graph = graph
        self.nodes = nodes
        self.length = len(nodes)
        self.time = 0
        self.point = 0

        if not initialize:
            return

        # calculate the time and the point
        # (1) for each node v
        for i in xrange(self.length):
            v = self.nodes[i]

            self.time += self.graph.time_nodes[v]
            self.point += self.graph.eval_nodes[v]

        # (2) for each edge (v_1 -> v_2)
        for i in xrange(self.length - 1):
            v_1, v_2 = self.nodes[i], self.nodes[i + 1]

            self.time += self.graph.time_edges[v_1][v_2]

    def add_node(self, pos, v):
        """Add `v` at position `pos`."""
        self.nodes.insert(pos, v)
        self.length += 1

        v_prev = self.nodes[pos - 1]
        v_next = self.nodes[pos + 1]

        # (1) add the node v
        self.time += self.graph.time_nodes[v]
        self.point += self.graph.eval_nodes[v]

        # (2) add the edges (v_prev -> v) and (v -> v_next)
        self.time += self.graph.time_edges[v_prev][v] \
            + self.graph.time_edges[v][v_next]

        # (3) remove the edge (v_prev -> v_next)
        self.time -= self.graph.time_edges[v_prev][v_next]

    def copy(self):
        """Copy the path. (Reuse the time and the point.)"""
        path_copy = Path(self.graph, self.nodes[:], initialize=False)
        path_copy.time = self.time
        path_copy.point = self.point

        return path_copy

    def __repr__(self):
        return '[' + ' -> '.join('%d' % v for v in self.nodes) + ']'


# ============================================================

class Router(object):
    def __init__(self, graph, verbose=False):
        """Constructor."""
        self.graph = graph
        self.verbose = verbose

    def find_best_path(self, v_start, v_end, list_max, length_max, time_max):
        def_path = Path(self.graph, [v_start, v_end])
        plist = [def_path]

        if self.verbose:
            print('> %s\n  (Point: %.3f, Time: %.3f)'
                  % (def_path, def_path.point, def_path.time))

        for i in xrange(length_max - 2):
            plist_prev = plist
            plist = self.find_next_path(plist, list_max, time_max)

            if self.verbose:
                for path in plist:
                    print('> %s\n  (Point: %.3f, Time: %.3f)'
                          % (path, path.point, path.time))

            # if plist is empty -> try to use the previous one
            if not plist:
                plist = plist_prev

        return plist

    def find_next_path(self, plist, list_max, time_max):
        """Given a list of path, try to add a node in the middle of the path.
        Add it to update the list.
        """
        plist_new = []

        for path in plist:
            not_used = [True] * self.graph.num_nodes

            for v in path.nodes:
                not_used[v] = False

            for v in xrange(self.graph.num_nodes):
                if not_used[v]:
                    path_best = None
                    time_best = infinity_pos

                    for pos in xrange(1, path.length):
                        path_new = path.copy()
                        path_new.add_node(pos, v)

                        if path_new.time > time_max:
                            continue

                        if path_new.time < time_best:
                            path_best = path_new
                            time_best = path_new.time

                        success = True

                        for path_tmp in plist_new:
                            if set(path_tmp.nodes) == set(path_best.nodes):
                                if path_tmp.time < path_best.time:
                                    path_best = path_tmp

                                success = False
                                break

                        if success:
                            plist_new.append(path_best)

        return heapq.nlargest(list_max, plist_new, key=attrgetter('point'))
