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

import abc

import six

from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import resource_helper
from neutron.common import exceptions as nexc
from neutron.openstack.common import log as logging
from neutron.plugins.common import constants
from neutron.services import service_base


LOG = logging.getLogger(__name__)


# Group Policy Exceptions
class PolicyActionNotFound(nexc.NotFound):
    message = _("PolicyAction %(policy_action_id)s could not be found")


class PolicyClassifierNotFound(nexc.NotFound):
    message = _("PolicyClassifier %(policy_classifier_id)s could not be found")


class GroupPolicyInvalidPortValue(nexc.InvalidInput):
    message = _("Invalid value for port %(port)s")


class GroupPolicyInvalidProtocol(nexc.InvalidInput):
    message = _("Protocol %(protocol)s is not supported. "
                "Only protocol values %(values)s and their integer "
                "representation (0 to 255) are supported.")


# Group Policy Values
gp_supported_actions = [None, constants.GP_ALLOW, constants.GP_REDIRECT]
gp_supported_directions = [None, constants.GP_DIRECTION_IN,
                           constants.GP_DIRECTION_OUT,
                           constants.GP_DIRECTION_BI]
gp_supported_protocols = [None, constants.TCP, constants.UDP, constants.ICMP]


# Group Policy input value conversion and validation functions
def convert_protocol(value):
    if value is None:
        return
    if value.lower() in gp_supported_protocols:
        return value.lower()
    else:
        raise GroupPolicyInvalidProtocol(protocol=value,
                                         values=
                                         gp_supported_protocols)


def convert_action_to_case_insensitive(value):
    if value is None:
        return
    else:
        return value.lower()


def convert_port_to_string(value):
    if value is None:
        return
    else:
        return str(value)


def _validate_port_range(data, key_specs=None):
    if data is None:
        return
    data = str(data)
    ports = data.split(':')
    for p in ports:
        try:
            val = int(p)
        except (ValueError, TypeError):
            msg = _("Port '%s' is not a valid number") % p
            LOG.debug(msg)
            return msg
        if val <= 0 or val > 65535:
            msg = _("Invalid port '%s'") % p
            LOG.debug(msg)
            return msg


attr.validators['type:port_range'] = _validate_port_range


POLICY_CLASSIFIERS = 'policy_classifiers'
POLICY_ACTIONS = 'policy_actions'

RESOURCE_ATTRIBUTE_MAP = {
    POLICY_CLASSIFIERS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True, 'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'protocol': {'allow_post': True, 'allow_put': True,
                     'is_visible': True, 'default': None,
                     'convert_to': convert_protocol,
                     'validate': {'type:values': gp_supported_protocols}},
        'port_range': {'allow_post': True, 'allow_put': True,
                       'validate': {'type:port_range': None},
                       'convert_to': convert_port_to_string,
                       'default': None, 'is_visible': True},
        'direction': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': gp_supported_directions},
                      'default': None, 'is_visible': True},
    },
    POLICY_ACTIONS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'action_type': {'allow_post': True, 'allow_put': True,
                        'convert_to': convert_action_to_case_insensitive,
                        'validate': {'type:values': gp_supported_actions},
                        'is_visible': True, 'default': 'allow'},
        'action_value': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:uuid_or_none': None},
                         'default': None, 'is_visible': True},
    },
}


class Group_policy(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Group Policy Abstraction"

    @classmethod
    def get_alias(cls):
        return "group-policy"

    @classmethod
    def get_description(cls):
        return "Extension for Group Policy Abstraction"

    @classmethod
    def get_namespace(cls):
        return "http://wiki.openstack.org/neutron/gp/v1.0/"

    @classmethod
    def get_updated(cls):
        return "2014-03-03T122:00:00-00:00"

    @classmethod
    def get_resources(cls):
        plural_mappings = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        attr.PLURALS.update(plural_mappings)
        return resource_helper.build_resource_info(plural_mappings,
                                                   RESOURCE_ATTRIBUTE_MAP,
                                                   constants.GROUP_POLICY)

    @classmethod
    def get_plugin_interface(cls):
        return GroupPolicyPluginBase

    def update_attributes_map(self, attributes):
        super(Group_policy, self).update_attributes_map(
            attributes, extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


@six.add_metaclass(abc.ABCMeta)
class GroupPolicyPluginBase(service_base.ServicePluginBase):

    def get_plugin_name(self):
        return constants.GROUP_POLICY

    def get_plugin_type(self):
        return constants.GROUP_POLICY

    def get_plugin_description(self):
        return 'Group Policy plugin'

    @abc.abstractmethod
    def get_policy_classifiers(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_policy_classifier(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_policy_classifier(self, context, policy_classifier):
        pass

    @abc.abstractmethod
    def update_policy_classifier(self, context, id, policy_classifier):
        pass

    @abc.abstractmethod
    def delete_policy_classifier(self, context, id):
        pass

    @abc.abstractmethod
    def get_policy_actions(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_policy_action(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_policy_action(self, context, policy_action):
        pass

    @abc.abstractmethod
    def update_policy_action(self, context, id, policy_action):
        pass

    @abc.abstractmethod
    def delete_policy_action(self, context, id):
        pass
