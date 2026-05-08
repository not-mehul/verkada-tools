import json
import sys

import requests


def check_org_exists(org_name):
    """
    Sends a POST request to Verkada's API to check if an org_name resolves to a valid shard.
    """
    url = f"https://vglobal.global-prod.verkada.com/__v/{org_name}/org/validate_short_name"

    # We dynamically update the origin and referer headers to match the target org
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": f"https://{org_name}.command.verkada.com",
    }

    payload = {"orgShortName": org_name}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        # If we get a 401/403, the endpoint might require auth or we've been rate limited.
        if response.status_code in [401, 403]:
            print(
                f"[!] Access Denied ({response.status_code}). Endpoint may no longer allow unauthenticated requests."
            )
            return None

        response.raise_for_status()
        data = response.json()

        # An invalid org returns {"name": null, "shard": null}
        # A valid org returns {"name": "mehul", "shard": {...}}
        if data.get("name") is not None:
            return data
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(f"[!] HTTP Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("[!] Failed to parse JSON response from server.")
        return None


def main():
    print("[*] Verkada Org Checker Interactive Mode")
    print("[*] Type 'quit' or press Ctrl+C to exit.")

    while True:
        try:
            org_input = input("\nEnter org short name to check: ").strip()

            if not org_input:
                continue

            if org_input.lower() in ["q", "quit", "exit"]:
                print("[*] Exiting...")
                break

            print(f"[*] Checking '{org_input}'...")
            result = check_org_exists(org_input)

            if result is False:
                print(f"[-] Org '{org_input}' does NOT exist.")
            elif result is not None:
                print(f"[+] SUCCESS! Org '{org_input}' exists!")
                print("Details returned by server:")
                print(json.dumps(result, indent=4))
            else:
                print("[-] Check failed due to an error.")

        except KeyboardInterrupt:
            print("\n\n[*] Script stopped by user. Exiting...")
            sys.exit(0)


if __name__ == "__main__":
    main()
