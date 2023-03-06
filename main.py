"""
Accessibility Notifier App.
Checks the accessibility of given websites.
"""

import csv
import os
import subprocess
import sys
import requests
import socket
from datetime import datetime


class AccessibilityNotifier:
    """
    AccessibilityNotifier app class.
    Checks the accessibility of websites given in file.

    To start checking websites, call a run() method of an instance of the class
    """

    unknown_host_name = '???'
    unknown_ip = '???'
    unknown_port = '-1'
    unknown_status = '???'
    port_open = "Opened"
    timeout = 2

    input_csv_file_name = "input"
    name = "Accessibility Notifier"

    def __init__(self):
        print(end="\n\n\n")
        print("-" * 40)
        print(f"{self.name:^40}")
        print("-" * 40, end="\n\n")
        print(f"Looking for CSV file \"{self.input_csv_file_name}\"... ")

        self.lines = self.open_csv_file()

        # disabling proxy to be able to connect to localhost
        os.environ['NO_PROXY'] = '127.0.0.1'

    def run(self):
        """
        Start checking accessibility of websites given in input file
        """

        print("Checking websites...\n")

        while True:
            print("-" * 40, end="\n\n")
            try:
                for line in self.lines[1:]:
                    # check validity
                    if line and line[0]:
                        if len(line) == 1:
                            ports = []
                        else:
                            ports = self.get_valid_ports(line[1].split(","))
                        target = line[0]
                    else:
                        continue
                    try:
                        target_is_ip = self.is_ip(target)
                    except socket.gaierror:
                        print(f"Error. Maybe caused by invalid input: {line}")
                        continue

                    # check if target is an ip or host name
                    if not target_is_ip:
                        ips = self.get_valid_ips(
                            self.get_ips_by_dns_lookup(target))
                        print([target, ips, ports])
                    else:
                        ips = [target]
                        print([self.unknown_host_name, ips, ports])

                    if target_is_ip and ports:
                        # target is an ip address and ports are provided
                        # check ip address on all ports
                        for port in ports:
                            print(self.check_ip(target,
                                                port,
                                                self.unknown_status))
                    elif target_is_ip:
                        # target is an ip address
                        # check ip address
                        print(self.ping_ip(target, self.unknown_status))
                    elif target and ports:
                        # target is a host name and ports are provided
                        # show error msg if error
                        for port in ports:
                            for ip in ips:
                                print(self.check_ip(ip, port, target))
                    elif target:
                        # target is a host name
                        # show error msg if error
                        for ip in ips:
                            print(self.ping_ip(ip, target=target))
                            # print(self.check_ip(ip, target=target))
                    else:
                        # invalid input data
                        sys.exit(f"Invalid input: {line}")
                    print()
            except KeyboardInterrupt:
                print("Keyboard Interrupt. Exiting...")
                break
            except requests.exceptions.ReadTimeout:
                print("Read timeout...")
            except socket.gaierror:
                print("Get address info failed.")

    def open_csv_file(self, file_name="input", delimiter=";"):
        """
        Opens CSV file and returns its lines.

        :param file_name: CSV file name in working directory.
        :param delimiter: CSV file delimiter.
        """

        try:
            with open(f"{file_name}.csv", "r") as file:
                print(
                    f"Reading CSV file using \"{delimiter}\" delimiter... \n")
                reader = csv.reader(file, delimiter=delimiter)
                return list(reader)
        except FileNotFoundError:
            return f"CSV file not found in working directory. \
                     It should be called \"{self.input_csv_file_name}\""

    def check_website(self, target, port="-1"):
        """ Gets information about target website using given port """

        try:
            request = self.get_request(target, port, timeout=self.timeout)
            ip = socket.gethostbyname(target)
            is_opened_port = self.scan_port(ip, int(port))
        except requests.exceptions.ConnectionError:
            return f"Connection to {target} with port {port} timed out."

        return f"{datetime.now()} | \
{target:^20} | \
{ip:^15} | \
{round(request.elapsed.total_seconds() * 1000, 2):^7} ms | \
{port:^4} | \
{self.port_open if is_opened_port else self.unknown_status}"

    def check_ip(self, ip, port="-1", target=None):
        """
        Gets information about target ip address using given port.

        :returns string with
        time, host name, ip address, road trip time, port, status.
        """

        try:
            request = self.get_request(ip, port, timeout=self.timeout)
            is_opened_port = self.scan_port(ip, int(port))
        except requests.exceptions.ConnectionError:
            return f"{datetime.now()} | \
{str(target):^20} | \
{ip:^15} | \
{str(self.timeout * 1000):^7} ms | \
{port:^4} | \
{self.unknown_status}"

        if target is not None:
            return f"{datetime.now()} | \
{target:^20} | \
{ip:^15} | \
{round(request.elapsed.total_seconds() * 1000, 2):^7} ms | \
{port:^4} | \
{self.port_open if is_opened_port else self.unknown_status}"

        return f"{datetime.now()} | \
{self.unknown_host_name:^20} | \
{ip:^15} | \
{round(request.elapsed.total_seconds() * 1000, 2):^7} ms | \
{port:^4} | \
{self.port_open if is_opened_port else self.unknown_status}"

    def ping_ip(self, ip, target=None):
        """
        Check accessibility of a host using ICMP protocol (ping).

        :returns string with
        time, host name, ip address, road trip time, port, status.
        """

        host_name, rtt = self.check_ping(ip)

        return f"{datetime.now()} | \
{target:^20} | \
{ip:^15} | \
{round(float(rtt), 2):^7} ms | \
{self.unknown_port:^4} | \
{self.unknown_status}"

    @staticmethod
    def scan_port(target, port):
        """
        Returns True if given port is open for target host name else False
        """

        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0.3)

        result = socket_connection.connect_ex((target, port))
        socket_connection.close()
        if result == 0:
            return True
        else:
            return False

    @staticmethod
    def check_ping(hostname):
        """
        Check accessibility of a host using ICMP protocol (ping).

        :returns tuple that contains host name and Road Trip Time.
        """

        try:
            response = subprocess.check_output("ping -n 1 " + hostname,
                                               shell=True).decode(
                "utf-8").split("\n")
        except subprocess.CalledProcessError:
            return f"Connection to {hostname} timed out."

        for i, line in enumerate(response):
            if line == "\r":
                response.remove(response[i])
            elif not line:
                response.remove(response[i])
            else:
                response[i] = response[i].lstrip(" ")

        return response[0][8:response[0].find(" ", 9)], response[-1][
                                                        response[-1].rfind(
                                                            " ") + 1:-3]

    @staticmethod
    def get_request(target, port="-1", timeout=2):
        """ Performs a GET request from target host using given port """

        if port == "443":
            request = requests.get(f"https://{target}", timeout=timeout)
        elif port == "-1":
            request = requests.get(f"http://{target}", timeout=timeout)
        else:
            request = requests.get(f"http://{target}:{port}", timeout=timeout)

        return request

    @staticmethod
    def get_ips_by_dns_lookup(target, port="443"):
        """
        Takes the passed target and optional port and does a dns lookup.
        It returns the ips that it finds to the caller.

        :param target:  the URI that you'd like to get the ip address(es) for.
        :param port:    the port you want to do the lookup on.
        """

        return list(map(lambda x: x[4][0],
                        socket.getaddrinfo('{}.'.format(target), port,
                                           type=socket.SOCK_STREAM)))

    @staticmethod
    def get_valid_ports(ports):
        """ Returns only valid ports using given ports """

        for port in ports:
            if not port.isdigit():
                ports.remove(port)
        return ports

    @staticmethod
    def get_valid_ips(ips):
        """ Returns only valid ips using given ips """

        for ip in ips:
            if len(ip) < 5:
                ips.remove(ip)
        return ips

    @staticmethod
    def is_ip(target):
        """ Checks if target is ip or not """

        if target == socket.gethostbyname(target):
            return True
        return False


if __name__ == "__main__":
    app = AccessibilityNotifier()
    app.run()
