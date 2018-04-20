from typing import Dict
from typing import List
from typing import Tuple

from sources.gloaders.loader_interface import LoaderInterface
from sources.metrics import jaccard_coefficient


STEP_COM = Tuple[List[str], int, str]
DY_COMMS = List[List[STEP_COM]]
FRONT = Dict[int, Tuple[List[str], int]]


class DynamicCommunityTraking:

    @classmethod
    def _add_new_dcomm(cls, dynamic_community: DY_COMMS, last_index: int, ts:int, comm: List[str], event="birth") -> int:

        index = last_index + 1
        dynamic_community.append([(comm, ts, event)])
        return index

    @classmethod
    def _one_to_one_match(cls,  dynamic_community: DY_COMMS, community: List[str], com_match: int, ts: int):
        front = {}
        last_step_com, _, _ = dynamic_community[com_match][-1]

        ratio = len(community) / len(last_step_com)
        if ratio > 1.1:
            # grow
            dynamic_community[com_match].append((community, ts, "grow"))
        elif ratio < 0.9:
            dynamic_community[com_match].append((community, ts, "contraction"))
        else:
            dynamic_community[com_match].append((community, ts, "stay"))

        front[com_match] = (community, ts)
        return front

    @classmethod
    def _process_split(cls, dynamic_community: DY_COMMS, step_community: List[str], community_index: int,
                       last_index: int, ts: int) -> (FRONT, int):
        last_index += 1

        t_aux = dynamic_community[community_index][-1]
        dynamic_community[community_index][-1] = (t_aux[0], t_aux[1], "split")

        dynamic_community.append([dynamic_community[community_index][-2]])
        dynamic_community[last_index].append((step_community, ts, "split"))

        front = {
            last_index: (step_community, ts)
        }
        return front, last_index

    def __init__(self, temporal_network: LoaderInterface, threshold=0.3, steps_to_die=3):

        self.temporal_network = temporal_network
        self.threshold = threshold
        self.steps_to_die = steps_to_die

    def find_events(self, n_ts_min=0, n_ts_max=-1):

        snapshots = self.temporal_network.get_snapshots(n_ts_min, n_ts_max)
        n_ts = len(snapshots)

        d_communities = []
        front = {}

        actual_snapshot = snapshots[0]
        for i, comm in enumerate(actual_snapshot.community_infomap()):
            comms_name = [actual_snapshot.vs[index]["name"] for index in comm]
            d_communities.append([(comms_name, 0, "birth")])
            front[i] = (comms_name, 0)

        last_c_index = i

        for ts in range(1, n_ts):
            actual_snapshot = snapshots[ts]
            front_temporal = {}
            already_matched = set()

            for comm in actual_snapshot.community_infomap():
                comms_name = [actual_snapshot.vs[index]["name"] for index in comm]
                matched_comms = self._match_community_front(front, comms_name)

                if len(matched_comms) == 0:
                    # Add new d community
                    last_c_index = DynamicCommunityTraking._add_new_dcomm(d_communities, last_c_index, ts, comms_name)
                    front_temporal[last_c_index] = (comms_name, ts)

                elif len(matched_comms) == 1:

                    dcomm_pair = matched_comms[0]
                    if dcomm_pair in already_matched:
                        # splitting
                        update_front, new_index = DynamicCommunityTraking._process_split(d_communities, comms_name,
                                                                                         dcomm_pair, last_c_index, ts)
                        last_c_index = new_index
                    else:
                        # grow, expansion, contraction
                        update_front = DynamicCommunityTraking._one_to_one_match(d_communities, comms_name, dcomm_pair,
                                                                                 ts)
                    already_matched.add(dcomm_pair)
                    front_temporal.update(update_front)
                else:
                    # merging
                    update_front = self._process_merge(d_communities, comms_name, matched_comms, ts)
                    front_temporal.update(update_front)

            # update front
            front.update(front_temporal)
            self._process_dead_communities(d_communities, front, ts)

        return d_communities

    def _match_community_front(self, front: FRONT, community: List[str]) -> List[int]:

        matched = []
        for dcom_id in front.keys():
            front_comm, _ = front[dcom_id]
            jaccard = jaccard_coefficient(front_comm, community)
            if jaccard > self.threshold:
                matched.append(dcom_id)

        return matched

    def _process_dead_communities(self, dynamic_community: DY_COMMS, front: FRONT, ts: int) -> None:

        keys_to_remove = []
        for comm_id in front.keys():
            comm_memebers, last_ts = front[comm_id]

            if last_ts < 0:
                keys_to_remove.append(comm_id)
            elif (ts - last_ts) >= self.steps_to_die:
                keys_to_remove.append(comm_id)
                dynamic_community[comm_id].append((comm_memebers, ts, "death"))

        for key in keys_to_remove:
            del front[key]

    def _process_merge(self, dynamic_community: DY_COMMS, community: List[str], matches: List[int], ts: int) -> FRONT:
        front = {}

        d_com_index_stay = min(matches)
        front[d_com_index_stay] = (community, ts)
        dynamic_community[d_com_index_stay].append((community, ts, "merge-main"))

        for d_com_index in matches:
            if d_com_index != d_com_index_stay:
                front[d_com_index] = (community, -self.steps_to_die)
                dynamic_community[d_com_index].append((community, ts, "merge-end"))

        return front
