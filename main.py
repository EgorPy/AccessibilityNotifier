"""
Accessibility Notifier App.
Notifies you when some websites can't be reached for some reason.
"""

import csv
import time

import requests
import socket
from datetime import datetime


def get_request(target, port):
    """
    Gets information about target website using given port.
    """

    start_time = time.time()
    if port == "443":
        request = requests.get(f"https://{target}", timeout=2)
    elif port == "80":
        request = requests.get(f"http://{target}", timeout=2)
    else:
        return f"Unknown port: {port}"
    ip = socket.gethostbyname(target)
    response_time = time.time() - start_time
    status_code = request.status_code
    return f"{datetime.now()} | {target} | {ip} | 0.0 | {round(response_time * 1000, 2)} ms | {port} | {status_code}"


if __name__ == "__main__":
    print("Accessibility Notifier\n")
    print("Looking for CSV file \"input\"... ")
    try:
        with open("input.csv", "r") as file:
            print("Reading CSV file using \";\" delimiter... \n")
            reader = csv.reader(file, delimiter=";")
            next(reader)
            for i, line in enumerate(reader):
                try:
                    target = line[0]
                    ports = line[1].split(",")
                    ip = socket.gethostbyname(target)
                    print([target, ip, ports])
                    for port in ports:
                        print(get_request(target, port))
                    print()
                except BaseException as e:
                    print(f"Exception occurred: {e}")

    except FileNotFoundError:
        print("CSV file not found in working directory. It should be called \"input\"")
