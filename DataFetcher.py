import ctypes
import psutil
import platform
import subprocess
import time
import os
import collections
from ctypes import wintypes

# windows api
PDH_FMT_DOUBLE = 0x00000200
PDH_INVALID_HANDLE = 0xC0000BC0

class PDH_API:
    """PDH.dll for system stats, so you can see if you have a SSS+ trir cpu"""
    def __init__(self):
        self.pdh = ctypes.windll.pdh
        self.query = wintypes.HANDLE()
        self.pdh.PdhOpenQueryW(None, 0, ctypes.byref(self.query))
        self.counters = {}

    def add_counter(self, path):
        counter = wintypes.HANDLE()
        self.pdh.PdhAddEnglishCounterW(self.query, path, 0, ctypes.byref(counter))
        self.counters[path] = counter
        return counter

    def get_value(self, path):
        self.pdh.PdhCollectQueryData(self.query)
        value = (ctypes.c_ulonglong * 2)() # placeholder
        self.pdh.PdhGetFormattedCounterValue(self.counters[path], PDH_FMT_DOUBLE, None, ctypes.byref(value))
        return float(ctypes.cast(ctypes.byref(value, 8), ctypes.POINTER(ctypes.c_double)).contents.value)

# init PDH
pdh = PDH_API()
# counters
cpu_counter = pdh.add_counter(r"\Processor(_Total)\% Processor Time")
disk_io_counter = pdh.add_counter(r"\LogicalDisk(_Total)\% Disk Time")

def get_cpu_load():
    """returns % CPU usage."""
    return pdh.get_value(r"\Processor(_Total)\% Processor Time")

def get_disk_io():
    """returns % Disk time usage."""
    return pdh.get_value(r"\LogicalDisk(_Total)\% Disk Time")

# memory via kernel32 
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_memory():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return {
        "total": stat.ullTotalPhys,
        "used": stat.ullTotalPhys - stat.ullAvailPhys,
        "avail": stat.ullAvailPhys,
        "page_total": stat.ullTotalPageFile,
        "page_used": stat.ullTotalPageFile - stat.ullAvailPageFile
    }

def get_cpu_ghz():
    freq = ctypes.windll.kernel32.GetSystemTimes
    # clock time for rms
    # or WMI via COM/OLE. 
    return 3.2 # placeholder

# system names
def get_system_names():
    """
    Fetches OS, CPU, and GPU names.
    note: call once on init
    """
    os_name = f"{platform.system()} {platform.release()}"
    cpu_name = platform.processor()
    gpu_name = "Unknown"

    # wmic
    try:
        output = subprocess.check_output(
            'wmic path win32_VideoController get name /value', 
            shell=True, text=True, stderr=subprocess.DEVNULL
        )
        for line in output.split('\n'):
            if '=' in line:
                gpu_name = line.split('=')[1].strip()
                break
    except subprocess.CalledProcessError:
        pass

    return os_name, cpu_name, gpu_name

# disks
# along with a fancy IO% system
last_disk_io = psutil.disk_io_counters(perdisk=True)
last_disk_time = time.time()

def get_disks():
    """Gets Free, Used, Total, and IO%"""
    global last_disk_io, last_disk_time
    
    current_io = psutil.disk_io_counters(perdisk=True)
    current_time = time.time()
    time_delta = current_time - last_disk_time

    disks = []
    for part in psutil.disk_partitions(all=False):
        # skips empty CD-ROM drives on Windows
        if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
            continue
            
        try:
            usage = psutil.disk_usage(part.mountpoint)
            
            # drive letter maping
            drive_name = part.device.replace('\\', '')
            disk_key = drive_name.replace(':', '')
            
            # Find the matching IO counter
            io_now = None
            io_old = None
            for key in current_io.keys():
                if disk_key in key or key in disk_key:
                    io_now = current_io[key]
                    io_old = last_disk_io.get(key)
                    break

            # Calculate IO %
            io_percent = 0.0
            if io_now and io_old and time_delta > 0:
                time_spent_ms = (io_now.read_time - io_old.read_time) + (io_now.write_time - io_old.write_time)
                max_possible_ms = time_delta * 1000
                if max_possible_ms > 0:
                    io_percent = min(100.0, (time_spent_ms / max_possible_ms) * 100)

            disks.append({
                "name": drive_name,
                "free": usage.free,
                "used": usage.used,
                "total": usage.total,
                "io_percent": round(io_percent, 2)
            })
        except PermissionError:
            continue

    # Save for next tick
    last_disk_io = current_io
    last_disk_time = current_time
    return disks

# network
def get_network():
    """gets network info"""
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    interfaces = []
    for name, stat in stats.items():
        name_lower = name.lower()
        
        # sorts the data
        if "wi-fi" in name_lower or "wireless" in name_lower or "wlan" in name_lower:
            if_type = "wifi"
        elif "loopback" in name_lower:
            if_type = "loopback"
        elif "ethernet" in name_lower:
            if_type = "ethernet"
        else:
            if_type = "unknown"

        interfaces.append({
            "name": name,
            "type": if_type,
            "sync": stat.isup, # is it running
            "auto": True,      # should work
            "zero": not stat.isup or name not in addrs # Disconnected or no IP assigned
        })
        
    return interfaces

# proccesses
def get_processes(filter_str="", reverse=False, tree=False):
    """gets processes, filters / sorts by RAM, and builds a tree."""
    procs = []
    
    for p in psutil.process_iter(['pid', 'ppid', 'name', 'memory_info']):
        try:
            info = p.info
            name = info['name'] or "Unknown"
            
            # Filter
            if filter_str.lower() in name.lower():
                mem_bytes = info['memory_info'].rss if info['memory_info'] else 0
                
                procs.append({
                    "name": name,
                    "pid": info['pid'],
                    "ppid": info['ppid'],
                    "mem_bytes": mem_bytes,
                    "children": [] # tree stuff
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass # deid or no have admin

    # sort based on memory (high -> low)
    procs.sort(key=lambda x: x["mem_bytes"], reverse=not reverse)

    # create the tree
    if tree:
        tree_procs = []
        # dict for PID lookups
        lookup = {p["pid"]: p for p in procs}
        
        for p in procs:
            if p["ppid"] in lookup and p["ppid"] != p["pid"]:
                lookup[p["ppid"]]["children"].append(p)
            else:
                tree_procs.append(p)
        return tree_procs

    return procs

def get_per_core_load():
    """
    Returns a list of %'s for each core.
    """
    return psutil.cpu_percent(interval=None, percpu=True)

def get_cpu_info():
    cpu_name = "Unknown"
    try:
        output = subprocess.check_output('wmic cpu get name', shell=True, text=True, stderr=subprocess.DEVNULL)
        lines = output.strip().split('\n')
        if len(lines) > 1:
            cpu_name = lines[1].strip()
    except:
        pass
    freq = psutil.cpu_freq()
    current_ghz = freq.current / 1000 if freq else 0.0
    return cpu_name, current_ghz

load_history = collections.deque(maxlen=900)

def update_load_history(current_load):
    load_history.append(current_load)

def get_load_averages():
    """60, 300, and 900 avrage of samples"""
    if len(load_history) == 0:
        return 0.0, 0.0, 0.0
    
    def get_avg(samples):
        subset = list(load_history)[-samples:]
        return round(sum(subset) / len(subset), 2)

    return get_avg(60), get_avg(300), get_avg(900)