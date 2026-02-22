#!/usr/bin/env python3
import subprocess
import sys
import os
import time

def setup_autostart():
    script_path = os.path.abspath(__file__)
    python_path = subprocess.run(["which", "python3"], capture_output=True, text=True).stdout.strip()
    service_content = f"""[Unit]
Description=Arch Linux Auto Updater
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStartPre=/bin/sleep 30
ExecStart={python_path} {script_path}
Restart=no

[Install]
WantedBy=default.target
"""
    service_dir = os.path.expanduser("~/.config/systemd/user/")
    os.makedirs(service_dir, exist_ok=True)
    with open(os.path.join(service_dir, "arch-autoupdater.service"), "w") as f:
        f.write(service_content)
    subprocess.run(["systemctl", "--user", "daemon-reload"])
    subprocess.run(["systemctl", "--user", "enable", "arch-autoupdater.service"])
    subprocess.run(["systemctl", "--user", "start", "arch-autoupdater.service"])
    print("✅ Setup complete!")

def download_updates():
    subprocess.run(["sudo", "pacman", "-Syuw", "--noconfirm"])

def ask_user():
    result = subprocess.run([
        "zenity", "--question",
        "--title=Arch Linux Updater",
        "--text=✅ Updates ready!\n\nInstall & Restart → installs and reboots\nNo Later → skips till next boot",
        "--ok-label=Install & Restart",
        "--cancel-label=No Later",
        "--width=440", "--height=170",
    ])
    return result.returncode == 0

def install_and_restart():
    os.system('notify-send "Arch Updater" "Installing... Please wait!"')
    subprocess.run(["sudo", "pacman", "-Su", "--noconfirm"])
    os.system('notify-send "Arch Updater" "Done! Restarting in 5 seconds..."')
    time.sleep(5)
    subprocess.run(["sudo", "reboot"])

def main():
    download_updates()
    os.system('notify-send "Arch Updater" "Updates ready!"')
    if ask_user():
        install_and_restart()
    else:
        os.system('notify-send "Arch Updater" "Skipped! See you next boot."')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_autostart()
    else:
        main()
