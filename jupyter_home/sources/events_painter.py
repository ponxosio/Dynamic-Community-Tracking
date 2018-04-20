import igraph

from typing import List
from typing import Tuple

STEP_COM = Tuple[List[str], int, str]
DY_COMMS = List[List[STEP_COM]]


class EventsPainter:

    @classmethod
    def split_by_ts(cls, comm_events):
        events_by_ts = []
        accumulate = []
        last_ts = 0
        for event in comm_events:
            ts = event[1]
            if ts > last_ts:
                events_by_ts.append(accumulate)
                accumulate = []

            accumulate.append(event)
            last_ts = ts

        events_by_ts.append(accumulate)
        return events_by_ts

    def __init__(self, dynamic_coms: DY_COMMS):
        self.dynamic_coms = dynamic_coms

    def make_events_graph(self):
        g = igraph.Graph(directed=True)

        for i in range(len(self.dynamic_coms)):
            check = False
            if i != 0:
                check = True
            self._add_nodes(g, i, check)
        return g

    def _add_nodes(self, g: igraph.Graph, com_id: int, check: bool):
        events_by_ts = EventsPainter.split_by_ts(self.dynamic_coms[com_id])

        prev_i = None
        for i in range(len(events_by_ts)):
            events = events_by_ts[i]
            added_names = []
            for event in events:
                ts = event[1]
                idcom = str(set(event[0]))
                idn = "{0}-{1}".format(ts, idcom)
                name = "C{0}.{1}".format(com_id, ts)
                added_names.append((idn, event[2]))

                if check:
                    found = g.vs.select(name=idn)
                    if len(found) == 0:
                        g.add_vertex(name=idn, label=name)
                else:
                    g.add_vertex(name=idn, label=name)

            if prev_i is not None:
                events = events_by_ts[prev_i]
                for event in events:
                    ts = event[1]
                    idcom = str(set(event[0]))
                    idn_s = "{0}-{1}".format(ts, idcom)

                    for idn_t, e_label in added_names:
                        g.add_edge(idn_s, idn_t, label=e_label)
            prev_i = i
