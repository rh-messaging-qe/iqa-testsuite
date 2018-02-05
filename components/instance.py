from autologging import logged, traced

import amom.router
import amom.broker
import amom.client

from components.nodes.node import Node
from components.nodes.executions.ansible import AnsibleCMD


@logged
@traced
class IQAInstance:
    """
    iQA helper class

    Store variables, nodes and related things
    """
    def __init__(self, inventory=''):
        self.inventory = inventory
        self.nodes = []
        self.components = []
        self.ansible = AnsibleCMD(inventory)

    def new_node(self, hostname, ip=None):
        """
        Create new node under iQA instance

        @TODO Pass inventory by true way for Ansible

        :param hostname
        :param ip
        :return: Node()
        """
        node = Node(hostname=hostname, ip=ip, ansible=self.ansible)
        self.nodes.append(node)
        return node

    def new_component(self, node: Node, component):
        """
        Create new node under iQA instance

        @TODO Pass inventory by true way for Ansible

        :param node
        :param component
        :return: component()
        """
        new_component = node.new_component(component)
        self.components.append(new_component)
        return new_component
        :return:
        """
        component = component(node=node)
        self.components.append(node)
        return component
