"""MTTL-W01 recovery planning. Pure stdlib; no USB or target access."""
import hashlib, json, struct
from dataclasses import dataclass

SIZE=0x100000
FIRST,SECOND,SETTINGS,FACTORY=0xb000,0x80000,0xee000,0xf0000
SECTOR=4096
BOOT_SIZE=14984
BOOT_SHA='4a3d3f255f94aae0efceb75c3cae54ae8c7339f75f80ab2fe80be3ab66b1f428'
SEED=bytes.fromhex('ca5923e7d79a84e843b3afe794b1afa7')
TABLE=bytes.fromhex('52544b57696e00ff000101009581010100000000')
NEW,OLD=b'81958711',b'01958711'

class RecoveryError(RuntimeError):pass
def require(ok,message):
    if not ok:raise RecoveryError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def word(data,offset):return struct.unpack_from('<I',data,offset)[0]

def decode_fwr(data):
    require(44<=len(data)<=SETTINGS-SECOND,'Invalid FWR length')
    require(sha(data)=='d780b578af69d52f3a05191a8e7d91a20e05085a912722327481cd5663682c04','This prototype accepts only the reference stock 1.0.66 FWR')
    key=bytes(((a^b)+1)&255 for a,b in zip(SEED,data[:16]))
    raw=data[:16]+bytes(v^key[i%16] for i,v in enumerate(data[16:],16))
    require(raw[8:16]==b'\xff'*8 and word(raw,4)==0x10006000,'Invalid FWR header; BIN and full dumps are not supported')
    require(word(raw,0)+20==len(raw) and raw[20:40]==TABLE,'Unsupported Image2 layout')
    entry=word(raw,16)
    require(entry&1 and 0x10006018<=entry&~1<0x10006000+word(raw,0),'Invalid entry point')
    require(sum(raw[:-4])&0xffffffff==word(raw,len(raw)-4),'Invalid FWR checksum')
    # Initial recovery release accepts the verified OEM family/version only.
    require(len(raw)>102000 and raw[736:745]==b'MTTL-W01\0' and raw[70036:70045]==b'MTTL-W01\0' and raw[101988:101995]==b'1.0.66\0','Only OEM MTTL-W01 1.0.66 FWR is supported')
    return raw

def diagnose(dump):
    require(len(dump)==SIZE,'Expected a complete 1 MiB flash dump')
    require((word(dump,0x18)&0xffff)*1024==FIRST and word(dump,0x9000)==SECOND,'Unsupported boot slot map')
    require(word(dump,16)==BOOT_SIZE and sha(dump[32:32+BOOT_SIZE])==BOOT_SHA,'Unknown bootloader; writes are refused')
    slots=[]
    for start,end in ((FIRST,SECOND),(SECOND,SETTINGS)):
        n=word(dump,start)+20
        slots.append({'address':hex(start),'signature':dump[start+8:start+16].hex(),'length':n,'length_in_slot':44<=n<=end-start})
    return {'flash_bytes':SIZE,'bootloader_sha256':BOOT_SHA,'slots':slots,'settings_nonblank':dump[SETTINGS:FACTORY]!=b'\xff'*(FACTORY-SETTINGS),'factory_preserved':True}

@dataclass(frozen=True)
class Step:
    address:int
    data:bytes
    erase:bool
    phase:str

@dataclass(frozen=True)
class Plan:
    expected:bytes
    steps:tuple
    backup_sha256:str
    firmware_sha256:str

def make_plan(dump,fwr):
    diagnose(dump);raw=decode_fwr(fwr);current=bytearray(dump);steps=[]
    for address in (SETTINGS,SETTINGS+SECTOR):
        require(dump[address+2048:address+SECTOR]==b'\xff'*2048,'Unknown data in settings-sector tail; writes refused')
    # First make slot 2 bootable. Only then replace slot 1. No mass erase.
    for start,end in ((SECOND,SETTINGS),(FIRST,SECOND)):
        staged=raw+b'\xff'*(end-start-len(raw))
        for off in range(0,len(staged),SECTOR):
            address=start+off;block=staged[off:off+SECTOR]
            if current[address:address+SECTOR]!=block:
                steps.append(Step(address,block,True,'slot2' if start==SECOND else 'slot1'))
                current[address:address+SECTOR]=block
        # Full sector readback occurs before setting a bootable signature.
        steps.append(Step(start+8,NEW,False,'activate'))
        current[start+8:start+16]=NEW
    steps.append(Step(SECOND+8,OLD,False,'fallback'))
    current[SECOND+8:SECOND+16]=OLD
    for address in (SETTINGS,SETTINGS+SECTOR):
        steps.append(Step(address,b'\xff'*SECTOR,True,'clear-settings'))
        current[address:address+SECTOR]=b'\xff'*SECTOR
    require(current[:FIRST]==dump[:FIRST] and current[FACTORY:]==dump[FACTORY:],'Protected region changed')
    return Plan(bytes(current),tuple(steps),sha(dump),sha(fwr))

def allowed(step):
    if step.erase:return step.address%SECTOR==0 and len(step.data)==SECTOR and FIRST<=step.address<FACTORY
    return step.address in (FIRST+8,SECOND+8) and step.data in (NEW,OLD)

def verify_backup(a,b):
    require(len(a)==SIZE and a==b,'Backup reads differ or are incomplete; no flash writes permitted')
    return diagnose(a)
