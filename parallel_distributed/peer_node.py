# Class Peer untuk implementasi P2P client
from p2pnetwork.node import Node

class PeerNode(Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super(PeerNode, self).__init__(host, port, id, callback, max_connections)

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)

    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        print("node_message from " + connected_node.id + ":\n" + str(data))

    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)

    def node_request_to_stop(self):
        print("node is requested to stop!")


# Main program: menjalankan dua peers yang pasif
if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if len(args) < 2:
        print("usage: python peer_node.py ip port [port2] [...]")
        sys.exit()

    # The port for each peer to listen for incoming node connections
    my_ip = args[0]
    ports = [int(a) for a in args[1:]]
    peers = list()

    for port in ports:
        # Instantiate the Peer
        peer = PeerNode(my_ip, port)
        # Start the node, if not started it shall not handle any requests!
        peer.start()
        peers.append(peer)


    # Wait until said "stop"
    stopped = False
    while not stopped:
        command = input("? ")
        if (command.lower() == "help"):
            print("stop: stop the peer node, help: show this help message")
        elif (command.lower() == "stop"):
            stopped = True

    for peer in peers:
        peer.stop()
