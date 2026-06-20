import serial.tools.list_ports
import serial
import time
import sys
import shutil

port = None

def divider(char="-"):
    terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    print(char * terminal_width)

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

def start():
    port = find_flipper()
    if port:
        print(f"\n- success - target Flipper found on: {port}")
    else:
        print("\n- Flipper not detected\nTry plugging it in.")

def landingPage():
    try:
        with serial.Serial(port, baudrate=115200, timeout=1) as flipper:
            #clears cmd's
            flipper.write(b'\r\n\r\n')
            time.sleep(0.2)
            flipper.read_all()
            
            print("Loading... (1/2)")
            flipper.write(b'info\r\n')
            time.sleep(0.5)
            raw_info = flipper.read_all().decode('utf-8', errors='ignore')
            
            print("Loading... (2/2)")
            flipper.write(b'storage info /ext\r\n')
            time.sleep(0.5)
            raw_storage = flipper.read_all().decode('utf-8', errors='ignore')

            return raw_info, raw_storage
    except serial.SerialException as e:
        print(f"connection failed: {e}")
        return None, None

def cli(port):
    try:
        with serial.Serial(port, baudrate=115200, timeout=0.1) as flipper:
            flipper.write(b'\r\n\r\n')
            time.sleep(0.2)
            flipper.read_all() 
            
            print(f"--- connected to Flipper Zero on {port} ---\n")
            flipper.write(f"{'neofetch'}\r\n".encode('utf-8'))
            response = ""
            while True:
                chunk = flipper.read(256).decode('utf-8', errors='ignore')
                response += chunk
                if ">:" in response:
                    break
                if not chunk:
                    time.sleep(0.01)
            print('\n'.join(response.replace(">:", "").strip().split('\n')[1:]) + '\n')
            divider()
            while True:
                user_cmd = input("Flipper> ")

                if user_cmd.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break

                #if user_cmd.lower() in ["w","a","s","d","q","e"]:
                #    exec(["p.up()","p.left()","p.down()","p.right()","p.back()","p.ok()",][["w","a","s","d","q","e"].index(user_cmd.lower())])
                
                if not user_cmd.strip():
                    continue

                # send to flipper
                flipper.write(f"{user_cmd}\r\n".encode('utf-8'))

                # get reponce
                response = ""
                while True:
                    chunk = flipper.read(256).decode('utf-8', errors='ignore')
                    response += chunk
                    
                    if ">:" in response:
                        break
                    if not chunk:
                        time.sleep(0.01)
                
                print('\n'.join(response.replace(">:", "").strip().split('\n')[1:]) + '\n')

    except serial.SerialException as e:
        print(f"\nConnection failed: {e}")
    except KeyboardInterrupt:
        # Handles the user hitting Ctrl+C
        print("\n\nquiting CLI...")
        sys.exit(0)

def cmd_btn(flipper, button_name):
    flipper.write(f"input send {button_name} short\r\n".encode('utf-8'))
    time.sleep(0.05) 
    flipper.read_all()

class press:
    def up(self):
        cmd_btn(serial.Serial(port, baudrate=115200, timeout=0.1), "up")
    def right(self):
        cmd_btn(serial.Serial(port, baudrate=115200, timeout=0.1), "right")
    def down(self):
        cmd_btn(serial.Serial(port, baudrate=115200, timeout=0.1), "down")
    def left(self):
        cmd_btn(serial.Serial(port, baudrate=115200, timeout=0.1), "left")
    def ok(self):
        cmd_btn(serial.Serial(port, baudrate=115200, timeout=0.1), "ok")
    def back(self):
        cmd_btn(serial.Serial(port, baudrate=115200, timeout=0.1), "back")

p = press()

def seeRaw():
    system_data, storage_data = landingPage()
    if system_data:
        print("\n--- raw (1/2) ---")
        print(system_data)
    
        print("\n--- raw (2/2) ---")
        print(storage_data)