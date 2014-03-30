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
from neutron.tests import base
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

    def test_create_policy_action(self):
        policy_action_id = _uuid()
        data = {'policy_action': {'name': 'pa1',
                                  'tenant_id': _uuid(),
                                  'action_type': 'allow',
                                  'action_value': None,
                                  'description': ''}}
        return_value = copy.copy(data['policy_action'])
        return_value.update({'id': policy_action_id})

        instance = self.plugin.return_value
        instance.create_policy_action.return_value = return_value
        res = self.api.post(_get_path('gp/policy_actions', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_policy_action.assert_called_with(mock.ANY,
                                                         policy_action=data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('policy_action', res)
        self.assertEqual(res['policy_action'], return_value)

    def test_list_policy_actions(self):
        policy_action_id = _uuid()
        return_value = [{'tenant_id': _uuid(),
                         'id': policy_action_id}]

        instance = self.plugin.return_value
        instance.get_policy_actions.return_value = return_value

        res = self.api.get(_get_path('gp/policy_actions', fmt=self.fmt))

        instance.get_policy_actions.assert_called_with(mock.ANY,
                                                       fields=mock.ANY,
                                                       filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_policy_action(self):
        policy_action_id = _uuid()
        return_value = {'tenant_id': _uuid(),
                        'id': policy_action_id}

        instance = self.plugin.return_value
        instance.get_policy_action.return_value = return_value

        res = self.api.get(_get_path('gp/policy_actions',
                                     id=policy_action_id, fmt=self.fmt))

        instance.get_policy_action.assert_called_with(mock.ANY,
                                                      policy_action_id,
                                                      fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_action', res)
        self.assertEqual(res['policy_action'], return_value)

    def test_update_policy_action(self):
        policy_action_id = _uuid()
        update_data = {'policy_action': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(),
                        'id': policy_action_id}

        instance = self.plugin.return_value
        instance.update_policy_action.return_value = return_value

        res = self.api.put(_get_path('gp/policy_actions',
                                     id=policy_action_id,
                                     fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_policy_action.assert_called_with(
            mock.ANY, policy_action_id, policy_action=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_action', res)
        self.assertEqual(res['policy_action'], return_value)

    def test_delete_policy_action(self):
        self._test_entity_delete('policy_action')

    def test_create_policy_classifier(self):
        policy_classifier_id = _uuid()
        data = {'policy_classifier': {'name': 'pc1',
                                      'tenant_id': _uuid(),
                                      'protocol': 'tcp',
                                      'port_range': '100:200',
                                      'direction': 'in',
                                      'description': ''}}
        return_value = copy.copy(data['policy_classifier'])
        return_value.update({'id': policy_classifier_id})

        instance = self.plugin.return_value
        instance.create_policy_classifier.return_value = return_value
        res = self.api.post(_get_path('gp/policy_classifiers', fmt=self.fmt),
                            self.serialize(data),
                            content_type='application/%s' % self.fmt)
        instance.create_policy_classifier.assert_called_with(mock.ANY,
                                                             policy_classifier=
                                                             data)
        self.assertEqual(res.status_int, exc.HTTPCreated.code)
        res = self.deserialize(res)
        self.assertIn('policy_classifier', res)
        self.assertEqual(res['policy_classifier'], return_value)

    def test_list_policy_classifiers(self):
        policy_classifier_id = _uuid()
        return_value = [{'tenant_id': _uuid(),
                         'id': policy_classifier_id}]

        instance = self.plugin.return_value
        instance.get_policy_classifiers.return_value = return_value

        res = self.api.get(_get_path('gp/policy_classifiers', fmt=self.fmt))

        instance.get_policy_classifiers.assert_called_with(mock.ANY,
                                                           fields=mock.ANY,
                                                           filters=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)

    def test_get_policy_classifier(self):
        policy_classifier_id = _uuid()
        return_value = {'tenant_id': _uuid(),
                        'id': policy_classifier_id}

        instance = self.plugin.return_value
        instance.get_policy_classifier.return_value = return_value

        res = self.api.get(_get_path('gp/policy_classifiers',
                                     id=policy_classifier_id, fmt=self.fmt))

        instance.get_policy_classifier.assert_called_with(mock.ANY,
                                                          policy_classifier_id,
                                                          fields=mock.ANY)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_classifier', res)
        self.assertEqual(res['policy_classifier'], return_value)

    def test_update_policy_classifier(self):
        policy_classifier_id = _uuid()
        update_data = {'policy_classifier': {'name': 'new_name'}}
        return_value = {'tenant_id': _uuid(), 'id': policy_classifier_id}

        instance = self.plugin.return_value
        instance.update_policy_classifier.return_value = return_value

        res = self.api.put(_get_path('gp/policy_classifiers',
                                     id=policy_classifier_id, fmt=self.fmt),
                           self.serialize(update_data))

        instance.update_policy_classifier.assert_called_with(
            mock.ANY, policy_classifier_id, policy_classifier=update_data)
        self.assertEqual(res.status_int, exc.HTTPOk.code)
        res = self.deserialize(res)
        self.assertIn('policy_classifier', res)
        self.assertEqual(res['policy_classifier'], return_value)

    def test_delete_policy_classifier(self):
        self._test_entity_delete('policy_classifier')


class TestGroupPolicyAttributeConverters(base.BaseTestCase):

    def test_convert_action_to_case_insensitive(self):
        self.assertEqual(
            gp.convert_action_to_case_insensitive('ALLOW'), 'allow')
        self.assertEqual(gp.convert_action_to_case_insensitive('In'), 'in')
        self.assertEqual(gp.convert_action_to_case_insensitive('bi'), 'bi')
        self.assertEqual(gp.convert_action_to_case_insensitive(''), '')

    def test_convert_port_to_string(self):
        self.assertEqual(gp.convert_port_to_string(100), '100')
        self.assertEqual(gp.convert_port_to_string('200'), '200')
        self.assertEqual(gp.convert_port_to_string(''), '')

    def test_convert_protocol_check_valid_protocols(self):
        self.assertEqual(gp.convert_protocol('tcp'), constants.TCP)
        self.assertEqual(gp.convert_protocol('TCP'), constants.TCP)
        self.assertEqual(gp.convert_protocol('udp'), constants.UDP)
        self.assertEqual(gp.convert_protocol('UDP'), constants.UDP)
        self.assertEqual(gp.convert_protocol('icmp'), constants.ICMP)
        self.assertEqual(gp.convert_protocol('ICMP'), constants.ICMP)

    def test_convert_protocol_check_invalid_protocols(self):
        self.assertRaises(gp.GroupPolicyInvalidProtocol,
                          gp.convert_protocol, 'garbage')


class TestGroupPolicyAttributeValidators(base.BaseTestCase):

    def test_validate_port_range(self):
        self.assertIsNone(gp._validate_port_range(None))
        self.assertIsNone(gp._validate_port_range('10'))
        self.assertIsNone(gp._validate_port_range(10))
        self.assertEqual(gp._validate_port_range(-1), "Invalid port '-1'")
        self.assertEqual(gp._validate_port_range('66000'),
                         "Invalid port '66000'")
        self.assertIsNone(gp._validate_port_range('10:20'))
        self.assertIsNone(gp._validate_port_range('1:65535'))
        self.assertEqual(gp._validate_port_range('0:65535'),
                         "Invalid port '0'")
        self.assertEqual(gp._validate_port_range('1:65536'),
                         "Invalid port '65536'")
        msg = gp._validate_port_range('abc:efg')
        self.assertEqual(msg, "Port 'abc' is not a valid number")
        msg = gp._validate_port_range('1:efg')
        self.assertEqual(msg, "Port 'efg' is not a valid number")
        msg = gp._validate_port_range('-1:10')
        self.assertEqual(msg, "Invalid port '-1'")
        msg = gp._validate_port_range('66000:10')
        self.assertEqual(msg, "Invalid port '66000'")
        msg = gp._validate_port_range('10:66000')
        self.assertEqual(msg, "Invalid port '66000'")
        msg = gp._validate_port_range('1:-10')
        self.assertEqual(msg, "Invalid port '-10'")
