"""One-click recovery workflow. All target access is injected and testable."""
from pathlib import Path
import datetime,json,os
from core import require,verify_backup,make_plan,decode_fwr,sha,SIZE

def save_json(path,value):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,ensure_ascii=False);f.flush();os.fsync(f.fileno())

def recover(backend,session,fwr,write,log,progress):
    """No reset on any failed check. Never resume a partially written image."""
    session=Path(session);result={'version':'1.1','started':datetime.datetime.now().isoformat(),'write_requested':bool(write),'writes_started':False,'completed':False,'physical_boot_verified':False}
    try:
        # Validate before USB access, while still enforcing backup before writes.
        firmware=Path(fwr).read_bytes() if write else None
        if write:decode_fwr(firmware)
        log('CONNECT');result['probe']=backend.connect()
        log('BACKUP 1/2');a=backend.dump(session/'backup-1.bin',lambda n,total:progress(n,total,1))
        log('BACKUP 2/2');b=backend.dump(session/'backup-2.bin',lambda n,total:progress(n,total,2))
        result['diagnosis']=verify_backup(a,b);result['backup_sha256']=sha(a)
        save_json(session/'backup-verified.json',result)
        log('BACKUP VERIFIED: '+sha(a))
        if not write:
            result['completed']=True;log('DIAGNOSIS COMPLETE; CPU HALTED. Power cycle isolated board to boot.');return result
        plan=make_plan(a,firmware);result['firmware_sha256']=plan.firmware_sha256
        # Private, same-device recovery image, not a redistributable firmware.
        with (session/'recovery-image-PRIVATE.bin').open('xb') as f:
            f.write(plan.expected);f.flush();os.fsync(f.fileno())
        save_json(session/'plan.json',{'backup_sha256':plan.backup_sha256,'firmware_sha256':plan.firmware_sha256,'expected_sha256':sha(plan.expected),'steps':[{'address':hex(s.address),'bytes':len(s.data),'erase':s.erase,'phase':s.phase,'sha256':sha(s.data)} for s in plan.steps]})
        require(sha((session/'backup-1.bin').read_bytes())==plan.backup_sha256,'Backup file changed before writing')
        require(sha((session/'backup-2.bin').read_bytes())==plan.backup_sha256,'Backup file changed before writing')
        result['planned_steps']=len(plan.steps)
        for i,step in enumerate(plan.steps):
            log(f'WRITE {step.phase} {step.address:#x}');result['writes_started']=True
            backend.write(step);result['last_verified_step']=i+1;result['last_verified_address']=hex(step.address);progress(i+1,len(plan.steps),3)
        log('FULL READBACK')
        actual=backend.dump(session/'readback.bin',lambda n,total:progress(n,total,4))
        require(len(actual)==SIZE and actual==plan.expected,'Full image verification failed; no reboot')
        result['readback_sha256']=sha(actual);result['write_verified']=True
        save_json(session/'verified-before-reset.json',result)
        log('VERIFIED; REBOOT REQUEST');backend.reset();result['reset_requested']=True;result['completed']=True
        return result
    except Exception as error:
        result['error']=str(error);raise
    finally:
        try:backend.close()
        finally:save_json(session/'result.json',result)
