import unittest

from sources.gloaders.dybench_loader import DybenchLoader
from sources.dynamic_community_tracking import DynamicCommunityTraking


class TestDybench(unittest.TestCase):

    def setUp(self):
        self.dybench = DybenchLoader(tgraph_path="datasets/merge100.tgraph", tcomms_path="datasets/merge100.tcomms")

    def test_whole(self):
        tracker = DynamicCommunityTraking(self.dybench)
        d_coms = tracker.find_events()


if __name__ == '__main__':
    unittest.main()
