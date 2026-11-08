import ctypes
import psutil
import platform
import subprocess
import time
import os
import collections
from ctypes import wintypes
import winreg
import re
import socket

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
        try:
            self.pdh.PdhGetFormattedCounterValue(self.counters[path], PDH_FMT_DOUBLE, None, ctypes.byref(value))
            return float(ctypes.cast(ctypes.byref(value, 8), ctypes.POINTER(ctypes.c_double)).contents.value)
        except OSError:
            return 0.0

# init PDH
pdh = PDH_API()
# counters
cpu_counter = pdh.add_counter(r"\Processor(_Total)\% Processor Time")
disk_io_counter = pdh.add_counter(r"\LogicalDisk(_Total)\% Disk Time")
queue_counter = pdh.add_counter(r"\System\Processor Queue Length")

def format_bytes(bytes_value, force_unit=None):
    if force_unit == "PiB" or (force_unit is None and bytes_value >= 1024**5):
        return f"{bytes_value / (1024**5):.2f} PiB"
    elif force_unit == "TiB" or (force_unit is None and bytes_value >= 1024**4):
        return f"{bytes_value / (1024**4):.2f} TiB"
    elif force_unit == "GiB" or (force_unit is None and bytes_value >= 1024**3):
        return f"{bytes_value / (1024**3):.2f} GiB"
    elif force_unit == "MiB" or (force_unit is None and bytes_value >= 1024**2):
        return f"{bytes_value / (1024**2):.1f} MiB"
    elif force_unit == "KiB" or (force_unit is None and bytes_value >= 1024):
        return f"{bytes_value / 1024:.2f} KiB"
    else:
        return f"{int(bytes_value)} Byte"

def format_bits(bytes_value):
    bits = bytes_value * 8
    if bits >= 1024**3:
        return f"{bits / (1024**3):.2f} Gibps"
    elif bits >= 1024**2:
        return f"{bits / (1024**2):.2f} Mibps"
    elif bits >= 1024:
        return f"{bits / 1024:.1f} Kibps"
    else:
        return f"{int(bits)} bps"

def get_cpu_load():
    """returns % CPU usage."""
    return round(pdh.get_value(r"\Processor(_Total)\% Processor Time"),0)

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

class PERFORMANCE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("CommitTotal", ctypes.c_size_t),
        ("CommitLimit", ctypes.c_size_t),
        ("CommitPeak", ctypes.c_size_t),
        ("PhysicalTotal", ctypes.c_size_t),
        ("PhysicalAvailable", ctypes.c_size_t),
        ("SystemCache", ctypes.c_size_t),
        ("KernelTotal", ctypes.c_size_t),
        ("KernelPaged", ctypes.c_size_t),
        ("KernelNonpaged", ctypes.c_size_t),
        ("PageSize", ctypes.c_size_t),
        ("HandleCount", wintypes.DWORD),
        ("ProcessCount", wintypes.DWORD),
        ("ThreadCount", wintypes.DWORD),
    ]

def get_windows_perf_info():
    perf_info = PERFORMANCE_INFORMATION()
    perf_info.cb = ctypes.sizeof(PERFORMANCE_INFORMATION)
    try:
        ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(perf_info), perf_info.cb)
        return perf_info
    except Exception:
        return None

def get_memory():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    perf = get_windows_perf_info()
    page_size = perf.PageSize if perf else 4096
    cache = (perf.SystemCache * page_size) if perf else 0
    committed = (perf.CommitTotal * page_size) if perf else 0
    
    return {
        "total"     : format_bytes(stat.ullTotalPhys),
        "used"      : format_bytes(stat.ullTotalPhys - stat.ullAvailPhys),
        "avail"     : format_bytes(stat.ullAvailPhys),
        "cache"     : format_bytes(cache),
        "commi"     : format_bytes(committed),
        "page_total": format_bytes(stat.ullTotalPageFile),
        "page_used" : format_bytes(stat.ullTotalPageFile - stat.ullAvailPageFile)
    }

def get_cpu_ghz():
    try:
        freq = psutil.cpu_freq()
        return round(freq.current / 1000, 2) if freq else 0.0
    except (AttributeError, NotImplementedError):
        return 0.0

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
                read_bps = (io_now.read_bytes - io_old.read_bytes) / time_delta
                write_bps = (io_now.write_bytes - io_old.write_bytes) / time_delta
            else:
                read_bps = 0
                write_bps = 0
            
            disks.append({
                "name": drive_name[:-1],
                "free": format_bytes(usage.free),
                "used": format_bytes(usage.used),
                "total": format_bytes(usage.total),
                "io_percent": round(io_percent, 2),
                "read_speed": read_bps,
                "write_speed": write_bps
            })
        except PermissionError:
            continue

    # Save for next tick
    last_disk_io = current_io
    last_disk_time = current_time
    return disks

