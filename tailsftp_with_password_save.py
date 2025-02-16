#!/usr/bin/env python3

import subprocess
import re
import os
import getpass
import keyring

SERVICE_NAME = 'tailscale_sftp'

def get_tailscale_status():
    result = subprocess.run(['tailscale', 'status'], stdout=subprocess.PIPE, text=True)
    return result.stdout

def parse_status_output(output):
    machines = []
    for line in output.splitlines():
        match = re.match(r'(\d+\.\d+\.\d+\.\d+)\s+(\S+)\s+\S+\s+(\S+)\s+(\S+)', line)
        if match and match.group(4) != 'offline':
            machines.append({
                'ip': match.group(1),
                'name': match.group(2),
                'os': match.group(3),
                'status': match.group(4)
            })
    return machines

def display_machines(machines):
    print(f"{'Index':<5} {'Name':<25} {'IP':<15} {'OS':<10}")
    print("=" * 60)
    for idx, machine in enumerate(machines):
        print(f"{idx:<5} {machine['name']:<25} {machine['ip']:<15} {machine['os']:<10}")

def get_saved_password(machine_name, username):
    return keyring.get_password(SERVICE_NAME, f"{machine_name}_{username}")

def save_password(machine_name, username, password):
    keyring.set_password(SERVICE_NAME, f"{machine_name}_{username}", password)

def main():
    # Get Tailscale status
    status_output = get_tailscale_status()
    machines = parse_status_output(status_output)

    if not machines:
        print("No online machines found.")
        return

    # Display the list of machines
    display_machines(machines)

    # Ask the user to select a machine
    while True:
        try:
            selection = int(input("\nEnter the index of the machine to connect to: "))
            if 0 <= selection < len(machines):
                selected_machine = machines[selection]
                break
            else:
                print("Invalid selection. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    machine_name = selected_machine['name']

    username = input(f"Enter SFTP username for {machine_name} (default: root): ").strip() or "root"

    saved_password = get_saved_password(machine_name, username)

    if saved_password:
        print(f"Using saved password for {username}@{machine_name}.")
        password = saved_password
    else:
        password = getpass.getpass(f"Enter SFTP password for {username}@{machine_name}: ")
        save_password_choice = input(f"Do you want to save this password for future use on {machine_name}? (y/N): ").strip().lower()
        if save_password_choice == 'y':
            save_password(machine_name, username, password)

    # Use an environment variable to securely pass the password
    os.environ['SSHPASS'] = password

    sftp_command = f"sshpass -e sftp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{selected_machine['ip']}"
    print(f"Running SFTP command: {sftp_command}")

    # Run the SFTP command
    os.system(sftp_command)

    del os.environ['SSHPASS']

if __name__ == '__main__':
    main()
