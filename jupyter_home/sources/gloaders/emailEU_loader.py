import igraph
import pandas

from sources.gloaders.loader_interface import LoaderInterface


class EmailEULoader(LoaderInterface):

    @classmethod
    def read_graph_file(cls, path: str) -> (list, int, int, int):
        net_matrix = pandas.read_table(path, sep='\s+', header=None, names=['node1', 'node2', 'time'])

        tss = net_matrix.time.unique()

        set_node1 = set(net_matrix.loc[net_matrix.time == 0].node1)
        set_node2 = set(net_matrix.loc[net_matrix.time == 0].node2)
        total_node = len(set_node1.union(set_node2))

        total_edges = net_matrix.loc[net_matrix.time == 0].shape[0]

        snapshots = []
        for t in tss:
            snapshots.append(EmailEULoader._graph_for_timestamp(net_matrix, t))

        return snapshots, total_node, total_edges

    @classmethod
    def _graph_for_timestamp(cls, net_matrix: pandas.DataFrame, t: int):
        matrix_t = net_matrix.loc[net_matrix['time'] == t]
        del matrix_t['time']
        tuples = matrix_t.itertuples(index=False, name=None)

        return igraph.Graph.TupleList(tuples, weights=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_datatset(self, **kwargs):
        snapshots, nnodes, nedges = EmailEULoader.read_graph_file(kwargs["tgraph_path"])

        n_ts = len(snapshots)
        n_nodes = [nnodes]*n_ts
        n_edges = [nedges]*n_ts

        communities = None
        n_comms = None

        info = {
            "dataset_file": kwargs["tgraph_path"],
            "snapshot_count": n_ts,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "ground_truth": False
        }
        return snapshots, n_ts, n_nodes, n_edges, info, communities, n_comms