def get_disk_type(drive_letter):
    """SSD or HDD
    """
    try:
        cmd = f"Get-PhysicalDisk | Where-Object {{ $_.FriendlyName -match '(?i)SSD' -or $_.MediaType -eq 'SSD' }}"
        ps_cmd = f"(Get-PhysicalDisk | Where-Object {{ $_.DeviceId -eq (Get-Partition -DriveLetter {drive_letter} | Select -ExpandProperty DiskNumber) }}).MediaType"
        
        result = subprocess.check_output(
            ['powershell', '-NoProfile', '-Command', ps_cmd], 
            text=True, creationflags=subprocess.CREATE_NO_WINDOW
        ).strip()
        return result if result else "HDD"
    except:
        return "Unknown"

# network
last_net_io = psutil.net_io_counters(pernic=True)
last_net_time = time.time()
top_download = 0.0
top_upload = 0.0

def get_ipv4(interface_name):
    """gets your ip address."""
    try:
        addrs = psutil.net_if_addrs().get(interface_name, [])
        for addr in addrs:
            if addr.family == socket.AF_INET:
                return addr.address
    except Exception:
        pass
    return "Disconnected"

def get_network_speeds(interface_name):
    """Speed of network"""
    global last_net_io, last_net_time, top_download, top_upload
    
    current_time = time.time()
    current_io = psutil.net_io_counters(pernic=True)
    time_delta = current_time - last_net_time
    
    # fallbacks
    data = {
        "ip": get_ipv4(interface_name),
        "down_speed_Bps": 0.0,
        "up_speed_Bps": 0.0,
        "down_total": 0,
        "up_total": 0,
        "top_down_Bps": top_download,
        "top_up_Bps": top_upload
    }

    if interface_name in current_io and interface_name in last_net_io and time_delta > 0:
        io_now = current_io[interface_name]
        io_old = last_net_io[interface_name]
        
        down_bps = (io_now.bytes_recv - io_old.bytes_recv) / time_delta
        up_bps = (io_now.bytes_sent - io_old.bytes_sent) / time_delta
        
        if down_bps > top_download: 
            top_download = down_bps
        if up_bps > top_upload: 
            top_upload = up_bps
            
        data["down_speed_Bps"] = down_bps
        data["up_speed_Bps"] = up_bps
        data["down_total"] = io_now.bytes_recv
        data["up_total"] = io_now.bytes_sent
        data["top_down_Bps"] = top_download
        data["top_up_Bps"] = top_upload
    
    last_net_io = current_io
    last_net_time = current_time
    
    return data

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
            "sync": stat.isup,
            "auto": True,
            "zero": not stat.isup or name not in addrs
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
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        raw_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        
        # clean up name
        name = raw_name.strip()
        if " with " in name:
            name = name.split(" with ")[0]
        if " @ " in name:
            name = name.split(" @ ")[0]
        name = name.replace("(R)", "").replace("(TM)", "").replace(" CPU", "")
        name = re.sub(r'\s*\d+-Core Processor.*', '', name)
        cpu_name = " ".join(name.split())
    except:
        pass
    freq = psutil.cpu_freq()
    current_ghz = freq.current / 1000 if freq else 0.0
    return cpu_name, round(current_ghz,2)

load_history = collections.deque(maxlen=900)

def update_load_history(current_load):
    load_history.append(current_load)

def get_load_averages():
    """60s, 300s, and 900s averages of the processor queue length"""
    if len(load_history) == 0:
        return 0.0, 0.0, 0.0
    
    def get_avg(samples):
        subset = list(load_history)[-samples:]
        return round(sum(subset) / len(subset), 2)

    return get_avg(60), get_avg(300), get_avg(900)

def generate_cpu_bar(percent, width=30, colors=["\033[48;2;150;200;250m", "\033[48;2;150;250;150m", "\033[48;2;250;100;100m"],block_char = "█"):
    """
    creates a cpu bar
    """
    filled_blocks = int((percent / 100) * width)
    empty_blocks = width - filled_blocks
    
    bar_string = ""
    for i in range(filled_blocks):
        current_percent = (i / width) * 100
        # colors
        if current_percent < 50:
            color = colors[0]
        elif current_percent < 80:
            color = colors[1]
        else:
            color = colors[2]
            
        bar_string += f"{color}{block_char}"
    bar_string += f"\033[38;2;80;80;80m{block_char * empty_blocks}"
    return bar_string + "\033[0m"
