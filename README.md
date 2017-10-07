# Interactive-Network-Switch-Simulator
While learning OOP in Python, I decided to build an interactive network switch simulator. It supports a simple CLI and basic functionalities of switches. 

Yes, I realize that this is not a fully-functional network
simulator. For now, it supports a single switch and a few PCs
connected to it.

I have tested it in my PyCharm and in my OS environment. And it works just fine.

To run this simulation, you can use the following commands for different scenarios
(quick command tutorial is provided under the input examples or you can issue command 'help'):

Getting help page:
-------------
help
quit


Creating a network switch SW_1 with 10 ports:
-------------
create switch
SW_1
10
show switch SW_1
quit


Creating a network switch SW_1 with 10 ports, creating VLAN 100 on that switch and assigning ports 0,1,2,3,4 to VLAN 100
------------
create switch
SW_1
10
switch vlan
100
y
0,1,2,3,4
SW_1
show switch SW_1
quit


Creating a network switch SW_1, VLAN 100, assigning ports 0,1,2,3,4 to VLAN 100, creating workstations PC_1 and PC_2
and connecting them to switch SW_1, and finally sending 5 frames from PC_1 to PC_2 and displaying corresponding statistics
--------------
create switch
SW_1
10
switch vlan
100
y
0,1,2,3,4
SW_1
create pc
PC_1
SW_1
0000.0000.0001
0
create pc
PC_2
SW_1
0000.0000.0002
3
send
PC_1
PC_2
5
show network
show switch SW_1
show pc PC_1
show pc PC_2
quit


Note: 0000.0000.0001 and 0000.0000.0002 are MAC adresses which are manually "configured" on workstations PC_1 and PC_2


To run this code in interactive mode, it's better to copy it in a .py file and run in a regular OS environment.
In interactive mode commands will prompt you to type in some parameters, such as device name, number of switch ports, MAC addresse, etc.


Below is a list of all supported commands. All commands will prompt you for some input.
It should be quite clear.
----------

'create switch' - this is where you start; this command will create a switch object for you.
Everything else is dependant on it

'create pc' - this command will create a workstation, which will be connected to your switch.
You have to manually specify MAC addresses

'show network' - briefly displays general statistics of your switch

'show switch <switch_name>' - displays more details about a state of your switch, e.g.
VLANs, ports, number of received frames, number of sent frames, etc.

'show pc <pc_name>' - similar command for your workstations

'switch vlan' - creates a vlan on your switch; optionally, allows you to assign ports to
the new VLAN

'switch assign' - assigns ports to an existing VLAN

'send' - allows you to manually send a frame from one workstation to another.
Then you can check reactions of all network devices using 'show' commands

'quit' - leave command line interface and stop the process


The same output can be displayed by issuing 'help' command.









