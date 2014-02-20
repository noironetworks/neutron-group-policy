# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 OpenStack Foundation.
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

import abc

from oslo.config import cfg

from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.common import exceptions as qexception
from neutron import manager
from neutron.plugins.common import constants


# Group-Policy Exceptions
class GroupPolicyInvalidPortValue(qexception.InvalidInput):
    message = _("Invalid value for port %(port)s")

# Group-Policy input value validation functions
def convert_validate_port_value(port):
    if port is None:
        return port
    try:
        val = int(port)
    except (ValueError, TypeError):
        raise GroupPolicyInvalidPortValue(port=port)

    if val >= 0 and val <= 65535
        return val
    else:
        raise GroupPolicyInvalidPortValue(port=port)

# Group-Policy Values
gp_supported_comparator = ['equal', 'less-than', 'greater-than' 'max', 'min']
gp_supported_security_action = ['allow', 'deny']


RESOURCE_ATTRIBUTE_MAP = {
    'endpoints': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '',
                 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'reference': {'allow_post': True, 'allow_put': True,
                      'required_by_policy': True,
                      'validate': {'type:endpoint_reference': None},
                      'is_visible': True}
    },
    'endpoint_groups': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '',
                 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'members': {'allow_post': True, 'allow_put': True,
                        'default': None,
                        'validate': {'type:uuid_list': None},
                        'required': True, 'is_visible': True}
    },
    'policies': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'src_group': {'allow_post': True, 'allow_put': True,
                        'default': None,
                        'validate': {'type:uuid_list': None},
                        'required': True, 'is_visible': True},
        'dst_group': {'allow_post': True, 'allow_put': True,
                        'default': None,
                        'validate': {'type:uuid_list': None},
                        'required': True, 'is_visible': True},
        'bidirectional': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:boolean': None},
                        'is_visible': True},
        'policy_rules': {'allow_post': True, 'allow_put': True,
                        'default': None,
                        'validate': {'type:uuid_list': None},
                        'required': True, 'is_visible': True}
    },
    'policy_rules': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '',
                 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'classifier': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:uuid': None},
                    'is_visible': True},
        'action_list': {'allow_post': True, 'allow_put': True,
                        'default': None,
                        'validate': {
                            'type:dict_or_nodata':  {
                                'action_type' : {
                                    'type:string' : None
                                },
                                'action_value' : {
                                    'type:uuid' : None
                                }}},
                        'required': True, 'is_visible': True}
    }
    'classifiers': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '',
                 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'type': {'allow_post': True, 'allow_put': False,
                 'validate': {'type:string': None},
                 'is_visible': True},
        'ports': {'allow_post': True, 'allow_put': True,
                  'default': None,
                  'validate': {
                    'type:dict_or_nodata':  {
                        'comparator' : {
                            'type:string': gp_supported_comparator
                        },
                        'port_value' : {
                            'type:string': None
                        }}}},
        'protocol': {'allow_post': True, 'allow_put': False,
                     'validate': {'type:string': None},
                     'is_visible': True}
    }
    'action_security': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'value': {'allow_post': True, 'allow_put': False,
                  'validate': {'type:string': gp_supported_security_action}}
    }
}


class GroupPolicy(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Group-Policy Abstraction"

    @classmethod
    def get_alias(cls):
        return "group-policy"

    @classmethod
    def get_description(cls):
        return "Extension for Group-Policy Abstraction"

    @classmethod
    def get_namespace(cls):
        return "http://wiki.openstack.org/neutron/gp/v1.0/"

    @classmethod
    def get_updated(cls):
        return "2014-02-03T122:00:00-00:00"

    @classmethod
    def get_resources(cls):
        my_plurals = []
        for plural in RESOURCE_ATTRIBUTE_MAP:
            if plural == 'policies':
                singular = 'policy'
            else:
                singular = plural[:-1]
            my_plurals.append((plural, singular))
        attr.PLURALS.update(dict(my_plurals))
        resources = []
        plugin = manager.NeutronManager.get_plugin()
        for collection_name in RESOURCE_ATTRIBUTE_MAP:
            if collection_name == 'policies':
                resource_name = 'policy'
            else:
                resource_name = collection_name[:-1]

            params = RESOURCE_ATTRIBUTE_MAP[collection_name]
            collection_name = collection_name.replace('_', '-')

            controller = base.create_resource(
                collection_name, resource_name, plugin, params,
                allow_pagination=cfg.CONF.allow_pagination,
                allow_sorting=cfg.CONF.allow_sorting)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                path_prefix="/gp",
                attr_map=params)
            resources.append(resource)

        return resources

    @classmethod
    def get_plugin_interface(cls):
        return GroupPolicyPluginBase

    def update_attributes_map(self, attributes):
        super(GroupPolicy, self).update_attributes_map(
            attributes, extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


class GroupPolicyPluginBase(ServicePluginBase):
    __metaclass__ = abc.ABCMeta

    def get_plugin_name(self):
        return "GROUPPOLICY"

    def get_plugin_type(self):
        return "GROUPPOLICY"

    def get_plugin_description(self):
        return 'Group Policy plugin'

    @abc.abstractmethod
    def get_endpoints(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_endpoint(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_endpoint(self, context, obj):
        pass

    @abc.abstractmethod
    def destroy_endpoint(self, context, id):
        pass

    @abc.abstractmethod
    def get_connectivity_groups(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_connectivity_group(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_connectivity_group(self, context, group):
        pass

    @abc.abstractmethod
    def update_connectivity_group(self, context, id, group):
        pass

    @abc.abstractmethod
    def delete_connectivity_group(self, context, id):
        pass

    @abc.abstractmethod
    def create_policy(self, context, policy);
        pass

    @abc.abstractmethod
    def update_policy(self, context, policy);
        pass

    @abc.abstractmethod
    def get_policies(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_policy(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def delete_policy(self, context, id):
        pass

    @abc.abstractmethod
    def get_policy_rules(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_policy_rule(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_policy_rule(self, context, id, rule):
        pass

    @abc.abstractmethod
    def update_policy_rule(self, context, id, rule):
        pass

    @abc.abstractmethod
    def delete_policy_rule(self, context, id):
        pass

    @abc.abstractmethod
    def get_classifiers(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_classifier(self, context, fields=None):
        pass

    @abc.abstractmethod
    def create_classifier(self, context, classifier):
        pass

    @abc.abstractmethod
    def update_classifier(self, context, id, classifier):
        pass

    @abc.abstractmethod
    def delete_classifier(self, context, id):
        pass

    @abc.abstractmethod
    def create_action(self, context, action):
        pass

    @abc.abstractmethod
    def update_action(self, context, id, action):
        pass

    @abc.abstractmethod
    def delete_action(self, context, id):
        pass

    @abc.abstractmethod
    def get_supported_actions(self, context, filters=None, fields=None):
        pass


