from os. path import join
from abc import ABCMeta, abstractmethod
from random import randint

import igraph
import numpy as np

import sources.gloaders.distribution_colors as dcolors


class LoaderInterface:
    _metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        snapshots, n_ts, n_nodes, n_edges, info, communities, n_comms = self.load_datatset(**kwargs)

        self.snapshots = snapshots
        self.n_ts = n_ts
        self.n_nodes = n_nodes
        self.n_edges = n_edges

        self.communities = communities
        self.n_comms = n_comms
        self.info = info

        if communities:
            self.available_colors = ['#%06X' % randint(0, 0xFFFFFF) for _ in range(self.n_comms)]
            # self.available_colors = ['green', 'red', 'blue', 'yellow']

    def get_snapshots(self, n_ts_min=0, n_ts_max=-1):
        end = n_ts_max if n_ts_max > 0 else self.n_ts
        return self.snapshots[n_ts_min:end]

    def get_communities(self, n_ts_min=0, n_ts_max=-1):
        end = n_ts_max if n_ts_max > 0 else self.n_ts
        return self.communities[n_ts_min:end]

    def get_dataset_info(self):
        return self.info

    @abstractmethod
    def load_datatset(self, **kwargs) -> (list, int, list, list): raise NotImplementedError

    def save_graphs_img(self, path: str, n_ts_min=0, n_ts_max=-1):
        end = n_ts_max if n_ts_max > 0 else self.n_ts
        snapshots = self.snapshots[n_ts_min:end]

        for i in range(len(snapshots)):
            img_path = join(path, "snapshot_{0}.png".format(i))

            for v in snapshots[i].vs:
                if self.communities:
                    node_id = int(v["name"])
                    community_id = int(self.communities[i][node_id])
                    v['color'] = self.available_colors[community_id]
                else:
                    v['color'] = 'green'

            visual_style = {"bbox": (800, 600), "margin": 60, "vertex_size": 8, "vertex_label_size": 24,
                            "vertex_color": snapshots[i].vs['color'], "edge_width": 0.5,
                            "layout": snapshots[i].layout_auto(), "vertex_label": snapshots[i].vs["name"]}

            igraph.plot(snapshots[i], img_path, **visual_style)

    def plot_neighbors_change_ts(self, axs, axs_legend, n_ts_min=0, n_ts_max=-1):
        width = 100

        end = n_ts_max if n_ts_max > 0 else self.n_ts
        snapshots = self.snapshots[n_ts_min:end]
        n_ts = len(snapshots)

        med = []
        xs = []
        scales = []
        for s_i in range(1, n_ts):
            nodes_changes = []
            for i in range(snapshots[s_i].vcount()):
                n1 = snapshots[s_i].vs[i]
                n2 = snapshots[s_i - 1].vs.select(name=n1["name"])
                if len(n2) > 0:
                    n2 = n2[0]
                    s1 = set([x["name"] for x in n1.neighbors()])
                    s2 = set([x["name"] for x in n2.neighbors()])

                    missing_value = (len(s1.difference(s2)) / len(s1)) * 100.0
                    missing_value = round(missing_value)
                    nodes_changes.append(missing_value)

            values, classes = np.histogram(nodes_changes, bins=10)
            values = values/len(nodes_changes)

            n_classes = []
            n_values = []
            for i in range(len(values)):
                if values[i] > 0.0:
                    n_classes.append(classes[i])
                    n_values.append(values[i])

            med.extend(n_classes)
            xs.extend([s_i]*len(n_classes))
            scales.extend(n_values)

        colors = np.zeros(len(scales)*3).reshape(len(scales), 3)
        for i in range(len(scales)):
            colors[i,:] = dcolors.select_color_10(scales[i])

        axs.scatter(xs, med, c=colors, edgecolors='#252525', marker='s', s=width)
        axs.set_xlabel("id timestamp")
        axs.set_ylabel("% of missing neighbors")

        dcolors.print_legend_10(axs_legend)

    def plot_missing_nodes(self, axs, n_ts_min=0, n_ts_max=-1):
        width = 0.8
        end = n_ts_max if n_ts_max > 0 else (self.n_ts + 1)
        snapshots = self.snapshots[n_ts_min:end]
        n_ts = len(snapshots)

        med = np.zeros(n_ts - 1)
        for s_i in range(1, n_ts):
            n1 = set(snapshots[s_i].vs["name"])
            n2 = set(snapshots[s_i-1].vs["name"])

            med[s_i-1] = len(n1.difference(n2))/len(n1) * 100

        axs.bar(range(1, n_ts), med, width)
        axs.axhline(np.median(med), color="orange")

        for i in range(n_ts-1):
            axs.text(i + width, med[i], "{0: .2f}".format(med[i]))

        axs.set_xlabel("id timestamp")
        axs.set_ylabel("% node change")

    def plot_number_nodes_ts(self, axs,  n_ts_min=0, n_ts_max=-1):
        width = 0.8
        end = n_ts_max if n_ts_max > 0 else (self.n_ts + 1)
        snapshots = self.snapshots[n_ts_min:end]
        n_ts = len(snapshots)

        new_nodes = np.zeros(n_ts)
        for s_i in range(1, n_ts):
            n1 = set(snapshots[s_i].vs["name"])
            n2 = set(snapshots[s_i - 1].vs["name"])

            ts_new = n1.difference(n2)
            new_nodes[s_i] = len(ts_new)

        sizes = np.array(self.n_nodes[n_ts_min:end])
        continuous_nodes = sizes - new_nodes

        p1 = axs.bar(range(n_ts), continuous_nodes, width)
        p2 = axs.bar(range(n_ts), new_nodes, width, bottom=continuous_nodes)

        axs.legend((p1[0], p2[0]), ('Old', 'New'))

        axs.set_xlabel("id timestamp")
        axs.set_ylabel("number of new/old nodes")
