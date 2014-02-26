# Copyright (c) 2014 OpenStack Foundation
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
from sqlalchemy import orm

from neutron.common import exceptions as neutron_exceptions
from neutron.db import db_base_plugin_v2 as base_db
from neutron.db import model_base
from neutron.db import models_v2
from neutron import manager
from neutron.openstack.common import uuidutils


'''
Group Policy model:

   tables                classes
   ------------------    -----------
   gp_endpoint           Endpoint
   gp_group              Group

   gp_policy             Policy
   gp_policy_rule        Policy_rule
   gp_classifier         Classifier
   gp_action             Action

   gp_group_endpoint     GroupEndpointAssociation
   gp_group_policy       GroupPolicyAssociation

The gp_group_endpoint  and gp_group_policy tables are association tables
establishing the many-to-many relationship between "groups and endpoints"
and "groups and policis", respectively.

The GroupPolicyDb provides the methods for populating the tables and
establishing the relationship when necessary.

'''


class Group(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    """Represent persistent state of a Policy Group.

    A collection of Endpoints.
    """

    __tablename__ = 'gp_group'

    name = sa.Column(sa.String(255))
    endpoints = orm.relationship('GroupEndpointAssociation',
                                 backref="gp_group",
                                 cascade="all, delete-orphan")

    policies = orm.relationship('GroupPolicyAssociation',
                                backref="gp_group",
                                cascade="all, delete-orphan")


class Endpoint(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    """Represent persistent state of an Endpoint.

    An endpoint can currently be either a Neutron Port or a Neutron Network.

    """

    __tablename__ = 'gp_endpoint'

    name = sa.Column(sa.String(255))
    endpoint_type = sa.Column(sa.Enum("network", "port",
                                      name="policy_group_endpoint_type"),
                              nullable=False)
    reference_network = sa.Column(sa.String(36),
                                  sa.ForeignKey('networks.id',
                                                ondelete="CASCADE"),
                                  nullable=False)
    reference_port = sa.Column(sa.String(36),
                               sa.ForeignKey('ports.id', ondelete="CASCADE"),
                               nullable=False)

    reference_id = property(
        lambda self: getattr(self,
                             'reference_%s' %
                             ('network'
                              if self.endpoint_type == 'network'
                              else 'port')))

    groups = orm.relationship('GroupEndpointAssociation',
                              backref='gp_endpoint',
                              cascade="all", lazy="joined"
                              )


class GroupEndpointAssociation(model_base.BASEV2,
                               models_v2.HasStatusDescription):
    """Many-to-many association between group and endpoint classes."""

    __tablename__ = 'gp_group_endpoint'

    group_id = sa.Column(sa.String(36),
                         sa.ForeignKey('gp_group.id'),
                         primary_key=True)
    endpoint_id = sa.Column(sa.String(36),
                            sa.ForeignKey('gp_endpoint.id'),
                            primary_key=True)


class GroupPolicyAssociation(model_base.BASEV2,
                             models_v2.HasStatusDescription):
    """Many-to-many association between group and policy classes."""

    __tablename__ = 'gp_group_policy'

    group_id = sa.Column(sa.String(36),
                         sa.ForeignKey('gp_group.id'),
                         primary_key=True)
    policy_id = sa.Column(sa.String(36),
                          sa.ForeignKey('gp_policy.id'),
                          primary_key=True)
    src_dst_type = sa.Column(sa.Enum("source", "destination",
                                     name="classifier_type"),
                             nullable=False)


class Policy(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    """Represent persistent state of a Policy Group.

    """

    __tablename__ = 'gp_policy'

    name = sa.Column(sa.String(255))
    #src_group = sa.Column(sa.String(255))   ..... m-to-m
    #dst_group = sa.Column(sa.String(255))   ..... m-to-m
    groups = orm.relationship('GroupPolicyAssociation',
                              backref='gp_policy',
                              cascade="all", lazy="joined"
                              )

    bidirectional = sa.Column(sa.Boolean)
    policy_rules = orm.relationship('Policy_rule',
                                    backref='gp_policy',
                                    lazy="joined",
                                    cascade='delete')


class Policy_rule(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    """Represent persistent state of a Policy Rules.

    Policy rules.

    """

    __tablename__ = 'gp_policy_rule'

    name = sa.Column(sa.String(255))
    classifier = orm.relationship('Classifier',
                                  backref='gp_policy_rule',
                                  uselist=False,
                                  lazy="joined",
                                  cascade='delete')

    actions = orm.relationship('Action',
                               backref='gp_policy_rule',
                               lazy="joined",
                               cascade='delete')
    policy = sa.Column(sa.String(36),
                       sa.ForeignKey('gp_policy.id', ondelete="CASCADE"),
                       nullable=False)


class Classifier(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    """Represent persistent state of a Classifier.

    A classifier.

    """

    __tablename__ = 'gp_classifier'

    name = sa.Column(sa.String(255))
    classifier_type = sa.Column(sa.Enum("unicast", "broadcast",
                                        name="classifier_type"),
                                nullable=False)

    ports = sa.Column(sa.String(255))   # .... range ....
    protocol = sa.Column(sa.Enum("tcp", "udp",
                                 name="protocol_type"),
                         nullable=False)
    policy_rule = sa.Column(sa.String(36),
                            sa.ForeignKey('gp_policy_rule.id',
                                          ondelete="CASCADE"),
                            nullable=False)


class Action(model_base.BASEV2, models_v2.HasId, models_v2.HasTenant):
    """Represent persistent state of an Action.

    Description of an Action.

    """

    __tablename__ = 'gp_action'

    name = sa.Column(sa.String(255))
    spec = sa.Column(sa.String(255))   # ..... use blob .....
    policy_rule = sa.Column(sa.String(36),
                            sa.ForeignKey('gp_policy_rule.id',
                                          ondelete="CASCADE"),
                            nullable=False)


'''



'''


class GroupPolicyDb(base_db.CommonDbMixin):
    """Wraps group policy with SQLAlchemy models.

    """

    @property
    def _core_plugin(self):
        return manager.NeutronManager.get_plugin()

    def _get_resource(self, context, model, id):
        try:
            r = self._get_by_id(context, model, id)
        except Exception:
            raise
        return r

    # Endpoint and Group
    def _make_endpoint_dict(self, endpoint, fields=None):
        res = {'id': endpoint['id'],
               'tenant_id': endpoint['tenant_id'],
               'name': endpoint['name'],
               'reference_id': endpoint['reference_id'],
               }

        # Get the associated groups
        res['groups'] = [group['id'] for group in endpoint['groups']]

        return self._fields(res, fields)

    def create_endpoint(self, context, endpoint):
        v = endpoint['endpoint']

        tenant_id = self._get_tenant_id_for_create(context, v)
        with context.session.begin(subtransactions=True):
            endpoint_db = Endpoint(id=uuidutils.generate_uuid(),
                                   tenant_id=tenant_id,
                                   name=v['name'],
                                   endpoint_type=v['endpoint_type'],
                                   reference_id=v['refernce_id'])

            context.session.add(endpoint_db)

        return self._make_endpoint_dict(endpoint_db)

    def _make_group_dict(self, group, fields=None):
        res = {'id': group['id'],
               'tenant_id': group['tenant_id'],
               'name': group['name'],
               }

        # Get the associated endpoints
        res['endpointss'] = [endpoint['id'] for endpoint in group['endpoints']]

        # Get the associated policies
        res['policies'] = [policy['id']
                           for policy in group['policies']]

        return self._fields(res, fields)

    def create_group(self, context, group):
        v = group['group']

        tenant_id = self._get_tenant_id_for_create(context, v)
        with context.session.begin(subtransactions=True):
            group_db = Group(id=uuidutils.generate_uuid(),
                             tenant_id=tenant_id,
                             name=v['name'])

            context.session.add(group_db)

        return self._make_group_dict(group_db)

    def create_group_endpoints(self, context, endpoint, group_id):
        endpoint_id = endpoint['endpoint']['id']
        with context.session.begin(subtransactions=True):
            assoc_qry = context.session.query(GroupEndpointAssociation)
            assoc = assoc_qry.filter_by(group_id=group_id,
                                        endpoint_id=endpoint_id).first()
            if assoc:
                raise GroupEndpointAssociationExists(
                    endpoint_id=endpoint_id, group_id=group_id)

            group = self._get_resource(context, Group, group_id)

            assoc = GroupEndpointAssociation(group_id=group_id,
                                             endpoint_id=endpoint_id)
            group.endpoints.append(assoc)
            endpoints = [myendpoint['endpoint_id']
                         for myendpoint in group['endpoints']]

        res = {"endpoint": endpoints}
        return res


class GroupEndpointAssociationExists(neutron_exceptions.Conflict):
    message = _('endpoint %(endpoint_id)s is already associated '
                'with group %(group_id)s')
