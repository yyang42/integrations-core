import json
import os

import pytest
from mock import Mock, MagicMock
from pyVmomi import vim



class MockedMOR(Mock):
    """
    Helper, generate a mocked Managed Object Reference (MOR) from the given attributes.
    """

    def __init__(self, **kwargs):
        # Deserialize `spec`
        if 'spec' in kwargs:
            kwargs['spec'] = getattr(vim, kwargs['spec'])

        # Mocking
        super(MockedMOR, self).__init__(**kwargs)

        self.name = kwargs.get('name')
        self.parent = None
        self.parent_name = kwargs.get('parent_name', None)
        self.customValue = []
        power_state = kwargs.get('runtime.powerState', None)
        host_name = kwargs.get('runtime.host_name', None)
        guest_hostname = kwargs.get('guest.hostName', None)
        if power_state:
            self.runtime_powerState = getattr(vim.VirtualMachinePowerState, power_state)
        if host_name:
            self.runtime_host_name = host_name
        if guest_hostname:
            self.guest_hostName = guest_hostname

