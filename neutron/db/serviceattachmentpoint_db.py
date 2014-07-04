# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2014 OpenStack Foundation.
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

import sqlalchemy as sa
from sqlalchemy.orm import exc as sa_exc

#from neutron.api.v2 import attributes
from neutron.common import exceptions as n_exc
from neutron.db import db_base_plugin_v2 as base_db
from neutron.db import model_base
from neutron.db import models_v2
from neutron.extensions import serviceattachmentpoint
from neutron import manager
from neutron.openstack.common import log as logging
from neutron.openstack.common import uuidutils
from neutron.plugins.common import constants

LOG = logging.getLogger(__name__)


class ServiceAttachmentPoint(model_base.BASEV2, models_v2.HasId,
                             models_v2.HasTenant):
    """Represents a Service Attachment Point."""

    __tablename__ = 'service_attachment_point'
    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    insert_mode = sa.Column(sa.Enum(constants.SERVICE_AP_INSERT_MODE_L1,
                                    constants.SERVICE_AP_INSERT_MODE_L2,
                                    constants.SERVICE_AP_INSERT_MODE_L3),
                            nullable=False)
    service_ap_type = sa.Column(sa.Enum(constants.SERVICE_AP_NEUTRON_PORT,
                                        constants.SERVICE_AP_ROUTER,
                                        constants.SERVICE_AP_EXTERNAL_AP,
                                        name="service_attachment_point_type"),
                                nullable=False)
    role = sa.Column(sa.String(32))
    attachment_point_id = sa.Column(sa.String(36), nullable=True)


class ServiceAttachmentPointDbMixin(
    serviceattachmentpoint.ServiceAttachmentPointPluginBase,
    base_db.CommonDbMixin):
    """Mixin class for Service Attachment Point DB implementation."""

    @property
    def _core_plugin(self):
        return manager.NeutronManager.get_plugin()

    def _get_service_attachment_point(self, context, id):
        try:
            return self._get_by_id(context, ServiceAttachmentPoint, id)
        except sa_exc.NoResultFound:
            raise n_exc.ServiceAttachmentPointNotFound(id=id)

    def _make_service_attachment_point_dict(self, service_ap, fields=None):
        res = {'id': service_ap['id'],
               'tenant_id': service_ap['tenant_id'],
               'name': service_ap['name'],
               'description': service_ap['description'],
               'insert_mode': service_ap['insert_mode'],
               'service_ap_type': service_ap['service_ap_type'],
               'role': service_ap['role'],
               'attachment_point_id': service_ap['attachment_point_id']}
        return self._fields(res, fields)

    def get_service_attachment_points(self, context, filters=None, fields=None,
                                      sorts=None, limit=None, marker=None,
                                      page_reverse=False):
        LOG.debug(_("get_service_attachment_points() called"))
        return self._get_collection(context, ServiceAttachmentPoint,
                                    self._make_service_attachment_point_dict,
                                    filters=filters, fields=fields)

    def get_service_attachment_point(self, context, id, fields=None):
        LOG.debug(_("get_service_attachment_point() called"))
        ap = self._get_service_attachment_point(context, id)
        return self._make_service_attachment_point_dict(ap, fields)

    def create_service_attachment_point(self, context, service_ap):
        LOG.debug(_("create_service_attachment_point() called"))
        ap = service_ap['service_attachment_point']
        tenant_id = self._get_tenant_id_for_create(context, ap)

        # TODO(Stephen): Needs to query the service to allocate a service
        # attachment point.
        # For example:
        # service_id = ap.get('service_id')
        # subnet_id = ap.get('subnet_id')
        # role = ap.get('role')
        #
        # insert_mode, ap_type, ap_id = service.allocate_interface(
        #     subnet_id, role)
        #
        # Depending the type of ep_id, the corresponding service ap can be
        # created with the ap_type and attachment_point_id

        # TODO(Stephen): For now, mock the insert_mode, ap_type, and ap_id
        insert_mode = constants.SERVICE_AP_INSERT_MODE_L3
        ap_type = constants.SERVICE_AP_NEUTRON_PORT
        role = 'ingress'
        ap_id = None
        with context.session.begin(subtransactions=True):
            ap_db = ServiceAttachmentPoint(
                id=uuidutils.generate_uuid(),
                tenant_id=tenant_id,
                name=ap.get('name'),
                description=ap.get('description'),
                insert_mode=insert_mode,
                service_ap_type=ap_type,
                role=role,
                attachment_point_id=ap_id)
            context.session.add(ap_db)
        return self._make_service_attachment_point_dict(ap_db)

    def update_service_attachment_point(self, context, id, service_ap):
        """Only name and description are allowed to be changed."""
        LOG.debug(_("update_service_attachment_point() called"))
        attrs = service_ap['service_attachment_point']

        session = context.session
        with context.session.begin(subtransactions=True):
            try:
                (session.query(ServiceAttachmentPoint).
                    enable_eagerloads(False).
                    filter_by(id=id).with_lockmode('update').one())
            except sa_exc.NoResultFound:
                LOG.error(_("The service attachment point '%s' doesn't "
                            "exist"), id)
                raise n_exc.ServiceAttachmentPointNotFound(service_ap_id=id)

            service_ap_query = context.session.query(
                ServiceAttachmentPoint).with_lockmode('update')
            service_ap_db = service_ap_query.filter_by(id=id).one()
            service_ap_db.update(attrs)
        return self._make_service_attachment_point_dict(service_ap_db)

    def delete_service_attachment_point(self, context, id):
        LOG.debug(_("delete_service_attachment_point() called"))
        session = context.session
        with context.session.begin(subtransactions=True):
            try:
                ap_db = (session.query(ServiceAttachmentPoint).
                         enable_eagerloads(False).
                         filter_by(id=id).with_lockmode('update').one())
            except sa_exc.NoResultFound:
                LOG.error(_("The service attachment point '%s' doesn't "
                            "exist"), id)
                return

            # TODO(Stephen): notify the service about the ap deletion
            service_ap_query = context.session.query(
                ServiceAttachmentPoint).with_lockmode('update')
            ap_db = service_ap_query.filter_by(id=id).one()
            context.session.delete(ap_db)
