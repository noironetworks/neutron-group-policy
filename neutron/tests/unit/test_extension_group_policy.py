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
from webob import exc

from neutron.extensions import group_policy as gp
from neutron.openstack.common import uuidutils
from neutron.plugins.common import constants
from neutron.tests.unit import test_api_v2
from neutron.tests.unit import test_api_v2_extension


_uuid = uuidutils.generate_uuid
_get_path = test_api_v2._get_path


class GroupPolicyExtensionTestCase(test_api_v2_extension.ExtensionTestCase):
    fmt = 'json'

    def setUp(self):
        super(GroupPolicyExtensionTestCase, self).setUp()
        self._setUpExtension(
            'neutron.extensions.group_policy.GroupPolicyPluginBase',
            constants.GROUP_POLICY, gp.RESOURCE_ATTRIBUTE_MAP,
            gp.Group_policy, 'gp', plural_mappings={})

    def test_create_endpoint(self):
        endpoint_id = _uuid()
        data = {'endpoint': {'name': 'ep1',
                             'endpoint_group_id': _uuid(),
                             'tenant_id': _uuid(),
                             'description': ''}}
        return_value = copy.copy(data['endpoint'])
        return_value.update({'id': endpoint_id})

        instance = self.plugin.return_value
        instance.create_endpoint.return_value = return_value
        res = self.api.post(_get_path('gp/endpoints', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_endpoint.assert_called_with(mock.ANY,
                                                    endpoint=data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('endpoint', res)
        self.assertEqual(res['endpoint'], return_value)

    def test_list_endpoints(self):
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

    def test_get_endpoint(self):
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

    def test_update_endpoint(self):
        endpoint_id = _uuid()
        update_data = {'endpoint': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(),
                        'id': endpoint_id}

        instance = self.plugin.return_value
        instance.update_endpoint.return_value = return_value

        res = self.api.put(_get_path('gp/endpoints',
                                     id=endpoint_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_endpoint.assert_called_with(
            mock.ANY, endpoint_id, endpoint=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('endpoint', res)
        self.assertEqual(res['endpoint'], return_value)

    def test_delete_endpoint(self):
        self._test_entity_delete('endpoint')

    def test_create_endpoint_group(self):
        endpoint_group_id = _uuid()
        data = {'endpoint_group': {'name': 'epg1',
                                   'tenant_id': _uuid(),
                                   'description': '',
                                   'l2_context_id': _uuid(),
                                   'provided_contracts': {_uuid(): None},
                                   'consumed_contracts': {_uuid(): None}}}
        return_value = copy.copy(data['endpoint_group'])
        return_value.update({'id': endpoint_group_id})
        return_value.update({'l2_context_id': None})

        instance = self.plugin.return_value
        instance.create_endpoint_group.return_value = return_value
        res = self.api.post(_get_path('gp/endpoint_groups', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_endpoint_group.assert_called_with(mock.ANY,
                                                          endpoint_group=data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('endpoint_group', res)
        self.assertEqual(res['endpoint_group'], return_value)

    def test_list_endpoint_groups(self):
        endpoint_group_id = _uuid()
        return_value = [{'tenant_id': _uuid(),
                         'id': endpoint_group_id}]

        instance = self.plugin.return_value
        instance.get_endpoint_groups.return_value = return_value

        res = self.api.get(_get_path('gp/endpoint_groups', fmt=self.fmt))

        instance.get_endpoint_groups.assert_called_with(mock.ANY,
                                                        fields=mock.ANY,
                                                        filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_endpoint_group(self):
        endpoint_group_id = _uuid()
        return_value = {'tenant_id': _uuid(),
                        'id': endpoint_group_id}

        instance = self.plugin.return_value
        instance.get_endpoint_group.return_value = return_value

        res = self.api.get(_get_path('gp/endpoint_groups',
                                     id=endpoint_group_id, fmt=self.fmt))

        instance.get_endpoint_group.assert_called_with(mock.ANY,
                                                       endpoint_group_id,
                                                       fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('endpoint_group', res)
        self.assertEqual(res['endpoint_group'], return_value)

    def test_update_endpoint_group(self):
        endpoint_group_id = _uuid()
        update_data = {'endpoint_group': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(),
                        'id': endpoint_group_id}

        instance = self.plugin.return_value
        instance.update_endpoint_group.return_value = return_value

        res = self.api.put(_get_path('gp/endpoint_groups',
                                     id=endpoint_group_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_endpoint_group.assert_called_with(
            mock.ANY, endpoint_group_id, endpoint_group=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('endpoint_group', res)
        self.assertEqual(res['endpoint_group'], return_value)

    def test_delete_endpoint_group(self):
        self._test_entity_delete('endpoint_group')

    def test_create_l2_context(self):
        l2_context_id = _uuid()
        data = {'l2_context': {'name': 'bd1', 'tenant_id': _uuid(),
                               'description': '',
                               'l3_context_id': _uuid()}}
        return_value = copy.copy(data['l2_context'])
        return_value.update({'id': l2_context_id})
        return_value.update({'l3_context_id': None})

        instance = self.plugin.return_value
        instance.create_l2_context.return_value = return_value
        res = self.api.post(_get_path('gp/l2_contexts', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_l2_context.assert_called_with(mock.ANY,
                                                      l2_context=data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('l2_context', res)
        self.assertEqual(res['l2_context'], return_value)

    def test_list_l2_contexts(self):
        l2_context_id = _uuid()
        return_value = [{'tenant_id': _uuid(),
                         'id': l2_context_id}]

        instance = self.plugin.return_value
        instance.get_l2_contexts.return_value = return_value

        res = self.api.get(_get_path('gp/l2_contexts', fmt=self.fmt))

        instance.get_l2_contexts.assert_called_with(mock.ANY,
                                                    fields=mock.ANY,
                                                    filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_l2_context(self):
        l2_context_id = _uuid()
        return_value = {'tenant_id': _uuid(),
                        'id': l2_context_id}

        instance = self.plugin.return_value
        instance.get_l2_context.return_value = return_value

        res = self.api.get(_get_path('gp/l2_contexts',
                                     id=l2_context_id, fmt=self.fmt))

        instance.get_l2_context.assert_called_with(mock.ANY,
                                                   l2_context_id,
                                                   fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('l2_context', res)
        self.assertEqual(res['l2_context'], return_value)

    def test_update_l2_context(self):
        l2_context_id = _uuid()
        update_data = {'l2_context': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(),
                        'id': l2_context_id}

        instance = self.plugin.return_value
        instance.update_l2_context.return_value = return_value

        res = self.api.put(_get_path('gp/l2_contexts',
                                     id=l2_context_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_l2_context.assert_called_with(
            mock.ANY, l2_context_id, l2_context=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('l2_context', res)
        self.assertEqual(res['l2_context'], return_value)

    def test_delete_l2_context(self):
        self._test_entity_delete('l2_context')

    def test_create_l3_context(self):
        l3_context_id = _uuid()
        data = {'l3_context': {'name': 'rd1', 'tenant_id': _uuid(),
                               'description': '', 'ip_version': 4,
                               'ip_pool': '10.0.0.0/8',
                               'default_subnet_prefix_length': 16}}
        return_value = copy.copy(data['l3_context'])
        return_value.update({'id': l3_context_id})

        instance = self.plugin.return_value
        instance.create_l3_context.return_value = return_value
        res = self.api.post(_get_path('gp/l3_contexts', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_l3_context.assert_called_with(mock.ANY,
                                                      l3_context=data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('l3_context', res)
        self.assertEqual(res['l3_context'], return_value)

    def test_list_l3_contexts(self):
        l3_context_id = _uuid()
        return_value = [{'tenant_id': _uuid(),
                         'id': l3_context_id}]

        instance = self.plugin.return_value
        instance.get_l3_contexts.return_value = return_value

        res = self.api.get(_get_path('gp/l3_contexts', fmt=self.fmt))

        instance.get_l3_contexts.assert_called_with(mock.ANY, fields=mock.ANY,
                                                    filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_l3_context(self):
        l3_context_id = _uuid()
        return_value = {'tenant_id': _uuid(),
                        'id': l3_context_id}

        instance = self.plugin.return_value
        instance.get_l3_context.return_value = return_value

        res = self.api.get(_get_path('gp/l3_contexts',
                                     id=l3_context_id, fmt=self.fmt))

        instance.get_l3_context.assert_called_with(mock.ANY, l3_context_id,
                                                   fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('l3_context', res)
        self.assertEqual(res['l3_context'], return_value)

    def test_update_l3_context(self):
        l3_context_id = _uuid()
        update_data = {'l3_context': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(),
                        'id': l3_context_id}

        instance = self.plugin.return_value
        instance.update_l3_context.return_value = return_value

        res = self.api.put(_get_path('gp/l3_contexts',
                                     id=l3_context_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_l3_context.assert_called_with(
            mock.ANY, l3_context_id, l3_context=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('l3_context', res)
        self.assertEqual(res['l3_context'], return_value)

    def test_delete_l3_context(self):
        self._test_entity_delete('l3_context')
