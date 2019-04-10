"""
Simple example that demonstrates how to use IQA abstract and tools
to handle clients abstract through a router or broker component.
"""
import sys

from iqa.components.abstract.component import Component, Sender, Server
from iqa.components.abstract.component import Receiver
from iqa.components.abstract.component import Router
from iqa.messaging_abstract.message import Message
from messaging_components.clients import ClientExternal, ReceiverJava
from pytest_iqa.instance import IQAInstance

# Inventory file to use
TIMEOUT = 10
MESSAGE_COUNT = 1000
inventory = sys.argv[1] if len(sys.argv) > 1 else 'inventory_local.yml'

# Message explaining what this sample does
intro_message = """
This sample will first iterate through all abstract (router/broker and clients)
defined through the inventory file %s and then it will start:
- One receiver instance of each client consuming messages from:
  /client/<implementation> (implementation being: java, python or nodejs)
  - Receivers will expect 1000 messages each
- One sender instance of each client sending messages to the same address
  pattern explained above (small message)
- Display results
""" % inventory
print(intro_message)

# Loading the instance
print("Loading IQAInstance using inventory file: %s" % inventory)
iqa = IQAInstance(inventory)

# Listing all routers in inventory
print("\n-> List of abstract abstract parsed from inventory")
for component in iqa.components:  # type: Component

    # List component name and type
    print("   * Name: %-20s | Type: %-10s | Implementation: %s" % (
        component.node.hostname,
        type(component),
        component.implementation
    ))

# Router instance to use on clients
router_or_broker = None
for component in iqa.components:
    if isinstance(component, Server):
        router_or_broker = component
assert router_or_broker or 'No Router or Broker component defined in inventory file.'

# Starting receivers
print("\n-> Starting receiver against [%s]" % type(router_or_broker))
for receiver in iqa.get_clients(Receiver):
    receiver.set_url('amqp://%s:%s/client/%s' % (router_or_broker.node.get_ip(), '5672', receiver.implementation))
    receiver.command.stdout = True
    receiver.command.timeout = TIMEOUT
    receiver.command.control.timeout = TIMEOUT
    receiver.command.control.count = MESSAGE_COUNT
    receiver.command.logging.log_msgs = 'dict'
    print("   -> starting %s receiver" % receiver.implementation)
    receiver.receive()


# Starting senders
print("-> Starting sender abstract")
msg = Message(body="1234567890")
for sender in iqa.get_clients(Sender):
    sender.set_url('amqp://%s:%s/client/%s' % (router_or_broker.node.get_ip(), '5672', sender.implementation))
    sender.command.timeout = TIMEOUT
    sender.command.control.timeout = TIMEOUT
    sender.command.control.count = MESSAGE_COUNT
    print("   -> starting %s sender" % sender.implementation)
    sender.send(msg)

# Wait till all senders and receivers are done
print("\n** Waiting all senders and receivers to complete **")
client_errors = []
for client in iqa.get_clients(Sender) + iqa.get_clients(Receiver):  # type: ClientExternal
    # Wait till execution finishes/timeout
    while client.execution.is_running():
        pass

    # Validate return code
    if not client.execution.completed_successfully():
        client_errors.append(client)

# Verifying clients
if not client_errors:
    all_msgs_received = True
    for receiver in iqa.get_clients(Receiver):
        received_count = len(receiver.execution.read_stdout(lines=True))
        if MESSAGE_COUNT != received_count:
            all_msgs_received = False
            print('   -> Receiver [%s] received %d out of %d expected messages'
                  % (receiver.implementation, received_count, MESSAGE_COUNT))

    if all_msgs_received:
        print("   => All clients completed successfully")
    else:
        print("   => Some clients did not receive all expected messages")
else:
    print("   => The following clients did not complete successfully:")
    for client in client_errors:  # Type: ClientExternal
        client_type = 'receiver' if isinstance(client, Receiver) else 'sender'
        print('      - %s [%s]' % (client_type, client.implementation))
