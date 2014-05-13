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

import mock

from neutron.api.rpc.agentnotifiers import dhcp_rpc_agent_api
from neutron.notifiers import nova
from neutron.plugins.grouppolicy import config
import neutron.tests.unit.db.grouppolicy.test_db_grouppolicy_mapping as tdb


GP_PLUGIN_KLASS = (
    "neutron.plugins.grouppolicy.plugin.GroupPolicyPlugin"
)


class GroupPolicyMappingTestCase(tdb.GroupPolicyMappingDbTestCase):
    def setUp(self, core_plugin=None, gp_plugin=None, ext_mgr=None):
        config.cfg.CONF.set_override('policy_drivers',
                                     ['mapping'],
                                     group='group_policy')
        super(GroupPolicyMappingTestCase, self).setUp(
            gp_plugin=GP_PLUGIN_KLASS,
            service_plugins={'gp_plugin_name': GP_PLUGIN_KLASS,
                             'l3_plugin_name': 'router'}
        )


class TestGroupPolicyMapping(GroupPolicyMappingTestCase):
    # REVISIT(rkukura): Mock core plugin?

    def test_implicit_workflow(self, **kwargs):
        with self.endpoint_group(name="epg1") as epg:
            self.assertIsNotNone(epg['endpoint_group']['bridge_domain_id'])
            subnets = epg['endpoint_group']['neutron_subnets']
            self.assertIsNotNone(subnets)
            self.assertEqual(len(subnets), 1)
            # TODO(rkukura): Verify subnet details
            # TODO(rkukura): Verify router interface added
            epg_id = epg['endpoint_group']['id']

            with self.endpoint(name="ep1", endpoint_group_id=epg_id) as ep:
                self.assertEqual(ep['endpoint']['endpoint_group_id'], epg_id)
                port_id = ep['endpoint']['neutron_port_id']
                self.assertIsNotNone(port_id)
                # TODO(rkukura): Verify port details

    def test_explicit_workflow(self, **kwargs):
        with self.routing_domain(name="rd1") as rd:
            routers = rd['routing_domain']['neutron_routers']
            self.assertIsNotNone(routers)
            self.assertEqual(len(routers), 1)
            # TODO(rkukura): Verify subnet details
            # TODO(rkukura): Verify router interface added
            rd_id = rd['routing_domain']['id']

            with self.bridge_domain(name="bd1",
                                    routing_domain_id=rd_id) as bd:
                self.assertEqual(bd['bridge_domain']['routing_domain_id'],
                                 rd_id)
                net_id = bd['bridge_domain']['neutron_network_id']
                self.assertIsNotNone(net_id)
                # TODO(rkukura): Verify network details
                bd_id = bd['bridge_domain']['id']

                with self.endpoint_group(name="epg1",
                                         bridge_domain_id=bd_id) as epg:
                    self.assertEqual(epg['endpoint_group']['bridge_domain_id'],
                                     bd_id)
                    subnets = epg['endpoint_group']['neutron_subnets']
                    self.assertIsNotNone(subnets)
                    self.assertEqual(len(subnets), 1)
                    # TODO(rkukura): Verify subnet details
                    epg_id = epg['endpoint_group']['id']

                    with self.endpoint(name="ep1",
                                       endpoint_group_id=epg_id) as ep:
                        self.assertEqual(ep['endpoint']['endpoint_group_id'],
                                         epg_id)
                        port_id = ep['endpoint']['neutron_port_id']
                        self.assertIsNotNone(port_id)
                        # TODO(rkukura): Verify port details


class NotificationTest(GroupPolicyMappingTestCase):
    def test_dhcp_notifier(self, **kwargs):
        with mock.patch.object(dhcp_rpc_agent_api.DhcpAgentNotifyAPI,
                               'notify') as dhcp_notifier:
            with self.endpoint_group(name="epg1") as epg:
                epg_id = epg['endpoint_group']['id']
                with self.endpoint(name="ep1", endpoint_group_id=epg_id) as ep:
                    self.assertEqual(ep['endpoint']['endpoint_group_id'],
                                     epg_id)
                    # REVISIT(rkukura): check dictionaries for correct
                    # id, etc.
                    dhcp_notifier.assert_any_call(mock.ANY, mock.ANY,
                                                  "router.create.end")
                    dhcp_notifier.assert_any_call(mock.ANY, mock.ANY,
                                                  "network.create.end")
                    dhcp_notifier.assert_any_call(mock.ANY, mock.ANY,
                                                  "subnet.create.end")
                    dhcp_notifier.assert_any_call(mock.ANY, mock.ANY,
                                                  "port.create.end")

    def test_nova_notifier(self, **kwargs):
        with mock.patch.object(nova.Notifier,
                               'send_network_change') as nova_notifier:
            with self.endpoint_group(name="epg1") as epg:
                epg_id = epg['endpoint_group']['id']
                with self.endpoint(name="ep1", endpoint_group_id=epg_id) as ep:
                    self.assertEqual(ep['endpoint']['endpoint_group_id'],
                                     epg_id)
                    # REVISIT(rkukura): check dictionaries for correct
                    # id, etc.
                    nova_notifier.assert_any_call("create_router", {},
                                                  mock.ANY)
                    nova_notifier.assert_any_call("create_network", {},
                                                  mock.ANY)
                    nova_notifier.assert_any_call("create_subnet", {},
                                                  mock.ANY)
                    nova_notifier.assert_any_call("create_port", {},
                                                  mock.ANY)

# TODO(Sumit): XML tests
