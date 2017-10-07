

"""
This is a trivial simulation of unmanaged switch's operations
"""

from sys import exit


# Class NetDevice is a general model of a networking device
# Note that this model is not supposed to provide a simulation of all functions of real gears
class NetDevice:

    # Create a networking device with a num of ports provided

    def __init__(self, num_ports):
        self.num_ports = abs(num_ports)
        self.ports = {}
        for port in range(num_ports):
            self.ports['port_{}'.format(str(port))] = {'sent_frames': {'sent': 0, 'buffer': []}, 'received': 0}
            # Buffer stores frames' destination MAC addresses which are checked by target hosts

    # Request a number of datagrams sent out of a specified port

    def get_sent_for_port(self, port_num):
        return self.ports['port_{}'.format(str(port_num))]['sent_frames']['sent']

    # Request a number of datagrams received at a specified port

    def get_received_for_port(self, port_num):
        return self.ports['port_{}'.format(str(port_num))]['received']

    # Total number of datagrams sent by the net device

    @property
    def total_sent(self):
        sent = 0
        for port in self.ports:
            sent += self.ports[port]['sent_frames']['sent']
        return sent

    # Total number of datagrams received by the net device

    @property
    def total_received(self):
        received = 0
        for port in self.ports:
            received += self.ports[port]['received']
        return received

    # Receiving datagram

    def receive(self, port_num):
        self.ports['port_{}'.format(port_num)]['received'] += 1

    # Sending datagram

    def send(self, port_num):
        self.ports['port_{}'.format(port_num)]['sent_frames']['sent'] += 1


# This is a class for a network switch object
class Switch(NetDevice):

    # Create a switch with a num of ports provided

    def __init__(self, num_ports):
        self.mac_table = {}
        self.vlan_db = {'vlan1': set()}
        super().__init__(num_ports)
        for port in self.ports:
            self.vlan_db['vlan1'].add(port)

    # Learn a new MAC address

    def _learn_mac(self, source_mac, port_num):
        if source_mac not in self.mac_table:
            port_vlan = ''
            for vlan in self.vlan_db:
                if 'port_{}'.format(port_num) in self.vlan_db[vlan]:
                    port_vlan = vlan
                    break
            self.mac_table[source_mac] = [port_num, 0, port_vlan]

    # Update timers of MAC table entries

    def _update_timers(self, source_mac):
        self.mac_table[source_mac][1] = 0
        for mac in self.mac_table:
            if mac != source_mac:
                self.mac_table[mac][1] += 1

    # Remove outdated records: after 5 steps (where each step is sending 1 frame by command 'send';
    # if multiple frames're sent at a time, it counts as several steps) a record for a MAC, which hasn't been
    # seen by the switch during 5 steps, will be removed from the switch's MAC table

    def _remove_mac(self):
        for_removal = []
        for mac in self.mac_table:
            if self.mac_table[mac][1] >= 5:
                for_removal.append(mac)
        for mac in for_removal:
            del self.mac_table[mac]

    # This method clears a port buffer for a particular port; it's used to remove frames which were not "pulled"
    # by connected hosts; that means that those frames were lost in transit

    def flush_buffer(self, port_num):
        self.ports['port_{}'.format(port_num)]['sent_frames']['buffer'] = []

    # Provides details about port-to-VLAN associations:

    @property
    def vlan_database(self):
        vlans = {}
        for vlan in self.vlan_db:
            vlans[vlan] = list(self.vlan_db[vlan])
            vlans[vlan].sort()
        return vlans

    # This method provides an interface for workstations to send their frames

    def send_frame(self, source_mac, dest_mac, port_num):
        for port in self.ports:
            number = port.split('_')[1]
            self.flush_buffer(number)
        self._learn_mac(source_mac, port_num)
        self._update_timers(source_mac)
        self._remove_mac()
        self.receive(port_num)
        if dest_mac in self.mac_table:
            if self.mac_table[source_mac][2] == self.mac_table[dest_mac][2]:
                self.send(self.mac_table[dest_mac][0])
                self.ports['port_{}'.format(self.mac_table[dest_mac][0])]['sent_frames']['buffer'].append(dest_mac)
        else:
            for port in self.vlan_db[self.mac_table[source_mac][2]]:
                if port != 'port_{}'.format(port_num):
                    self.ports[port]['sent_frames']['buffer'].append(dest_mac)
                    self.ports[port]['sent_frames']['sent'] += 1

    # This method allows to create a VLAN on a switch

    def create_vlan(self, vlan_num):
        if 'vlan{}'.format(vlan_num) not in self.vlan_db:
            self.vlan_db['vlan{}'.format(vlan_num)] = set()

    # This method allows to assign ports to a VLAN, provided that the VLAN exists and all port numbers do not
    # exceed the switch's (num_ports - 1), which is a maximum port number

    def assign_ports_to_vlan(self, vlan_num, vlan_ports):
        if 'vlan{}'.format(vlan_num) in self.vlan_db:
            for port in vlan_ports:
                if int(port) < self.num_ports:
                    self.vlan_db['vlan{}'.format(vlan_num)].add('port_{}'.format(port))
            for vlan in self.vlan_db:
                if vlan != 'vlan{}'.format(vlan_num):
                    for port in vlan_ports:
                        if "port_{}".format(port) in self.vlan_db[vlan]:
                            self.vlan_db[vlan].remove("port_{}".format(port))


