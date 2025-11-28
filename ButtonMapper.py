import openvr
import time

print("Listening...") 
openvr.init(openvr.VRApplication_Background)
vr = openvr.VRSystem()

while True:
    for idx in range(openvr.k_unMaxTrackedDeviceCount):
        if vr.getTrackedDeviceClass(idx) != openvr.TrackedDeviceClass_Controller:
            continue
        result, state = vr.getControllerState(idx)
        if result and state.ulButtonPressed:
            print(f"Controller {idx} Value: {state.ulButtonPressed}")
    time.sleep(0.05)
