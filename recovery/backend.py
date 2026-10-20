"""Persistent localhost Tcl RPC owner; never auto-connect on import."""
from pathlib import Path
import socket,subprocess,threading,time,os
from core import RecoveryError,require,SIZE,SECTOR,allowed

def tcl_path(path):
    text=str(Path(path).resolve()).replace('\\','/')
    require(not any(c in text for c in '{}\n\r'),'Unsupported path characters')
    return '{'+text+'}'

class OpenOCD:
    def __init__(self,home,session,log):
        self.home,self.session,self.log=Path(home),Path(session),log
        self.process=None;self.sock=None;self.rebooted=False
    def connect(self):
        exe=self.home/'tools/openocd/bin/openocd.exe'
        scripts=self.home/'tools/openocd/share/openocd/scripts'
        rtl=self.home/'tools/rtl8711af'
        require(exe.is_file(),'OpenOCD runtime missing')
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
        args=[str(exe),'-s',str(scripts),'-s',str(rtl),'-f','interface/stlink.cfg','-c','transport select hla_swd','-f','rtl8710-legacy.ocd','-c','adapter speed 100','-c','set rtl8710_flasher_buffer_size 262144','-c','bindto 127.0.0.1','-c','gdb_port disabled','-c','telnet_port disabled','-c',f'tcl_port {port}','-c','init','-c','reset halt']
        self.process=subprocess.Popen(args,cwd=self.session,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        def output():
            for line in self.process.stdout:self.log(line.decode('utf-8',errors='replace').rstrip())
        self.output_thread=threading.Thread(target=output,daemon=True);self.output_thread.start()
        for _ in range(150):
            if self.process.poll() is not None:raise RecoveryError('OpenOCD failed; check driver, wiring and power. See log.')
            try:self.sock=socket.create_connection(('127.0.0.1',port),timeout=.2);break
            except OSError:time.sleep(.1)
        require(self.sock is not None,'OpenOCD connection timeout')
        self.sock.settimeout(120)
        self.rpc('rtl8710_flash_read_id')
        capacity=int(self.rpc('set rtl8710_flasher_capacity'))
        require(capacity==SIZE,'Unsupported flash size')
        cpuid=int(self.rpc('rtl8710_flasher_mrw 0xe000ed00'),0)
        require((cpuid>>4)&0xfff==0xc23,'Unsupported CPU; expected Cortex-M3')
        self.rpc('rtl8710_flash_auto_erase 0; rtl8710_flash_auto_verify 0')
        return {'capacity':capacity,'cpuid':hex(cpuid),'speed_khz':100}
    def rpc(self,command):
        wire='set recovery_rc [catch {'+command+'} recovery_msg]; if {$recovery_rc} {format {ERR:%s} $recovery_msg} else {format {OK:%s} $recovery_msg}'
        self.sock.sendall(wire.encode('utf-8')+b'\x1a');data=bytearray()
        while b'\x1a' not in data:
            chunk=self.sock.recv(65536)
            require(bool(chunk),'OpenOCD disconnected; target must not be restarted')
            data.extend(chunk);require(len(data)<1048576,'Invalid RPC response')
        text=bytes(data).split(b'\x1a',1)[0].decode('utf-8',errors='replace')
        require(text.startswith('OK:'),'OpenOCD: '+text[:500])
        return text[3:]
    def read(self,address,size):
        require(0<=address<SIZE and 0<size<=262144 and address+size<=SIZE,'Invalid read range')
        p=self.session/'transfer.bin'
        self.rpc(f'rtl8710_flasher_read_block {address} {size}; dump_image {tcl_path(p)} [expr {{$rtl8710_flasher_buffer + 0x20}}] {size}')
        data=p.read_bytes();require(len(data)==size,'Short flash read');return data
    def dump(self,path,progress):
        data=bytearray()
        # Persist each completed chunk, so an interrupted read is visibly partial.
        with Path(path).open('xb') as f:
            for address in range(0,SIZE,262144):
                block=self.read(address,262144);f.write(block);f.flush();data.extend(block);progress(address+len(block),SIZE)
            os.fsync(f.fileno())
        return bytes(data)
    def write(self,step):
        require(allowed(step),'Write outside recovery allowlist')
        p=self.session/'write.bin';p.write_bytes(step.data)
        if step.erase:self.rpc(f'rtl8710_flash_sector_erase {step.address}')
        # Even erased settings are checked with a fresh read, not only driver status.
        if step.data!=b'\xff'*len(step.data):self.rpc(f'rtl8710_flash_write {tcl_path(p)} {step.address}')
        require(self.read(step.address,len(step.data))==step.data,'Flash readback mismatch; stopped without reset')
    def reset(self):self.rpc('rtl8710_reboot');self.rebooted=True
    def close(self):
        if self.sock:
            try:
                self.sock.settimeout(2)
                if not self.rebooted:self.rpc('halt')
            except Exception:pass
            self.sock.close();self.sock=None
        if self.process:
            self.process.terminate()
            try:self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
            if hasattr(self,'output_thread'):self.output_thread.join(timeout=3)