# This is a class for workstation object. Acts as a client on a LAN
class Station(NetDevice):

    # Creating a workstation with one LAN port, MAC address and connecting it to a switch_port on the switch

    def __init__(self, mac, switch, switch_port):
        self._switch = switch
        self.switch_port = int(switch_port)
        self.mac = mac
        super().__init__(1)

    # Sending message to switch

    def send_msg(self, dest_mac):
        self._switch.send_frame(self.mac, dest_mac, self.switch_port)
        self.send(0)

    # Receiving message from the corresponding switch port

    def receive_msg(self):
        for mac in self._switch.ports['port_{}'.format(self.switch_port)]['sent_frames']['buffer']:
            if mac == self.mac:
                self._switch.ports['port_{}'.format(self.switch_port)]['sent_frames']['buffer'].remove(mac)
                self.receive(0)


# This is a main user environment
class RuntimeEnv:

    def __init__(self):
        self.network_objects = {'pc': {},
                                'switch': {}
                                }

    # Command line interface

    def shell(self):
        while True:
            command = input('> ')
            # Split command string into parts
            com_stack = command.split()

            # Help command
            if com_stack[0] == 'help':
                print('=' * 10)
                print("This is my attempt to create a simple simulation\n"
                      "of the most basic operations of a network switch.\n"
                      "Yes, I realize that this is not a fully-functional network\n"
                      "simulator. For now, it supports a single switch and a few PCs\n"
                      "connected to it.")
                print('=' * 10)
                print("Below is a list of all supported commands. All commands will prompt you for some input.\n"
                      "It should be quite clear.")
                print('-' * 10)
                print("'create switch' - this is where you start; this command will create a switch object for you.\n"
                      "Everything else is dependant on it\n")
                print("'create pc' - this command will create a workstation, which will be connected to your switch.\n"
                      "You have to manually specify MAC addresses\n")
                print("'show network' - briefly displays general statistics of your switch\n")
                print("'show switch <switch_name>' - displays more details about a state of your switch, e.g.\n"
                      "VLANs, ports, number of received frames, number of sent frames, etc.\n")
                print("'show pc <pc_name>' - similar command for your workstations\n")
                print("'switch vlan' - creates a vlan on your switch; optionally, allows you to assign ports to\n"
                      "the new VLAN\n")
                print("'switch assign' - assigns ports to an existing VLAN\n")
                print("'send' - allows you to manually send a frame from one workstation to another.\n"
                      "Then you can check reactions of all network devices using 'show' commands\n")
                print("'quit' - the meaning is obvious, isn't it?\n\n")
                continue

            # Analysis of 'create' command
            if com_stack[0] == 'create':

                # User can create either a switch or a workstation (PC)
                if com_stack[1] == 'switch' or com_stack[1] == 'pc':
                    while True:
                        # Giving a unique name to the device
                        name = input("Provide a name for your new device: ")
                        # Name must be unique
                        if (name in self.network_objects['switch']) or (name in self.network_objects['pc']):
                            print("Names must be unique")
                            continue
                        else:
                            break
                    # User creates a switch
                    if com_stack[1] == 'switch':
                        num_ports = int(input("How many ports (int number): "))
                        self.network_objects['switch'][name] = [Switch(num_ports), set()]   # Creating a switch object plus a set to store used ports
                    # Users creates a PC
                    if com_stack[1] == 'pc':
                        if len(self.network_objects['switch']) > 0:  # PC cannot be created without at least one switch
                            switch_name = input("Which switch is it connected to?(switch name): ")
                            mac_address = input("MAC address for your host (format xxxx.xxxx.xxxx, all hex digits): ")
                            # Checking if the port number isn't higher than a total number of ports on the switch,
                            # and the port is not used
                            while True:
                                port_num = int(input("Which switch port your host is connected to (int number): "))
                                if (self.network_objects['switch'][switch_name][0].num_ports >= abs(port_num)) and (port_num not in self.network_objects['switch'][switch_name][1]):
                                    self.network_objects['pc'][name] = [Station(mac_address, self.network_objects['switch'][switch_name][0], port_num), switch_name]
                                    self.network_objects['switch'][switch_name][1].add(port_num)
                                    break
                                else:
                                    print("Invalid input: switch doesn't have this port or this port is used")
                                    continue
                        else:
                            print("You have to create at least one switch")
                            continue
                else:
                    print("Invalid command")
                    continue

            # Analysis of 'show' command
            elif com_stack[0] == 'show':
                if len(com_stack) < 2:
                    print("Specify what to display")
                    continue
                # General info about existing switches
                if com_stack[1] == 'network':
                    if len(self.network_objects['switch']) > 0:
                        print("Switches:")
                        for sw_name in self.network_objects['switch']:
                            print("Switch name:{0}, number of ports:{1}, used:{2}".format(sw_name, self.network_objects['switch'][sw_name][0].num_ports,
                                                                                          self.network_objects['switch'][sw_name][1]))
                            pcs = ''
                            for pc_name in self.network_objects['pc']:
                                if self.network_objects['pc'][pc_name][1] == sw_name:
                                    pcs = pcs + pc_name + ' '
                            print('PCs connected: {}'.format(pcs))
                    else:
                        print("You haven't created any switches yet")
                        continue
                # Statistics for a specified switch
                elif com_stack[1] == 'switch':
                    if len(self.network_objects['switch']) == 0:
                        print("You haven't created any switches yet")
                        continue
                    if len(com_stack) < 3:
                        print("Switch name is missing")
                        continue
                    if self.network_objects['switch'][com_stack[2]]:
                        print("Switch stats:")
                        print("Name: {}".format(com_stack[2]))
                        print("Number of ports: {}".format(self.network_objects['switch'][com_stack[2]][0].num_ports))
                        print("Ports per VLAN")
                        vlan_stats = self.network_objects['switch'][com_stack[2]][0].vlan_database
                        for vlan in vlan_stats:
                            print(vlan.upper())
                            for port in vlan_stats[vlan]:
                                port_number = int(port.split('_')[1])
                                print("Port: {0}, frames sent:{1}, frames received:{2}".format(port, self.network_objects['switch'][com_stack[2]][0].get_sent_for_port(port_number),
                                                                                               self.network_objects['switch'][com_stack[2]][0].get_received_for_port(port_number)))
                        print("MAC table")
                        print("=" * 10)
                        for mac in self.network_objects['switch'][com_stack[2]][0].mac_table:
                            print("Dest. MAC: {0}, dest. port: {1}, VLAN: {2}, age: {3}".format(mac, self.network_objects['switch'][com_stack[2]][0].mac_table[mac][0],
                                                                                                self.network_objects['switch'][com_stack[2]][0].mac_table[mac][2],
                                                                                                self.network_objects['switch'][com_stack[2]][0].mac_table[mac][1]))
                        print("=" * 10)
                        print("Total sent/received:")
                        print("Total sent: {0}, total received: {1}".format(self.network_objects['switch'][com_stack[2]][0].total_sent,
                                                                            self.network_objects['switch'][com_stack[2]][0].total_received))
                    else:
                        print("Specify a switch name")
                        continue
                # Show details for a specific PC
                elif com_stack[1] == 'pc':
                    if len(self.network_objects['pc']) == 0:
                        print("You don't have any workstations")
                        continue
                    if len(com_stack) < 3:
                        print("Specify a PC name for an existing PC")
                        continue
                    if self.network_objects['pc'][com_stack[2]]:
                        print("PC stats:")
                        print("PC name: {0}, MAC address: {1}".format(com_stack[2], self.network_objects['pc'][com_stack[2]][0].mac))
                        print("Frames sent: {0}, frames received: {1}".format(self.network_objects['pc'][com_stack[2]][0].get_sent_for_port(0),
                                                                              self.network_objects['pc'][com_stack[2]][0].get_received_for_port(0)))
                    else:
                        print("PC with this name doesn't exist")
                        continue
                else:
                    print("Unrecognized command")
                    continue

            # Creating VLANs on a switch
            elif com_stack[0] == 'switch':
                if len(com_stack) < 2:
                    print("Command is not full")
                    continue
                if com_stack[1] == 'vlan':
                    vlan = input("Specify a VLAN number (int number): ")
                    ports_for_vlan = False
                    while True:
                        assign_ports = input("Assign ports to this VLAN? (y or n): ")
                        if assign_ports == 'y':
                            ports_for_vlan = input("Which port numbers to assign to this VLAN? (e.g., 1,10,3,6 no spaces): ").split(',')
                            break
                        elif assign_ports == 'n':
                            break
                        else:
                            print("Please, type y or n")
                            continue
                    sw_name = input("Provide a switch name: ")
                    if self.network_objects['switch'][sw_name]:
                        self.network_objects['switch'][sw_name][0].create_vlan(vlan)
                        if ports_for_vlan:
                            self.network_objects['switch'][sw_name][0].assign_ports_to_vlan(vlan, ports_for_vlan)
                    else:
                        print("This switch doesn't exist")
                        continue
                elif com_stack[1] == 'assign':
                    sw_name = input("Specify switch name: ")
                    vlan = input("Specify VLAN number: ")
                    ports_for_vlan = input("Which port numbers to assign to this VLAN? (e.g., 1,10,3,6 no spaces): ").split(',')
                    if self.network_objects['switch'][sw_name]:
                        self.network_objects['switch'][sw_name][0].assign_ports_to_vlan(vlan, ports_for_vlan)
                    else:
                        print("This switch doesn't exist")
                        continue
                else:
                    print("Unrecognized command")
                    continue

            # Sending frames between two PCs
            elif com_stack[0] == 'send':
                if len(self.network_objects['switch']) == 0:
                    print("You haven't created any switches yet")
                    continue
                from_pc = input("Where to send a frame FROM? (PC name): ")
                to_pc = input("Where to send a frame TO? (PC name): ")
                from_mac = self.network_objects['pc'][from_pc][0].mac
                to_mac = self.network_objects['pc'][to_pc][0].mac
                number_of_frames = int(input("How many frames? (int number): "))
                for n in range(number_of_frames):
                    print("Sending a frame: {0}:{1} ---> {2}:{3} ".format(from_pc, from_mac, to_pc, to_mac))
                    self.network_objects['pc'][from_pc][0].send_msg(to_mac)
                    self.network_objects['pc'][to_pc][0].receive_msg()

            # 'quit' command, leaving CLI
            elif com_stack[0] == 'quit':
                break

            # Invalid command
            else:
                print("Unrecognized command")
                continue




# Run simulation

if __name__ == "__main__":

    print("Starting simulator ...")

    session = RuntimeEnv()
    print("Session created")

    print("Shell started\n")
    session.shell()

    exit(0)































