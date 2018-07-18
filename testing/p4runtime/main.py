#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))

import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

#import modules
import writeRules
import debug

SWITCH_COUNT = 1

def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    # always needs to be done
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for each switch present in the system.
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        switches = []

        #make a list of switches
        for i in range(SWITCH_COUNT):
        	sName = "s" + str(i+1)
        	sAddress = '127.0.0.1:5005' + str(i+1)
        	sDevice_id=i
        	sProto_dump_file='logs/s'+str(i+1)+'-p4runtime-requests.txt'
        	sW = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        		name=sName,
        		address=sAddress,
        		device_id=sDevice_id,
        		proto_dump_file=sProto_dump_file)
        	switches.append(sW)
        

        for switch in switches:
        	print switch
        	# Send master arbitration update message to establish this controller as
        	# master (required by P4Runtime before performing any other write operation)
        	switch.MasterArbitrationUpdate()

        count = 1
        for switch in switches:
        	# Install the P4 program on the switches
        	switch.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        	print "Installed P4 Program using SetForwardingPipelineConfig on switch" + str(count)
        	count = count + 1

        

        # Write the rules that tunnel traffic from h1 to h2
        writeRules.writeForwarding(p4info_helper, sw=switches[0], port=2,
                         dst_eth_addr="00:00:00:00:01:02", dst_ip_addr="10.0.1.2")

        # Write the rules that tunnel traffic from h2 to h1
        writeRules.writeForwarding(p4info_helper, sw=switches[0], port=1,
                         dst_eth_addr="00:00:00:00:01:01", dst_ip_addr="10.0.1.1")

        # TODO Uncomment the following two lines to read table entries from s1 and s2
        debug.readTableRules(p4info_helper, switches[0])
        

    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        debug.printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/p4program.p4info')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/p4program.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
