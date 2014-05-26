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
class EndpointNotFound(nexc.NotFound):
    message = _("Endpoint %(endpoint_id)s could not be found")


class EndpointGroupNotFound(nexc.NotFound):
    message = _("EndpointGroup %(endpoint_group_id)s could not be found")


class L2ContextNotFound(nexc.NotFound):
    message = _("L2Context %(l2_context_id)s could not be found")


class L3ContextNotFound(nexc.NotFound):
    message = _("L3Context %(l3_context_id)s could not be found")


ENDPOINTS = 'endpoints'
ENDPOINT_GROUPS = 'endpoint_groups'
L2_CONTEXT = 'l2_contexts'
L3_CONTEXT = 'l3_contexts'


RESOURCE_ATTRIBUTE_MAP = {
    ENDPOINTS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None}, 'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None}, 'default': '',
                 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True, 'is_visible': True},
        'endpoint_group_id': {'allow_post': True, 'allow_put': True,
                              'validate': {'type:uuid_or_none': None},
                              'required': True, 'is_visible': True},
    },
    ENDPOINT_GROUPS: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None}, 'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True, 'is_visible': True},
        'endpoints': {'allow_post': False, 'allow_put': False,
                      'validate': {'type:uuid_list': None},
                      'convert_to': attr.convert_none_to_empty_list,
                      'default': None, 'is_visible': True},
        'l2_context_id': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:uuid_or_none': None},
                          'default': None, 'is_visible': True},
        'provided_contracts': {'allow_post': True, 'allow_put': True,
                               'validate': {'type:dict_or_none': None},
                               'convert_to': attr.convert_none_to_empty_dict,
                               'default': None, 'is_visible': True},
        'consumed_contracts': {'allow_post': True, 'allow_put': True,
                               'validate': {'type:dict_or_none': None},
                               'convert_to': attr.convert_none_to_empty_dict,
                               'default': None, 'is_visible': True},
    },
    L2_CONTEXT: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None}, 'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True, 'is_visible': True},
        'endpoint_groups': {'allow_post': False, 'allow_put': False,
                            'validate': {'type:uuid_list': None},
                            'convert_to': attr.convert_none_to_empty_list,
                            'default': None, 'is_visible': True},
        'l3_context_id': {'allow_post': True, 'allow_put': True,
                          'validate': {'type:uuid_or_none': None},
                          'default': None, 'is_visible': True,
                          'required': True},
        # TODO (sumit): uncomment when supported in data path
        # 'allow_broadcast': {'allow_post': True, 'allow_put': True,
        #                    'default': True, 'is_visible': True,
        #                    'convert_to': attr.convert_to_boolean,
        #                    'required': False},
    },
    L3_CONTEXT: {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None}, 'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True, 'is_visible': True},
        'ip_version': {'allow_post': True, 'allow_put': False,
                       'convert_to': attr.convert_to_int,
                       'validate': {'type:values': [4, 6]},
                       'default': 4, 'is_visible': True},
        'ip_pool': {'allow_post': True, 'allow_put': False,
                    'validate': {'type:subnet': None}, 'is_visible': True},
        'default_subnet_prefix_length': {'allow_post': True, 'allow_put': True,
                                         'convert_to': attr.convert_to_int,
                                         'validate': {
                                             'type:values': range(30)},
                                         'default': 24, 'is_visible': True},
        'l2_contexts': {'allow_post': False, 'allow_put': False,
                        'validate': {'type:uuid_list': None},
                        'convert_to': attr.convert_none_to_empty_list,
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
    def get_endpoints(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_endpoint(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_endpoint(self, context, endpoint):
        pass

    @abc.abstractmethod
    def update_endpoint(self, context, id, endpoint):
        pass

    @abc.abstractmethod
    def delete_endpoint(self, context, id):
        pass

    @abc.abstractmethod
    def get_endpoint_groups(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_endpoint_group(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_endpoint_group(self, context, endpoint_group):
        pass

    @abc.abstractmethod
    def update_endpoint_group(self, context, id, endpoint_group):
        pass

    @abc.abstractmethod
    def delete_endpoint_group(self, context, id):
        pass

    @abc.abstractmethod
    def get_l2_contexts(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_l2_context(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_l2_context(self, context, l2_context):
        pass

    @abc.abstractmethod
    def update_l2_context(self, context, id, l2_context):
        pass

    @abc.abstractmethod
    def delete_l2_context(self, context, id):
        pass

    @abc.abstractmethod
    def get_l3_contexts(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_l3_context(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_l3_context(self, context, l3_context):
        pass

    @abc.abstractmethod
    def update_l3_context(self, context, id, l3_context):
        pass

    @abc.abstractmethod
    def delete_l3_context(self, context, id):
        pass
