# Accessibility Notifier App
## Checks the accessibility of given websites.

Can work 24/7.
Even if the network error or other error occurs.

---

## Running the program

To run the program, download the repository and run main.py file.
Code tested on Python 3.9.

This program will search for file named input.csv 
and will check the accessibility of the websites given in this file.

1. If only the domain name of the server is specified, the application resolves the domain name to one or more IP addresses and performs checks for each IP address
2. If an IP address is given, the application performs checks for this address
3. If the input data is incorrect, the application informs the user about it, but does not stop its work
4. If ports for checking are not specified, the application only checks the availability of the address using the ICMP protocol (ping)
5. If a port or several ports are specified, the application checks the openness of these ports
6. The report format for each server from the input data contains the value of RTT (round trip time) in ms (ms), port number (if specified) and port status (opened or unknown)

## Input
![input](https://user-images.githubusercontent.com/86737447/223112104-c9921981-c811-4c24-b861-6901932aa55e.png)
## Output
![AccessibilityNotifier](https://user-images.githubusercontent.com/86737447/223108188-299b2e98-6483-4858-8c0c-d6d2a0bab34f.png)

Used modules:
- csv
- os
- subprocess
- sys
- requests
- socket
- datetime
