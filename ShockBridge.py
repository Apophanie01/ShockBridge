
import openvr
import time
import requests
import sys
from datetime import datetime, timedelta

#no paranthashies on mask!, default is for index right thumbstick press, replace  if sy need.
BUTTON_MASK = 4294967296 
OPENSHOCK_TOKEN = ""
SHOCKER_ID = ""
COOLDOWN_SECONDS = 1.0

API_URL = "https://api.openshock.app/2/shockers/control"


ASCII_ART_LINES = [
    "                                 ",
    "                                            ",
    "                                  █         ",
    "                                ████        ",
    "                               █████        ",
    "                             ███████        ",
    "                            ████████        ",
    "                           █████████        ",
    "                         ██████████         ",
    "                        ██████████          ",
    "                █████  ███████████       ██ ",
    "           ██████████████████████     █████ ",
    "        ██████       ███████████    ██████  ",
    "      █████         ███████████  ████████   ",
    "     ████          ██████████████████████   ",
    "   ████           ██████████ ██████████     ",
    "   ███            ████████ ███████████      ",
    "  ███            ████████ ██████████        ",
    "  ███           ███████ ████████████        ",
    "  ███           ██████ ██████████ ██        ",
    "  ███          █████ ███████████ ███ ██████ ",
    "  ███          ████ ██████████ ███████████  ",
    "  ████        ████ ███████ █████████████    ",
    "   ████       ███ █████ █████████████       ",
    "    ████      ██ ███ █████████████          ",
    "     █████   ██ ██ █████████████            ",
    "       █████ █  ██████████████              ",
    "         ████ ██████████████                ",
    "              ██████████                    ",
    "                                            ",
    "                                            ",
]

class SteamVROpenShockBridge:
    def __init__(self):
        print("\n".join(ASCII_ART_LINES))
        intensity = self._get_intensity_input()
        duration_ms = self._get_duration_input_seconds()
        print(f"\nConfiguration set: Intensity {intensity}%, Duration {duration_ms}ms")
        print("[=== BRIDGE IS NOW RUNNING ===]\nHappy Shocking!")

        self.last_shock_time = datetime.min
        self.was_pressed = False
        self.vr_system = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SteamVR-OpenShock/v2.3",
            "Open-Shock-Token": OPENSHOCK_TOKEN,
            "Content-Type": "application/json"
        })
        self.thumbstick_mask = BUTTON_MASK
        self.payload = {
            "shocks": [{
                "id": SHOCKER_ID,
                "type": "Shock",
                "intensity": intensity,
                "duration": duration_ms
            }],
            "body": {}
        }

    def _get_intensity_input(self):
        while True:
            value = int(input("Enter Intensity (1-100): "))
            if 1 <= value <= 100:
                return value
            else:
                print("A Valid Number PLease!")

    def _get_duration_input_seconds(self):
        min_sec = 0.3
        max_sec = 65.535
        while True:
            value_sec = float(input(f"Enter Duration (0.3-65.5) seconds): "))
            value_ms = int(value_sec * 1000)
            if 300 <= value_ms <= 65535:
                return value_ms
            else:
                print("A Valid Number PLease!")

    def trigger_shock(self):
        if datetime.now() - self.last_shock_time < timedelta(seconds=COOLDOWN_SECONDS):
            return
        try:
            response = self.session.post(API_URL, json=self.payload, timeout=2)
            if response.status_code == 200:
                self.last_shock_time = datetime.now()
            else:
                sys.stderr.write(f"OpenShock API Error: {response.status_code} - {response.text}\n")
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"OpenShock Connection Error: {e}\n")

    def run(self):
        try:
            self.vr_system = openvr.init(openvr.VRApplication_Background)
        except openvr.OpenVRError as e:
            sys.stderr.write(f"SteamVR Error: {e}\n")
            return

        try:
            while True:
                for idx in range(openvr.k_unMaxTrackedDeviceCount):
                    if self.vr_system.getTrackedDeviceClass(idx) != openvr.TrackedDeviceClass_Controller:
                        continue
                    result, state = self.vr_system.getControllerState(idx)
                    if result and state.ulButtonPressed & self.thumbstick_mask:
                        self.trigger_shock()
                time.sleep(0.016)
        except KeyboardInterrupt:
            pass
        finally:
            if self.vr_system:
                openvr.shutdown()

if __name__ == "__main__":
    try:
        bridge = SteamVROpenShockBridge()
        bridge.run()
    except Exception as e:
        sys.stderr.write(f"Shit's fucked, GL.. {e}\n")