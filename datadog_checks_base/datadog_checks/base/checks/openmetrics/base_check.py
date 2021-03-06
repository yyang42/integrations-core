# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from ...errors import CheckException
from .. import AgentCheck
from .mixins import OpenMetricsScraperMixin


class OpenMetricsBaseCheck(OpenMetricsScraperMixin, AgentCheck):
    """
    OpenMetricsBaseCheck is a class that helps instantiating PrometheusCheck only
    with YAML configurations. As each check has it own states it maintains a map
    of all checks so that the one corresponding to the instance is executed.
    Minimal example configuration::

        instances:
        - prometheus_url: http://example.com/endpoint
            namespace: "foobar"
            metrics:
            - bar
            - foo


    Agent 5 signature:

        OpenMetricsBaseCheck(name, init_config, agentConfig, instances=None, default_instances=None,
                             default_namespace=None)

    Agent 6 signature:

        OpenMetricsBaseCheck(name, init_config, instances, default_instances=None, default_namespace=None)

    """

    DEFAULT_METRIC_LIMIT = 2000

    def __init__(self, *args, **kwargs):
        args = list(args)
        default_instances = kwargs.pop('default_instances', None) or {}
        default_namespace = kwargs.pop('default_namespace', None)

        legacy_kwargs_in_args = args[4:]
        del args[4:]

        if len(legacy_kwargs_in_args) > 0:
            default_instances = legacy_kwargs_in_args[0] or {}
        if len(legacy_kwargs_in_args) > 1:
            default_namespace = legacy_kwargs_in_args[1]

        super(OpenMetricsBaseCheck, self).__init__(*args, **kwargs)
        self.config_map = {}
        self.default_instances = default_instances
        self.default_namespace = default_namespace

        # pre-generate the scraper configurations

        if 'instances' in kwargs:
            instances = kwargs['instances']
        elif len(args) == 4:
            # instances from agent 5 signature
            instances = args[3]
        elif isinstance(args[2], (tuple, list)):
            # instances from agent 6 signature
            instances = args[2]
        else:
            instances = None

        if instances is not None:
            for instance in instances:
                self.get_scraper_config(instance)

    def check(self, instance):
        # Get the configuration for this specific instance
        scraper_config = self.get_scraper_config(instance)

        # We should be specifying metrics for checks that are vanilla OpenMetricsBaseCheck-based
        if not scraper_config['metrics_mapper']:
            raise CheckException(
                "You have to collect at least one metric from the endpoint: {}".format(scraper_config['prometheus_url'])
            )

        self.process(scraper_config)

    def get_scraper_config(self, instance):
        endpoint = instance.get('prometheus_url')

        if endpoint is None:
            raise CheckException("Unable to find prometheus URL in config file.")

        # If we've already created the corresponding scraper configuration, return it
        if endpoint in self.config_map:
            return self.config_map[endpoint]

        # Otherwise, we create the scraper configuration
        config = self.create_scraper_configuration(instance)

        # Add this configuration to the config_map
        self.config_map[endpoint] = config

        return config

    def _finalize_tags_to_submit(self, _tags, metric_name, val, metric, custom_tags=None, hostname=None):
        """
        Format the finalized tags
        This is generally a noop, but it can be used to change the tags before sending metrics
        """
        return _tags

    def _filter_metric(self, metric, scraper_config):
        """
        Used to filter metrics at the begining of the processing, by default no metric is filtered
        """
        return False
