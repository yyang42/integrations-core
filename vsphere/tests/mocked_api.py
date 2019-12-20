import json
import os

from mock import MagicMock
from pyVmomi import vim
HERE = os.path.abspath(os.path.dirname(__file__))


class MockedCounter(object):
    def __init__(self, key, group_info_key, name_info_key, rollup):
        self.key = key
        self.groupInfo = MagicMock(key=group_info_key)
        self.nameInfo = MagicMock(key=name_info_key)
        self.rollupType = rollup


class MockedAPI(object):
    def __init__(self, _):
        pass

    def smart_connect(self):
        pass

    def get_perf_counter_by_level(self, _):
        with open(os.path.join(HERE, 'fixtures', 'metrics.json')) as f:
            file_data = json.load(f)
            return [MockedCounter(m) for m in file_data]

    def get_infrastructure(self):
        with open(os.path.join(HERE, 'fixtures', 'topology.json')) as f:
            file_data = json.load(f)
            return {
                MagicMock(spec=getattr(vim, f['spec'])): f for f in file_data
            }

    def query_metrics(self):
        return []

