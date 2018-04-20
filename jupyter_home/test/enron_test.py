import unittest

from datetime import date, timedelta

from sources.gloaders.enron_loader import EnronLoader
from sources.dynamic_community_tracking import DynamicCommunityTraking


class TestEnron(unittest.TestCase):

    def setUp(self):
        self.enron = EnronLoader(file="datasets/enron_corrected.csv",
                                 init_date=date(1999, 5, 1),
                                 end_date=date(2000, 1, 1),
                                 duration_snapshot=timedelta(days=30),
                                 overlap=timedelta(days=5))

    def test_whole(self):
        tracker = DynamicCommunityTraking(self.enron)
        d_coms = tracker.find_events()


if __name__ == '__main__':
    unittest.main()
