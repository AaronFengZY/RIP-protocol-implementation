"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import RoutePacket, \
                     Table, TableEntry, \
                     DVRouterBase, Ports, \
                     FOREVER, INFINITY


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # Dead entries should time out after this interval
    GARBAGE_TTL = 10

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (self.SPLIT_HORIZON and self.POISON_REVERSE), \
                    "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."
        self.table[host] = TableEntry(dst=host, port=port, latency=self.ports.get_latency(port), expire_time=FOREVER)
        #self.send_routes(force=False)


    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """

        if packet.dst not in self.table: return

        export = self.table[packet.dst]
        
        if export.latency >= INFINITY: return
        # we can judge the destination by the rules above
        self.send(packet, export.port) 

    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        # This code is used for sharing the routing table
        for port in self.ports.get_all_ports():
            for host, entry in self.table.items():
                latency_now = entry.latency if not self.POISON_REVERSE or entry.port!=port else INFINITY
                if not self.SPLIT_HORIZON or port!=entry.port:
                    self.send_route(port=port, dst=host, latency=latency_now)

    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        renew_table = Table()

        for host, entry in self.table.items():
            if entry.expire_time > api.current_time():
                renew_table[u] = v
            elif self.POISON_EXPIRED and v.latency<INFINITY:
                renew_table[u] = TableEntry(dst=v.dst, port=v.port, latency=INFINITY, expire_time=api.current_time()+self.ROUTE_TTL)

        self.table = renew_table

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        if route_latency == INFINITY:
            if route_dst in self.table and self.table[route_dst].port == port:
                x = self.table[route_dst]
                self.table[route_dst] = TableEntry(dst = route_dst, port=port, latency=INFINITY,expire_time=self.ROUTE_TTL + api.current_time()
                                        if x.latency < INFINITY else x.expire_time)
        else:
            latency_sum = route_latency + self.ports.get_latency(port)
            if (route_dst not in self.table) or (latency_sum < self.table[route_dst].latency) or (port == self.table[route_dst].port):
                self.table[route_dst] = TableEntry(dst = route_dst, port=port, latency=latency_sum, expire_time=self.ROUTE_TTL + 
                                                                api.current_time())
        # call api_current_time to get the current time in seconds
        
        self.send_routes(force=False)

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        # TODO: fill in the rest!

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router does down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        # TODO: fill this in!

    # Feel free to add any helper methods!
