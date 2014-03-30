# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib

import webob.exc

from neutron.api import extensions as api_ext
from neutron.common import config
from neutron import context
from neutron.db.grouppolicy import db_group_policy as gpdb
import neutron.extensions
from neutron.extensions import group_policy as gpolicy
from neutron.openstack.common import importutils
from neutron.plugins.common import constants
from neutron.tests.unit import test_db_plugin


DB_CORE_PLUGIN_KLASS = 'neutron.db.db_base_plugin_v2.NeutronDbPluginV2'
DB_GP_PLUGIN_KLASS = (
    "neutron.db.grouppolicy.db_group_policy.GroupPolicyDbMixin"
)

extensions_path = ':'.join(neutron.extensions.__path__)


class GroupPolicyTestMixin(object):
    resource_prefix_map = dict(
        (k, constants.COMMON_PREFIXES[constants.GROUP_POLICY])
        for k in gpolicy.RESOURCE_ATTRIBUTE_MAP.keys()
    )

    def _get_test_policy_classifier_attrs(self, name='pc1'):
        attrs = {'name': name, 'tenant_id': self._tenant_id}
        return attrs

    def _get_test_policy_action_attrs(self, name='pa1'):
        attrs = {'name': name, 'tenant_id': self._tenant_id}
        return attrs

    def _create_policy_classifier(self, fmt, name, description, protocol,
                                  port_range, direction,
                                  expected_res_status=None, **kwargs):
        data = {'policy_classifier': {'name': name, 'description': description,
                                      'protocol': protocol,
                                      'port_range': port_range,
                                      'direction': direction,
                                      'tenant_id': self._tenant_id}}
        pc_req = self.new_create_request('policy_classifiers', data, fmt)
        pc_res = pc_req.get_response(self.ext_api)
        if expected_res_status:
            self.assertEqual(pc_res.status_int, expected_res_status)
        return pc_res

    def _create_policy_action(self, fmt, name, description, action_type,
                              action_value, expected_res_status=None,
                              **kwargs):
        data = {'policy_action': {'name': name, 'description': description,
                                  'action_type': action_type,
                                  'action_value': action_value,
                                  'tenant_id': self._tenant_id}}
        pa_req = self.new_create_request('policy_actions', data, fmt)
        pa_res = pa_req.get_response(self.ext_api)
        if expected_res_status:
            self.assertEqual(pa_res.status_int, expected_res_status)
        return pa_res

    @contextlib.contextmanager
    def policy_classifier(self, fmt=None, name='pc1', description="",
                          protocol='tcp', port_range='80', direction='in',
                          no_delete=False, **kwargs):
        if not fmt:
            fmt = self.fmt
        res = self._create_policy_classifier(fmt, name, description, protocol,
                                             port_range, direction, **kwargs)
        if res.status_int >= 400:
            raise webob.exc.HTTPClientError(code=res.status_int)
        pc = self.deserialize(fmt or self.fmt, res)

        yield pc
        if not no_delete:
            self._delete('policy_classifiers', pc['policy_classifier']['id'])

    @contextlib.contextmanager
    def policy_action(self, fmt=None, name='pa1', description="",
                      action_type='allow', action_value=None,
                      no_delete=False, **kwargs):
        if not fmt:
            fmt = self.fmt
        res = self._create_policy_action(fmt, name, description, action_type,
                                         action_value, **kwargs)
        if res.status_int >= 400:
            raise webob.exc.HTTPClientError(code=res.status_int)
        pa = self.deserialize(fmt or self.fmt, res)

        yield pa
        if not no_delete:
            self._delete('policy_actions', pa['policy_action']['id'])


class GroupPolicyDbTestCase(GroupPolicyTestMixin,
                            test_db_plugin.NeutronDbPluginV2TestCase):

    def setUp(self, core_plugin=None, gp_plugin=None, ext_mgr=None):
        if not gp_plugin:
            gp_plugin = DB_GP_PLUGIN_KLASS
        service_plugins = {'gp_plugin_name': gp_plugin}
        gpdb.GroupPolicyDbMixin.supported_extension_aliases = ['group-policy']
        super(GroupPolicyDbTestCase, self).setUp(
            ext_mgr=ext_mgr,
            service_plugins=service_plugins
        )
        if not ext_mgr:
            self.plugin = importutils.import_object(gp_plugin)
            ext_mgr = api_ext.PluginAwareExtensionManager(
                extensions_path,
                {constants.GROUP_POLICY: self.plugin}
            )
            app = config.load_paste_app('extensions_test_app')
            self.ext_api = api_ext.ExtensionMiddleware(app, ext_mgr=ext_mgr)


