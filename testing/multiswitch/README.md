# Implementing a Control Plane using P4Runtime

## Introduction

In this exercise, we will be using P4Runtime to send flow entries to the 
switch instead of using the switch's CLI. We will be building on the same P4
program that is in the [basic_tunnel](../basic_tunnel) exercise. The
P4 program has been renamed to `p4program.p4`.

## Step 1: Run controller code

The code for this is in a file called `main.py`. In this system, the controller code is modularized amongst 4 different files.
This includes
- main.py
- setup.py
- writeRules.py
- debug.py

Let's first compile the new P4 program, start the network, use `main.py`
to install a few rules, and look at the console to see that things
are working as expected.

1. In your shell, run:
   ```bash
   make
   ```
   This will:
   * compile `p4program.p4`,
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`)
     configured in a triangle, each connected to one host (`h1`, `h2`, `h3`), and
   * assign IPs of `10.0.1.1`, `10.0.2.2`, `10.0.3.3` to the respective hosts.

2. You should now see a Mininet command prompt. Start a ping between h1 and h2:
   ```bash
   mininet> h1 ping h2
   ```
 
   
3. Open another shell and run the starter code:
   ```bash
   ./main.py
   ```
   This will install the `p4program.p4` program on the switches and push the
   tunnel ingress rules.

4. Press `Ctrl-C` to the second shell to stop `mycontroller.py`

Each switch is currently mapping traffic into tunnels based on the destination IP
address. 

### Potential Issues

If you see the following error message when running `mycontroller.py`, then
the gRPC server is not running on one or more switches.

```
p4@p4:~/tutorials/P4D2_2017_Fall/exercises/p4runtime$ ./mycontroller.py
...
grpc._channel._Rendezvous: <_Rendezvous of RPC that terminated with (StatusCode.UNAVAILABLE, Connect Failed)>
```

You can check to see which of gRPC ports are listening on the machine by running:
```bash
sudo netstat -lpnt
```

The easiest solution is to enter `Ctrl-D` or `exit` in the `mininet>` prompt,
and re-run `make`.

### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules
within each table are inserted by the control plane. In this case,
`main.py` implements our control plane, instead of installing static
table entries like we have in the previous exercises.

**Important:** A P4 program also defines the interface between the
switch pipeline and control plane. This interface is defined in the
`p4program.p4info` file. The table entries that you build in `main.py`
refer to specific tables, keys, and actions by name, and we use a P4Info helper
to convert the names into the IDs that are required for P4Runtime. Any changes
in the P4 program that add or rename tables, keys, or actions will need to be
reflected in your table entries.

- [P4Info](https://github.com/p4lang/PI/blob/master/proto/p4/config/p4info.proto)

#### Cleaning up Mininet

If the Mininet shell crashes, it may leave a Mininet instance
running in the background. Use the following command to clean up:
```bash
make clean
```

# TODO
This p4program is supposed to send packets without forwarding rules back to the controller by modifying the default action from drop().
This currently is not working :(

