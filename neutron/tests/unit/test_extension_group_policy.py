# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import copy

import mock
from oslo.config import cfg
from webob import exc
import webtest

from neutron.api import extensions
from neutron.api.v2 import attributes
from neutron.common import config
from neutron.extensions import group_policy as gpolicy
from neutron import manager
from neutron.openstack.common import uuidutils
from neutron.plugins.common import constants
from neutron.tests import base
from neutron.tests.unit import test_api_v2
from neutron.tests.unit import test_extensions
from neutron.tests.unit import testlib_api


_uuid = uuidutils.generate_uuid
_get_path = test_api_v2._get_path


class GroupPolicyTestExtensionManager(object):

    def get_resources(self):
        # Add the resources to the global attribute map
        # This is done here as the setup process won't
        # initialize the main API router which extends
        # the global attribute map
        attributes.RESOURCE_ATTRIBUTE_MAP.update(
            gpolicy.RESOURCE_ATTRIBUTE_MAP)
        return gpolicy.GroupPolicy.get_resources()

    def get_actions(self):
        return []

    def get_request_extensions(self):
        return []


class GroupPolicyExtensionTestCase(testlib_api.WebTestCase):
    fmt = 'json'

    def setUp(self):
        super(GroupPolicyExtensionTestCase, self).setUp()
        plugin = 'neutron.extensions.gpolicy.GroupPolicyPluginBase'
        # Ensure 'stale' patched copies of the plugin are never returned
        manager.NeutronManager._instance = None

        # Ensure existing ExtensionManager is not used
        extensions.PluginAwareExtensionManager._instance = None

        # Create the default configurations
        args = ['--config-file', test_api_v2.etcdir('neutron.conf.test')]
        config.parse(args)

        cfg.CONF.set_override('core_plugin', plugin)
        # TODO(sumit): following based on plugin decision
        # cfg.CONF.set_override('service_plugins', [plugin])

        self._plugin_patcher = mock.patch(plugin, autospec=True)
        self.plugin = self._plugin_patcher.start()
        instance = self.plugin.return_value
        # TODO(sumit): following based on plugin decision
        # instance.get_plugin_type.return_value = constants.GROUPPOLICY

        ext_mgr = GroupPolicyTestExtensionManager()
        self.ext_mdw = test_extensions.setup_extensions_middleware(ext_mgr)
        self.api = webtest.TestApp(self.ext_mdw)
        super(GroupPolicyExtensionTestCase, self).setUp()

    def tearDown(self):
        self._plugin_patcher.stop()
        self.api = None
        self.plugin = None
        cfg.CONF.reset()
        super(GroupPolicyExtensionTestCase, self).tearDown()

    def _test_entity_delete(self, entity):
        """Does the entity deletion based on naming convention."""
        entity_id = _uuid()
        path_prefix = 'gp/'

        if entity == 'policy':
            entity_plural = 'policies'
        else:
            entity_plural = entity + 's'

        res = self.api.delete(_get_path(path_prefix + entity_plural,
                                        id=entity_id, fmt=self.fmt))
        delete_entity = getattr(self.plugin.return_value, "delete_" + entity)
        delete_entity.assert_called_with(mock.ANY, entity_id)
        self.assertEqual(res.status_int, exc.HTTPNoContent.code)

    def test_create_endpoint(self):
        endpoint_id = _uuid()
        data = {'endpoint': {'name': 'endpoint1',
                             'reference': {'network': _uuid()},
                             'tenant_id': _uuid()}}
        return_value = copy.copy(data['endpoint'])
        return_value.update({'id': endpoint_id})

        instance = self.plugin.return_value
        instance.create_endpoint.return_value = return_value
        res = self.api.post(_get_path('gp/group_policies', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_endpoint.assert_called_with(mock.ANY,
                                                    endpoint=data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('endpoint', res)
        self.assertEqual(res['endpoint'], return_value)

    def test_endpoint_list(self):
        endpoint_id = _uuid()
        return_value = [{'tenant_id': _uuid(),
                         'id': endpoint_id}]

        instance = self.plugin.return_value
        instance.get_endpoints.return_value = return_value

        res = self.api.get(_get_path('gp/endpoints', fmt=self.fmt))

        instance.get_endpoints.assert_called_with(mock.ANY,
                                                  fields=mock.ANY,
                                                  filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_endpoint_get(self):
        endpoint_id = _uuid()
        return_value = {'tenant_id': _uuid(),
                        'id': endpoint_id}

        instance = self.plugin.return_value
        instance.get_endpoint.return_value = return_value

        res = self.api.get(_get_path('gp/endpoints',
                                     id=endpoint_id, fmt=self.fmt))

        instance.get_endpoint.assert_called_with(mock.ANY,
                                                 endpoint_id,
                                                 fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('endpoint', res)
        self.assertEqual(res['endpoint'], return_value)

    def test_endpoint_update(self):
        endpoint_id = _uuid()
        update_data = {'endpoint': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(),
                        'id': endpoint_id}

        instance = self.plugin.return_value
        instance.update_endpoint.return_value = return_value

        res = self.api.put(_get_path('gp/endpoints', id=endpoint_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_endpoint.assert_called_with(mock.ANY, endpoint_id,
                                                    endpoint=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('endpoint', res)
        self.assertEqual(res['endpoint'], return_value)

    def test_endpoint_delete(self):
        self._test_entity_delete('endpoint')
