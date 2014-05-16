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


@six.add_metaclass(abc.ABCMeta)
class EndpointContext(object):
    """Context passed to policy engine for endpoint resource changes.

    An EndpointContext instance wraps an endpoint resource. It provides
    helper methods for accessing other relevant information. Results
    from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the endpoint.

        Return the current state of the endpoint, as defined by
        GroupPolicyPlugin.create_endpoint.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the endpoint.

        Return the original state of the endpoint, prior to a call to
        update_endpoint. Method is only valid within calls to
        update_endpoint_precommit and update_endpoint_postcommit.
        """
        pass

    @abc.abstractmethod
    def set_neutron_port_id(self, port_id):
        """Set the neutron port for the endpoint.

        :param port_id: Port to which endpoint is mapped.

        Set the neutron port to which the endpoint is mapped.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class EndpointGroupContext(object):
    """Context passed to policy engine for endpoint_group resource changes.

    An EndpointContext instance wraps an endpoint_group resource. It provides
    helper methods for accessing other relevant information. Results
    from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the endpoint_group.

        Return the current state of the endpoint_group, as defined by
        GroupPolicyPlugin.create_endpoint_group.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the endpoint_group.

        Return the original state of the endpoint_group, prior to a call to
        update_endpoint_group. Method is only valid within calls to
        update_endpoint_group_precommit and update_endpoint_group_postcommit.
        """
        pass

    @abc.abstractmethod
    def set_bridge_domain_id(self, bridge_domain_id):
        """Set the bridge_domain for the endpoint_group.

        :param bridge_domain_id: bridge_domain for the endpoint_group.

        Set the bridge_domain for the endpoint_group.
        """
        pass

    @abc.abstractmethod
    def is_cidr_available(self, cidr):
        """Check if CIDR is available.

        :param cidr: CIDR to check.

        Return True iff the specified CIDR does not overlap with any
        subnets currently allocated within this endpoint_group's
        bridge_domain's routing_domain. Note that this does not lock
        anything, so its only a hint.
        """
        pass

    @abc.abstractmethod
    def add_neutron_subnet(self, subnet_id):
        """Add the neutron subnet to the endpoint_group.

        :param subnet_id: Subnet to which endpoint_group is mapped.

        Add a neutron subnet to the set of subnets to which the
        endpoint_group is mapped.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class ContractContext(object):
    """Context passed to policy engine for changes to contract resources.

    An ContractContext instance wraps an contract resource. It provides
    helper methods for accessing other relevant information. Results
    from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the contract.

        Return the current state of the contract, as defined by
        GroupPolicyPlugin.create_contract.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the contract.

        Return the original state of the contract, prior to a call to
        update_contract. Method is only valid within calls to
        update_contract_precommit and update_contract_postcommit.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class PolicyRuleContext(object):
    """Context passed to policy engine for policy_rule resource changes.

    An PolicyRuleContext instance wraps an policy_rule resource.
    It provides helper methods for accessing other relevant information.
    Results from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the policy_rule.

        Return the current state of the policy_rule, as defined by
        GroupPolicyPlugin.create_policy_rule.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the policy_rule.

        Return the original state of the policy_rule, prior to a call to
        update_policy_rule. Method is only valid within calls to
        update_policy_rule_precommit and
        update_policy_rule_postcommit.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class PolicyClassifierContext(object):
    """Context passed to policy engine for policy_classifier resource changes.

    An PolicyClassifierContext instance wraps an policy_classifier resource.
    It provides helper methods for accessing other relevant information.
    Results from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the policy_classifier.

        Return the current state of the policy_classifier, as defined by
        GroupPolicyPlugin.create_policy_classifier.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the policy_classifier.

        Return the original state of the policy_classifier, prior to a call to
        update_policy_classifier. Method is only valid within calls to
        update_policy_classifier_precommit and
        update_policy_classifier_postcommit.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class PolicyActionContext(object):
    """Context passed to policy engine for policy_action resource changes.

    An PolicyActionContext instance wraps an policy_action resource.
    It provides helper methods for accessing other relevant information.
    Results from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the policy_action.

        Return the current state of the policy_action, as defined by
        GroupPolicyPlugin.create_policy_action.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the policy_action.

        Return the original state of the policy_action, prior to a call to
        update_policy_action. Method is only valid within calls to
        update_policy_action_precommit and update_policy_action_postcommit.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class BridgeDomainContext(object):
    """Context passed to policy engine for bridge_domain resource changes.

    A BridgeDomainContext instance wraps an bridge_domain resource. It provides
    helper methods for accessing other relevant information. Results
    from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the bridge_domain.

        Return the current state of the bridge_domain, as defined by
        GroupPolicyPlugin.create_bridge_domain.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the bridge_domain.

        Return the original state of the bridge_domain, prior to a call to
        update_bridge_domain. Method is only valid within calls to
        update_bridge_domain_precommit and update_bridge_domain_postcommit.
        """
        pass

    @abc.abstractmethod
    def set_routing_domain_id(self, routing_domain_id):
        """Set the routing_domain for the bridge_domain.

        :param routing_domain_id: routing_domain for the bridge_domain.

        Set the routing_domain for the bridge_domain.
        """
        pass

    @abc.abstractmethod
    def set_neutron_network_id(self, network_id):
        """Set the neutron network for the bridge_domain.

        :param network_id: Network to which bridge_domain is mapped.

        Set the neutron network to which the bridge_domain is mapped.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class RoutingDomainContext(object):

    """Context passed to policy engine for routing_domain resource changes.

    A RoutingDomainContext instance wraps an routing_domain resource.xi
    It provides helper methods for accessing other relevant information.
    Results from expensive operations are cached for convenient access.
    """

    @abc.abstractproperty
    def current(self):
        """Return the current state of the routing_domain.

        Return the current state of the routing_domain, as defined by
        GroupPolicyPlugin.create_routing_domain.
        """
        pass

    @abc.abstractproperty
    def original(self):
        """Return the original state of the routing_domain.

        Return the original state of the routing_domain, prior to a call to
        update_routing_domain. Method is only valid within calls to
        update_routing_domain_precommit and update_routing_domain_postcommit.
        """
        pass

    @abc.abstractmethod
    def add_neutron_router(self, router_id):
        """Add the neutron router to the routing_domain.

        :param router_id: Router to which routing_domain is mapped.

        Add a neutron router to the set of routers to which the
        routing_domain is mapped.
        """
        pass


@six.add_metaclass(abc.ABCMeta)
class PolicyDriver(object):
    """Define stable abstract interface for Group Policy drivers.

    A policy driver is called on the creation, update, and deletion
    of all Group Policy resources. For every event, there are two methods that
    get called - one within the database transaction (method suffix of
    _precommit), one right afterwards (method suffix of _postcommit).

    Exceptions raised by methods called inside the transaction can
    rollback, but should not make any blocking calls (for example,
    REST requests to an outside controller). Methods called after
    transaction commits can make blocking external calls, though these
    will block the entire process. Exceptions raised in calls after
    the transaction commits may cause the associated resource to be
    deleted.

    Because rollback outside of the transaction is not done in the
    case of update of resources, all data validation must be done within
    methods that are part of the database transaction.
    """

    @abc.abstractmethod
    def initialize(self):
        """Perform driver initialization.

        Called after all drivers have been loaded and the database has
        been initialized. No abstract methods defined below will be
        called prior to this method being called.
        """
        pass

    def create_endpoint_precommit(self, context):
        """Allocate resources for a new endpoint.

        :param context: EndpointContext instance describing the new
        endpoint.
        """
        pass

    def create_endpoint_postcommit(self, context):
        """Create a endpoint.

        :param context: EndpointContext instance describing the new
        endpoint.
        """
        pass

    def update_endpoint_precommit(self, context):
        """Update resources of a endpoint.

        :param context: EndpointContext instance describing the new
        state of the endpoint, as well as the original state prior
        to the update_endpoint call.
        """
        pass

    def update_endpoint_postcommit(self, context):
        """Update a endpoint.

        :param context: EndpointContext instance describing the new
        state of the endpoint, as well as the original state prior
        to the update_endpoint call.
        """
        pass

    def delete_endpoint_precommit(self, context):
        """Delete resources for a endpoint.

        :param context: EndpointContext instance describing the current
        state of the endpoint, prior to the call to delete it.
        """
        pass

    def delete_endpoint_postcommit(self, context):
        """Delete a endpoint.

        :param context: EndpointContext instance describing the current
        state of the endpoint, prior to the call to delete it.
        """
        pass

    def create_endpoint_group_precommit(self, context):
        """Allocate resources for a new endpoint_group.

        :param context: EndpointGroupContext instance describing the new
        endpoint_group.
        """
        pass

    def create_endpoint_group_postcommit(self, context):
        """Create a endpoint_group.

        :param context: EndpointGroupContext instance describing the new
        endpoint_group.
        """
        pass

    def update_endpoint_group_precommit(self, context):
        """Update resources of a endpoint_group.

        :param context: EndpointGroupContext instance describing the new
        state of the endpoint_group, as well as the original state prior
        to the update_endpoint_group call.
        """
        pass

    def update_endpoint_group_postcommit(self, context):
        """Update a endpoint_group.

        :param context: EndpointGroupContext instance describing the new
        state of the endpoint_group, as well as the original state prior
        to the update_endpoint_group call.
        """
        pass

    def delete_endpoint_group_precommit(self, context):
        """Delete resources for a endpoint_group.

        :param context: EndpointGroupContext instance describing the current
        state of the endpoint_group, prior to the call to delete it.
        """
        pass

    def delete_endpoint_group_postcommit(self, context):
        """Delete a endpoint_group.

        :param context: EndpointGroupContext instance describing the current
        state of the endpoint_group, prior to the call to delete it.
        """
        pass

    def create_bridge_domain_precommit(self, context):
        """Allocate resources for a new bridge_domain.

        :param context: BridgeContext instance describing the new
        bridge_domain.
        """
        pass

    def create_bridge_domain_postcommit(self, context):
        """Create a bridge_domain.

        :param context: BridgeContext instance describing the new
        bridge_domain.
        """
        pass

    def update_bridge_domain_precommit(self, context):
        """Update resources of a bridge_domain.

        :param context: BridgeContext instance describing the new
        state of the bridge_domain, as well as the original state prior
        to the update_bridge_domain call.
        """
        pass

    def update_bridge_domain_postcommit(self, context):
        """Update a bridge_domain.

        :param context: BridgeContext instance describing the new
        state of the bridge_domain, as well as the original state prior
        to the update_bridge_domain call.
        """
        pass

    def delete_bridge_domain_precommit(self, context):
        """Delete resources for a bridge_domain.

        :param context: BridgeContext instance describing the current
        state of the bridge_domain, prior to the call to delete it.
        """
        pass

    def delete_bridge_domain_postcommit(self, context):
        """Delete a bridge_domain.

        :param context: BridgeContext instance describing the current
        state of the bridge_domain, prior to the call to delete it.
        """
        pass

    def create_routing_domain_precommit(self, context):
        """Allocate resources for a new routing_domain.

        :param context: RoutingContext instance describing the new
        routing_domain.
        """
        pass

    def create_routing_domain_postcommit(self, context):
        """Create a routing_domain.

        :param context: RoutingContext instance describing the new
        routing_domain.
        """
        pass

    def update_routing_domain_precommit(self, context):
        """Update resources of a routing_domain.

        :param context: RoutingContext instance describing the new
        state of the routing_domain, as well as the original state prior
        to the update_routing_domain call.
        """
        pass

    def update_routing_domain_postcommit(self, context):
        """Update a routing_domain.

        :param context: RoutingContext instance describing the new
        state of the routing_domain, as well as the original state prior
        to the update_routing_domain call.
        """
        pass

    def delete_routing_domain_precommit(self, context):
        """Delete resources for a routing_domain.

        :param context: RoutingContext instance describing the current
        state of the routing_domain, prior to the call to delete it.
        """
        pass

    def delete_routing_domain_postcommit(self, context):
        """Delete a routing_domain.

        :param context: RoutingContext instance describing the current
        state of the routing_domain, prior to the call to delete it.
        """
        pass