class TestGroupPolicyUnMappedResources(GroupPolicyDbTestCase):

    def test_create_policy_classifier(self, **kwargs):
        name = "pc1"
        attrs = self._get_test_policy_classifier_attrs(name)
        with self.policy_classifier(name=name) as pc:
            for k, v in attrs.iteritems():
                self.assertEqual(pc['policy_classifier'][k], v)

    def test_show_policy_classifier(self):
        name = "pc1"
        attrs = self._get_test_policy_classifier_attrs(name)
        with self.policy_classifier(name=name) as pc:
            req = self.new_show_request('policy_classifiers',
                                        pc['policy_classifier']['id'],
                                        fmt=self.fmt)
            res = self.deserialize(self.fmt, req.get_response(self.ext_api))
            for k, v in attrs.iteritems():
                self.assertEqual(res['policy_classifier'][k], v)

    def test_list_policy_classifiers(self):
        with contextlib.nested(self.policy_classifier(name='pc1',
                                                      description='pc'),
                               self.policy_classifier(name='pc2',
                                                      description='pc'),
                               self.policy_classifier(name='pc3',
                                                      description='pc')
                               ) as p_classifiers:
            self._test_list_resources('policy_classifier', p_classifiers,
                                      query_params='description=pc')

    def test_update_policy_classifier(self):
        name = "new_policy_classifier1"
        attrs = self._get_test_policy_classifier_attrs(name)

        with self.policy_classifier() as pc:
            data = {'policy_classifier': {'name': name}}
            req = self.new_update_request('policy_classifiers', data,
                                          pc['policy_classifier']['id'])
            res = self.deserialize(self.fmt, req.get_response(self.ext_api))
            for k, v in attrs.iteritems():
                self.assertEqual(res['policy_classifier'][k], v)

    def test_delete_policy_classifier(self):
        ctx = context.get_admin_context()
        with self.policy_classifier(no_delete=True) as pc:
            pc_id = pc['policy_classifier']['id']
            req = self.new_delete_request('policy_classifiers', pc_id)
            res = req.get_response(self.ext_api)
            self.assertEqual(res.status_int, 204)
            self.assertRaises(gpolicy.PolicyClassifierNotFound,
                              self.plugin.get_policy_classifier, ctx, 'pc_id')

    def test_create_policy_action(self, **kwargs):
        name = "pa1"
        attrs = self._get_test_policy_action_attrs(name)

        with self.policy_action(name=name) as pa:
            for k, v in attrs.iteritems():
                self.assertEqual(pa['policy_action'][k], v)

    def test_show_policy_action(self):
        name = "pa1"
        attrs = self._get_test_policy_action_attrs(name)

        with self.policy_action(name=name) as pa:
            req = self.new_show_request('policy_actions',
                                        pa['policy_action']['id'],
                                        fmt=self.fmt)
            res = self.deserialize(self.fmt, req.get_response(self.ext_api))
            for k, v in attrs.iteritems():
                self.assertEqual(res['policy_action'][k], v)

    def test_list_policy_actions(self):
        with contextlib.nested(self.policy_action(name='pa1',
                                                  description='pa'),
                               self.policy_action(name='pa2',
                                                  description='pa'),
                               self.policy_action(name='pa3',
                                                  description='pa')
                               ) as p_actions:
            self._test_list_resources('policy_action', p_actions,
                                      query_params='description=pa')

    def test_update_policy_action(self):
        name = "new_policy_action1"
        attrs = self._get_test_policy_action_attrs(name)

        with self.policy_action() as pc:
            data = {'policy_action': {'name': name}}
            req = self.new_update_request('policy_actions', data,
                                          pc['policy_action']['id'])
            res = self.deserialize(self.fmt, req.get_response(self.ext_api))
            for k, v in attrs.iteritems():
                self.assertEqual(res['policy_action'][k], v)

    def test_delete_policy_action(self):
        ctx = context.get_admin_context()
        with self.policy_action(no_delete=True) as pa:
            pa_id = pa['policy_action']['id']
            req = self.new_delete_request('policy_actions', pa_id)
            res = req.get_response(self.ext_api)
            self.assertEqual(res.status_int, 204)
            self.assertRaises(gpolicy.PolicyActionNotFound,
                              self.plugin.get_policy_action, ctx, pa_id)


class TestInternalUtilityMethods(GroupPolicyDbTestCase):

    def test_get_min_max_ports_from_range(self):
        self.assertEqual(self.plugin._get_min_max_ports_from_range(''),
                         [None, None])
        self.assertEqual(self.plugin._get_min_max_ports_from_range('10:10'),
                         [10, 10])
        self.assertEqual(self.plugin._get_min_max_ports_from_range('10:20'),
                         [10, 20])

    def test_get_port_range_from_min_max_ports(self):
        self.assertEqual(self.plugin._get_port_range_from_min_max_ports(
            None, None), None)
        self.assertEqual(self.plugin._get_port_range_from_min_max_ports(
            10, 10), '10')
        self.assertEqual(self.plugin._get_port_range_from_min_max_ports(
            10, 20), '10:20')
