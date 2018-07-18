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

def yieldSwitches(p4info_helper, bmv2_file_path, count):
	switches = []
 	#make a list of switches
 	for i in range(count):
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
	return switches

def forwardingPipeline(p4info_helper, bmv2_file_path, switches):
	count = 1
	for switch in switches:
		switch.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                   bmv2_json_file_path=bmv2_file_path)
		print "Installed P4 Program using SetForwardingPipelineConfig on switch" + str(count)
    	count = count + 1

	