import openvr
import time
import requests
import sys
import threading
import tkinter as tk
from datetime import datetime, timedelta

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
        
        self.intensity = 10
        self.duration_ms = 1000

        self.last_shock_time = datetime.min
        self.vr_system = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SteamVR-OpenShock/v2.3",
            "Open-Shock-Token": OPENSHOCK_TOKEN,
            "Content-Type": "application/json"
        })
        self.thumbstick_mask = BUTTON_MASK
        self.update_payload()

    def update_payload(self):
        self.payload = {
            "shocks": [{"id": SHOCKER_ID, "type": "Shock", "intensity": self.intensity, "duration": self.duration_ms}],
            "body": {}
        }

    def trigger_shock(self):
        if datetime.now() - self.last_shock_time < timedelta(seconds=COOLDOWN_SECONDS):
            return
        try:
            response = self.session.post(API_URL, json=self.payload, timeout=2)
            if response.status_code == 200:
                self.last_shock_time = datetime.now()
                print(f"Shock Sent: {self.intensity}% | {self.duration_ms}ms")
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
                    if self.vr_system.getTrackedDeviceClass(idx) != openvr.TrackedDeviceClass_Controller: continue
                    result, state = self.vr_system.getControllerState(idx)
                    if result and state.ulButtonPressed & self.thumbstick_mask:
                        self.trigger_shock()
                time.sleep(0.016)
        except KeyboardInterrupt:
            pass
        finally:
            if self.vr_system: openvr.shutdown()

def start_ui(bridge):
    root = tk.Tk()
    root.title("PainScale")
    root.geometry("900x600")
    
    
    for i in range(2): 
        root.columnconfigure(i, weight=1)
        root.rowconfigure(i, weight=1)

    
    lbl_int = tk.Label(root, text=f"{bridge.intensity}%", font=("Arial", 30, "bold"), bg="yellow")
    lbl_int.place(relx=0.25, rely=0.5, anchor="center")
    
    lbl_dur = tk.Label(root, text=f"{bridge.duration_ms}ms", font=("Arial", 30, "bold"), bg="yellow")
    lbl_dur.place(relx=0.75, rely=0.5, anchor="center")

    def update(d_int, d_dur):
        bridge.intensity = max(1, min(100, bridge.intensity + d_int))
        bridge.duration_ms = max(300, min(10000, bridge.duration_ms + d_dur))
        bridge.update_payload()
        lbl_int.config(text=f"{bridge.intensity}%")
        lbl_dur.config(text=f"{bridge.duration_ms}ms")

    
    tk.Button(root, bg="#7C43F0", command=lambda: update(5, 0)).grid(row=0, column=0, sticky="nsew")
    tk.Button(root, bg="#584F65", command=lambda: update(-5, 0)).grid(row=1, column=0, sticky="nsew")
    tk.Button(root, bg="#7C43F0", command=lambda: update(0, 1000)).grid(row=0, column=1, sticky="nsew")
    tk.Button(root, bg="#584F65", command=lambda: update(0, -1000)).grid(row=1, column=1, sticky="nsew")

    lbl_int.lift()
    lbl_dur.lift()
    root.mainloop()

if __name__ == "__main__":
    try:
        bridge = SteamVROpenShockBridge()
        threading.Thread(target=bridge.run, daemon=True).start()
        start_ui(bridge)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
