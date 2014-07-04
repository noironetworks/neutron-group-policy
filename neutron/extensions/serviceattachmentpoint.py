# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack Foundation.
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

import six

from neutron.api import extensions
from neutron.api.v2 import attributes as attr
from neutron.api.v2 import base
from neutron.api.v2 import resource_helper
from neutron.common import exceptions as qexception
from neutron import manager
from neutron.openstack.common import log as logging
from neutron.plugins.common import constants
from neutron import quota

LOG = logging.getLogger(__name__)


# ServiceAttachmentPoint Exceptions
class ServiceAttachmentPointNotFound(qexception.NotFound):
    message = _("Service attachment point %(id)s does not exist")


class ServiceAttachmentPointInUse(qexception.InUse):
    message = _("Service attachment point %(id)s is already assign to"
                " network %(net_id)s")


supported_insert_mode = [
    constants.SERVICE_AP_INSERT_MODE_L1,
    constants.SERVICE_AP_INSERT_MODE_L2,
    constants.SERVICE_AP_INSERT_MODE_L3
]
supported_ap_type = [
    constants.SERVICE_AP_NEUTRON_PORT,
    constants.SERVICE_AP_ROUTER,
    constants.SERVICE_AP_EXTERNAL_AP
]

RESOURCE_ATTRIBUTE_MAP = {
    'service_attachment_points': {
        'id': {'allow_post': False, 'allow_put': False,
               'enforce_policy': True,
               'validate': {'type:uuid': None},
               'is_visible': True, 'primary_key': True},
        'service_id': {'allow_post': True, 'allow_put': True,
                       'required_by_policy': True,
                       'validate': {'type:uuid_or_none': None},
                       'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'enforce_policy': True,
                 'validate': {'type:string': None},
                 'is_visible': True, 'default': ''},
        'description': {'allow_post': True, 'allow_put': True,
                        'enforce_policy': True,
                        'validate': {'type:string': None},
                        'is_visible': True, 'default': ''},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'required_by_policy': True,
                      'is_visible': True},
        'role': {'allow_post': True, 'allow_put': False,
                 'enforce_policy': True,
                 'default': '', 'validate': {'type:string': None},
                 'is_visible': True},
        'subnet_id': {'allow_post': True, 'allow_put': False,
                      'enforce_policy': True,
                      'validate': {'type:uuid_or_none': None},
                      'is_visible': True, 'default': None},
    }
}


class ServiceAttachmentPoint(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Neutron Service Attachment Point"

    @classmethod
    def get_alias(cls):
        return "service_attachment_point"

    @classmethod
    def get_description(cls):
        return "Neutron service attachment point configuration"

    @classmethod
    def get_namespace(cls):
        return ("http://wiki.openstack.org/neutron/serviceattachmentpoint/"
                "API_1.0")

    @classmethod
    def get_updated(cls):
        return "2014-07-01:00:00-00:00"

    def update_attributes_map(self, attributes):
        super(ServiceAttachmentPoint, self).update_attributes_map(
            attributes, extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    @classmethod
    def get_resources(cls):
        plural_mappings = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        resource_name = "service_attachment_point"
        collection_name = resource_name.replace('_', '-') + "s"
        exts = []
        attr.PLURALS.update(plural_mappings)
        plugin = manager.NeutronManager.get_plugin()
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name + "s", dict())
        quota.QUOTAS.register_resource_by_name(resource_name)
        controller = base.create_resource(collection_name,
                                          resource_name,
                                          plugin, params, allow_bulk=True,
                                          allow_pagination=True,
                                          allow_sorting=True)

        ext = extensions.ResourceExtension(collection_name,
                                           controller,
                                           attr_map=params)
        exts.append(ext)
        return exts

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}


@six.add_metaclass(abc.ABCMeta)
class ServiceAttachmentPointPluginBase(object):

    @abc.abstractmethod
    def get_service_attachment_points(self, context, filters=None, fields=None,
                                      sorts=None, limit=None, marker=None,
                                      page_reverse=False):
        pass

    @abc.abstractmethod
    def get_service_attachment_point(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_service_attachment_point(self, context, service_ap):
        pass

    @abc.abstractmethod
    def update_service_attachment_point(self, context, id, service_ap):
        pass

    @abc.abstractmethod
    def delete_service_attachment_point(self, context, id):
        pass
