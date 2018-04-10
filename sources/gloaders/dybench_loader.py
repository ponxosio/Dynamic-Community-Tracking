import igraph
import pandas

from sources.gloaders.loader_interface import LoaderInterface


class DybenchLoader(LoaderInterface):

    @classmethod
    def read_graph_file(cls, path: str) -> (list, int, int, int):
        net_matrix = pandas.read_table(path, sep='\s+', header=None, names=['node1', 'node2', 'weight', 'time'])
        del net_matrix['weight']

        tss = net_matrix.time.unique()

        set_node1 = set(net_matrix.loc[net_matrix.time == 0].node1)
        set_node2 = set(net_matrix.loc[net_matrix.time == 0].node2)
        total_node = len(set_node1.union(set_node2))

        total_edges = net_matrix.loc[net_matrix.time == 0].shape[0]

        snapshots = []
        for t in tss:
            snapshots.append(DybenchLoader._graph_for_timestamp(net_matrix, t))

        return snapshots, total_node, total_edges

    @classmethod
    def read_tcomm_file(cls, path: str):
        comms_matrix = pandas.read_table(path, sep='\s+', header=None, names=['time', 'node', 'communities'])
        tss = comms_matrix.time.unique()

        n_comms = len(comms_matrix.communities.unique())

        members = []
        for t in tss:
            members.append(DybenchLoader._communities_for_timestamp(comms_matrix, t))
        return members, n_comms

    @classmethod
    def _communities_for_timestamp(cls, comms_matrix: pandas.DataFrame, t: int):
        matrix_t = comms_matrix.loc[comms_matrix['time'] == t]
        del matrix_t['time']

        node_count = matrix_t.shape[0]
        memberships = [None] * node_count

        tuples = matrix_t.itertuples(index=False, name=None)
        for node, community in tuples:
            memberships[int(node)] = int(community)
        return memberships

    @classmethod
    def _graph_for_timestamp(cls, net_matrix: pandas.DataFrame, t: int):
        matrix_t = net_matrix.loc[net_matrix['time'] == t]
        del matrix_t['time']
        tuples = matrix_t.itertuples(index=False, name=None)

        return igraph.Graph.TupleList(tuples, weights=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load_datatset(self, **kwargs):
        snapshots, nnodes, nedges = DybenchLoader.read_graph_file(kwargs["tgraph_path"])

        n_ts = len(snapshots)
        n_nodes = [nnodes]*n_ts
        n_edges = [nedges]*n_ts

        communities, n_comms = DybenchLoader.read_tcomm_file(kwargs["tcomms_path"])
        communities = communities
        n_comms = n_comms

        info = {
            "dataset_file": kwargs["tgraph_path"],
            "snapshot_count": n_ts,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "ground_truth": True,
            "memebers": communities,
            "n_communites": n_comms
        }
        return snapshots, n_ts, n_nodes, n_edges, info, communities, n_comms

