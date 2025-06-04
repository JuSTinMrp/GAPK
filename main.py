#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import re

CONFIG_FILE = "config.json"
DOCKER_IMAGE = "ghcr.io/efforg/apkeep:stable"

# Change output directory to "Downloads" folder next to main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "Downloads")


def save_config(email, aas_token):
    config = {"email": email, "aas_token": aas_token}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print("[✓] Configuration saved to", CONFIG_FILE)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("[!] Config file not found. Run `./main.py configure` first.")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def configure():
    print("---- CONFIGURE ----")
    email = input("Enter your email: ").strip()
    aas_token = input("Enter your AAS token: ").strip()
    save_config(email, aas_token)


def generate_aas_token():
    print("---- GENERATE AAS TOKEN (via Docker) ----")
    email = input("Enter your email: ").strip()
    oauth_token = input("Enter your OAuth token: ").strip()

    command = [
        "sudo", "docker", "run", "--rm", "-it",
        DOCKER_IMAGE,
        "-e", email,
        "--oauth-token", oauth_token
    ]

    print("\n[Running Docker to generate AAS token…]\n")
    subprocess.run(command)


def extract_app_id(url_or_id):
    """
    If the user supplied a full Play Store link, extract the "id=<package_name>".
    Otherwise assume they've given a raw package name.
    """
    if re.match(r'^(http|https)://', url_or_id):
        match = re.search(r"id=([\w\.]+)", url_or_id)
        if match:
            return match.group(1)
        else:
            print("[!] Could not extract an application ID from that URL.")
            sys.exit(1)
    return url_or_id


def download_apk():
    print("---- DOWNLOAD APK ----")
    config = load_config()

    app_input = input("Enter Play Store URL or application ID (e.g. com.facebook.katana): ").strip()
    app_id = extract_app_id(app_input)

    # Ensure "Downloads" directory exists next to main.py:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    command = [
        "sudo", "docker", "run", "--rm",
        "-v", f"{OUTPUT_DIR}:/output",
        DOCKER_IMAGE,
        "-a", app_id,
        "-d", "google-play",
        "-e", config["email"],
        "-t", config["aas_token"],
        "/output"
    ]

    print(f"\n[Downloading APK for {app_id} to {OUTPUT_DIR} …]\n")
    subprocess.run(command)
    print("\n[Done]")


def main():
    ascii_banner = r"""
  ___   _   ___ _  __  _____         _ 
 / __| /_\ | _ \ |/ / |_   _|__  ___| |
| (_ |/ _ \|  _/ ' <    | |/ _ \/ _ \ |
 \___/_/ \_\_| |_|\_\   |_|\___/\___/_|
                                             
    """

    parser = argparse.ArgumentParser(
        description=f"{ascii_banner}\n"
                    "\n"
                    "Available subcommands:\n"
                    "  configure     Prompt to set email and AAS token\n"
                    "  generate      Prompt for OAuth token and generate AAS token\n"
                    "  download      Prompt for Play Store URL or app ID, then download\n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="sub-command to run")

    subparsers.add_parser(
        "configure",
        help="Prompt to set email and AAS token (one‑time)"
    )
    subparsers.add_parser(
        "generate",
        help="Prompt for OAuth token and generate AAS token via Docker"
    )
    subparsers.add_parser(
        "download",
        help="Prompt for Play Store URL or app ID, then download via Docker"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "configure":
        configure()
    elif args.command == "generate":
        generate_aas_token()
    elif args.command == "download":
        download_apk()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
