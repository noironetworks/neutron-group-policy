# Copyright (c) 2013 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Sumit Naiksatam

import logging
import types

from oslo.config import cfg

from neutron.common import constants as q_const
from neutron.db import api as qdbapi
from neutron.db.grouppolicy import db_group_policy
from neutron.plugins.common import constants

LOG = logging.getLogger(__name__)


class GroupPolicyPlugin(db_group_policy.DbMixin):

    """Implementation of the Neutron Group Policy resources.

    This class implements a Group Policy plugin. It implements
    the group policy abstractions as well as acts on all
    neutron core and extension API calls including advanced
    services. It leverages south-bound plugin drivers to render
    policy on backends which natively do not understand these
    group policy constructs.
    """
    supported_extension_aliases = []
    

    def __init__(self, plugin_references=None):
        super(GroupPolicyPlugin, self).__init__()

    def __getattribute__(self, name):
        """Delegate calls to the proper class.

        Two categories of calls,
        (1) group policy,
        (2) everything else
        """
        LOG.debug(_("Method called: %s"), name)
        return object.__getattribute__(self, "mapping_function")

    def get_plugin_type(self):
        return constants.GROUP_POLICY

    def get_plugin_description(self):
        """returns string description of the plugin."""
        return ("Group Policy plugin")

    def mapping_function(self, name):
        return
