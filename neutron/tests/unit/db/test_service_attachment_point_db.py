# Copyright (c) 2014 OpenStack Foundation.
#
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

from neutron import context
from neutron.db import api as db
from neutron.db import db_base_plugin_v2 as base_plugin
from neutron.db import serviceattachmentpoint_db
from neutron.plugins.common import constants
from neutron.tests import base


class FakePlugin(base_plugin.NeutronDbPluginV2,
                 serviceattachmentpoint_db.ServiceAttachmentPointDbMixin):
    """A fake plugin class containing all DB methods."""
    pass


test_port_ap = {'service_attachment_point': {
    'name': 'test-name',
    'description': 'test-description',
    'insert_mode': constants.SERVICE_AP_INSERT_MODE_L3,
    'role': 'ingress',
    'service_ap_type': constants.SERVICE_AP_NEUTRON_PORT,
    'attachment_point_id': '981797982872'}}

test_router_ap = test_port_ap
test_router_ap['service_attachment_point']['service_ap_type'] = (
    constants.SERVICE_AP_ROUTER)

test_external_ap = test_port_ap
test_external_ap['service_attachment_point']['service_ap_type'] = (
    constants.SERVICE_AP_EXTERNAL_AP)


class TestDbServiceAttachmentPoint(base.BaseTestCase):
    def setUp(self):
        super(TestDbServiceAttachmentPoint, self).setUp()
        self.plugin = FakePlugin()
        self.context = context.get_admin_context()
        self.addCleanup(db.clear_db)

    def _test_create_service_attachment_point(self, test_ap):
        expected_ap_type = (
            test_ap['service_attachment_point']['service_ap_type'])
        self.plugin.create_service_attachment_point(self.context, test_ap)
        aps = self.plugin.get_service_attachment_points(self.context)
        self.assertEqual(1, len(aps))
        self.assertEqual(expected_ap_type, aps[0]['service_ap_type'])
        one_ap = self.plugin.get_service_attachment_point(self.context,
                                                          aps[0]['id'])
        self.assertEqual(one_ap, aps[0])

    def test_create_service_attachment_point_to_neutron_port(self):
        self._test_create_service_attachment_point(test_port_ap)

    def test_create_service_attachment_point_to_router(self):
        self._test_create_service_attachment_point(test_router_ap)

    def test_create_service_attachment_point_to_external(self):
        self._test_create_service_attachment_point(test_external_ap)

    def _test_delete_service_attachment_point(self, test_ap):
        self._test_create_service_attachment_point(test_ap)
        aps = self.plugin.get_service_attachment_points(self.context)
        self.assertEqual(1, len(aps))
        self.plugin.delete_service_attachment_point(self.context, aps[0]['id'])
        aps = self.plugin.get_service_attachment_points(self.context)
        self.assertFalse(aps)

    def test_delete_service_attachment_point_to_neutron_port(self):
        self._test_delete_service_attachment_point(test_port_ap)

    def test_delete_service_attachment_point_to_router(self):
        self._test_delete_service_attachment_point(test_router_ap)

    def test_delete_service_attachment_point_to_external(self):
        self._test_delete_service_attachment_point(test_external_ap)
