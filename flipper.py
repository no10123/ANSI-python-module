import serial.tools.list_ports

def find_flipper():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # debug info
        print(f"Checking: {port.device} | Description: {port.description} | VID: {port.vid} | PID: {port.pid}")
        
        # hardwere id
        if port.vid == 0x0483 and port.pid == 0x5740:
            return port.device
            
        # Fallback
        if port.description and "Flipper" in port.description:
            return port.device
            
    return None

port = find_flipper()
if port:
    print(f"\n- success - target Flipper found on: {port}")
else:
    print("\n- Flipper not detected\nTry plugging it in.")