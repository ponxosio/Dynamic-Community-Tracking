from datetime import date, datetime, timedelta

import pandas
import igraph

from sources.gloaders.loader_interface import LoaderInterface


class EnronLoader(LoaderInterface):

    @classmethod
    def _remove_isolated_nodes(cls, graph: igraph.Graph):
        nodes_to_delete = []
        for v in graph.vs:
            if v.degree(mode=igraph.ALL) == 0:
                nodes_to_delete.append(v.index)
        graph.delete_vertices(nodes_to_delete)

    @classmethod
    def _make_graph(cls, table: pandas.DataFrame, init_d: datetime, end_d: datetime):
        t = table[(table['timestamp'] >= str(init_d)) & (table['timestamp'] <= str(end_d))]
        del t['timestamp']

        tuples = t.itertuples(index=False, name=None)
        graph = igraph.Graph.TupleList(tuples, weights=False)
        EnronLoader._remove_isolated_nodes(graph)

        return graph

    @classmethod
    def _load_enron(cls, file_path: str, init_date: date, end_date: date, duration_snapshot: timedelta,
                    overlap: timedelta):

        t = pandas.read_csv(file_path)
        t = t[(t['timestamp'] >= str(init_date)) & (t['timestamp'] <= str(end_date))]

        snapshots = []
        n_nodes = []
        n_edges = []

        # make date into datetime
        last_t = init_date + overlap

        while last_t < end_date:
            g_snapshot = EnronLoader._make_graph(t, last_t - overlap, last_t + duration_snapshot)
            snapshots.append(g_snapshot)
            n_nodes.append(g_snapshot.vcount())
            n_edges.append(g_snapshot.ecount())

            last_t += duration_snapshot

        return snapshots, n_nodes, n_edges

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_datatset(self, **kwargs) -> (list, int, list, list):
        snapshots, n_nodes, n_edges = EnronLoader._load_enron(kwargs["file"], kwargs["init_date"], kwargs["end_date"],
                                                              kwargs["duration_snapshot"], kwargs["overlap"])
        n_ts = len(snapshots)
        communities = None
        n_comms = None

        info = {
            "dataset_file": kwargs["file"],
            "init_date": str(kwargs["init_date"]),
            "end_date": str(kwargs["end_date"]),
            "duration_snapshot": str(kwargs["duration_snapshot"]),
            "snapshot_count": n_ts,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "ground_truth": False,
            "memebers": communities,
            "n_communites": n_comms
        }
        return snapshots, n_ts, n_nodes, n_edges, info, communities, n_comms
