from datetime import datetime, timedelta

import pytest
from mock import MagicMock, patch
from pyVmomi import vim
from six import iteritems

from datadog_checks.vsphere.cache import VSphereCache, MetricsMetadataCache, InfrastructureCache
from datadog_checks.vsphere.constants import ALL_RESOURCES, ALL_RESOURCES_WITH_METRICS


def test_generic_cache_usage():
    interval = 120
    with patch('datadog_checks.vsphere.cache.time') as time:
        mocked_timestamps = [object() for _ in range(3)]
        time.time = MagicMock(side_effect=mocked_timestamps)
        cache = VSphereCache(interval)
        # Assert initialization
        assert cache._last_ts is mocked_timestamps[0]
        assert cache._interval == interval
        assert not cache._content

        # Update the content
        with cache.update():
            assert cache._last_ts is mocked_timestamps[0]
            cache._content['foo'] = 'bar'

        # Assert that the cache last ts was updated successfully
        assert cache._last_ts is mocked_timestamps[1]

        # Update the content but an error is raised
        with pytest.raises(Exception), cache.update():
            assert not cache._content
            cache._content['foo'] = 'baz'
            raise Exception('foo')

        # Because of the exception the content and the timestamps were not updated
        assert cache._last_ts is mocked_timestamps[1]
        assert cache._content['foo'] == 'bar'


def test_refresh():
    interval = 120
    with patch('datadog_checks.vsphere.cache.time') as time:
        base_time = 1576263848
        mocked_timestamps = [base_time + 50 * i for i in range(4)]
        time.time = MagicMock(side_effect=mocked_timestamps)
        cache = VSphereCache(interval)

        assert cache.is_expired()
        cache._last_ts = base_time

        assert not cache.is_expired()  # Only 50 seconds
        assert not cache.is_expired()  # Only 100 seconds
        assert cache.is_expired()  # 150 > 120 seconds


def test_metrics_metadata_cache():
    cache = MetricsMetadataCache(float('inf'))
    data = {k: object() for k in ALL_RESOURCES_WITH_METRICS}

    with cache.update():
        for k, v in iteritems(data):
            cache.set_metadata(k, v)

    for k, v in iteritems(data):
        assert cache.get_metadata(k) == v


@patch('datadog_checks.vsphere.cache.type')
def test_infrastructure_cache(mocked_type):
    mocked_type.side_effect = lambda x: x.mocked_spec if hasattr(x, 'mocked_spec') else type(x)
    cache = InfrastructureCache(float('inf'))
    mors = {MagicMock(mocked_spec=k): object() for k in ALL_RESOURCES_WITH_METRICS * 2}
    with cache.update():
        for k, v in iteritems(mors):
            cache.set_mor_data(k, v)

    for r in ALL_RESOURCES_WITH_METRICS:
        assert len(cache.get_mors(r)) == 2

    for k, v in iteritems(mors):
        assert cache.get_mor_props(k) == v

