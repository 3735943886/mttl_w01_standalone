"""Portable Korean/English recovery GUI. No USB access until Start is clicked."""
from pathlib import Path
import json,queue,sys,threading,datetime
from core import RecoveryError
from backend import OpenOCD
from engine import recover
from runtime import verify_runtime
from prepare import ensure_dependencies

TEXT={
'ko':{'title':'MTTL-W01 Recovery · 0.1.0','heading':'MTTL-W01 순정 펌웨어 복구','lang':'English','file':'순정 1.0.66 FWR','browse':'파일 선택','safe':'Wi-Fi 보드를 AC 보드에서 완전히 분리했으며, 절연된 전원·GND·3.3V 신호와 ST Link V2 연결을 확인했습니다.','write':'순정 복구 실행 (해제 시 진단·이중 백업만 수행)','warning':'복구 시 두 펌웨어 슬롯과 독립 설정을 초기화합니다. 부트·제조·보정 영역은 보존합니다.\n이 버전은 오프라인 모의 검증 단계이며 실제 보드에서 기록 검증 전입니다. 백업에는 비밀번호가 포함될 수 있습니다.','start':'시작','busy':'작업 중… 전원·USB를 분리하지 마세요.','done':'기록·재읽기 검증 완료. 실제 부팅과 설정 AP는 별도 확인하세요.','backup':'진단·이중 백업 완료. CPU는 정지 상태입니다. 보드 전원을 재연결해 부팅하세요.','failed':'작업 실패. 원본 백업과 로그를 보존하세요. 기록을 시작했다면 재부팅하지 마세요.','need':'분리·전원·배선 확인 항목에 체크하세요.','close':'작업 중에는 창을 닫지 마세요.','working':'백업·로그 폴더: '},
'en':{'title':'MTTL-W01 Recovery · 0.1.0','heading':'MTTL-W01 Stock Firmware Recovery','lang':'한국어','file':'Stock 1.0.66 FWR','browse':'Choose file','safe':'Wi-Fi board is fully disconnected from the AC assembly. Isolated power, GND, 3.3V signals and ST Link V2 wiring are checked.','write':'Restore stock firmware (unchecked: diagnose and double-backup only)','warning':'Restore replaces both firmware slots and clears standalone settings. Boot/factory/calibration areas are preserved.\nOffline mock validation only; target writes have not been validated for this tool. Backups may contain passwords.','start':'Start','busy':'Working… Do not disconnect power or USB.','done':'Write/readback verified. Actual boot and setup AP still need checking.','backup':'Diagnosis and double-backup complete. CPU halted; power cycle the board to boot.','failed':'Failed. Keep backups/logs. If writing began, do not reboot.','need':'Confirm board isolation, power and wiring first.','close':'Do not close the window while working.','working':'Backup/log folder: '}}

TEXT['ko'].update(title='MTTL-W01 Recovery · 1.0.0',folder='백업·로그 폴더',warning='복구 시 순정 1.0.66을 양쪽 슬롯에 기록하고 독립 설정을 초기화합니다. 부트·제조·보정 영역은 보존합니다.\n실제 보드 검증은 아직 하지 않았습니다. 백업에는 암호가 포함될 수 있으니 공개하지 마세요.')
TEXT['en'].update(title='MTTL-W01 Recovery · 1.0.0',folder='Backup / logs folder',warning='Restore installs stock 1.0.66 in both slots and clears standalone settings, preserving boot/factory/calibration areas.\nPhysical-board validation is still pending. Backups may contain passwords; keep them private.')
TEXT['ko']['warning']+='\n최초 사용 시 OpenOCD와 순정 FWR를 지정 배포처에서 다운로드·검증합니다. 인터넷이 필요합니다.'
TEXT['en']['warning']+='\nFirst use downloads and verifies OpenOCD and stock FWR from the documented sources. Internet is required.'
STAGES={'ko':{'RUNTIME':'프로그램 구성 파일 확인','CONNECT':'ST Link V2 연결 및 기기 확인','BACKUP 1/2':'전체 이미지 백업 1/2','BACKUP 2/2':'전체 이미지 백업 2/2','FULL READBACK':'최종 전체 이미지 재읽기 검증','VERIFIED; REBOOT REQUEST':'검증 완료 · 재부팅 요청'},'en':{'RUNTIME':'Checking runtime integrity','CONNECT':'Connecting ST Link V2 and identifying target','BACKUP 1/2':'Full flash backup 1/2','BACKUP 2/2':'Full flash backup 2/2','FULL READBACK':'Verifying full flash readback','VERIFIED; REBOOT REQUEST':'Verified · requesting reboot'}}

def home():return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent

class App:
    def __init__(self,root):
        import tkinter as tk
        from tkinter import ttk,filedialog,messagebox
        self.root=root;self.tk=tk;self.ttk=ttk;self.dialog=filedialog;self.message=messagebox;self.base=home();self.language='ko';self.busy=False;self.events=queue.Queue();self.last_session=None
        self.safety=tk.BooleanVar(value=False);self.write=tk.BooleanVar(value=False);self.file=tk.StringVar(value=str(self.base/'firmware/comMTTL-W01_1.0.66.fwr'))
        try:self.language=json.loads((self.base/'preferences.json').read_text()).get('language','ko')
        except (OSError,ValueError):pass
        if self.language not in TEXT:self.language='ko'
        root.geometry('1040x760');root.minsize(900,650);root.protocol('WM_DELETE_WINDOW',self.close)
        style=ttk.Style();style.theme_use('clam');style.configure('.',font=('Segoe UI',10));style.configure('Title.TLabel',font=('Segoe UI',21,'bold'))
        box=ttk.Frame(root,padding=20);box.pack(fill='both',expand=True);box.columnconfigure(0,weight=1);box.rowconfigure(8,weight=1)
        self.title=ttk.Label(box,style='Title.TLabel');self.title.grid(row=0,column=0,sticky='w')
        self.lang=ttk.Button(box,command=self.switch);self.lang.grid(row=0,column=1,sticky='e')
        self.label=ttk.Label(box);self.label.grid(row=1,column=0,sticky='w',pady=(20,6))
        self.entry=ttk.Entry(box,textvariable=self.file);self.entry.grid(row=2,column=0,sticky='ew')
        self.browse=ttk.Button(box,command=self.choose);self.browse.grid(row=2,column=1,padx=(10,0))
        self.ack=ttk.Checkbutton(box,variable=self.safety);self.ack.grid(row=3,column=0,columnspan=2,sticky='w',pady=(20,8))
        self.mode=ttk.Checkbutton(box,variable=self.write);self.mode.grid(row=4,column=0,columnspan=2,sticky='w')
        self.warning=ttk.Label(box,wraplength=950,foreground='#9a3412');self.warning.grid(row=5,column=0,columnspan=2,sticky='w',pady=14)
        self.start=ttk.Button(box,command=self.run);self.start.grid(row=6,column=0,columnspan=2,pady=8)
        self.folder=ttk.Button(box,command=self.open_folder);self.folder.grid(row=6,column=1,sticky='e')
        self.progress=ttk.Progressbar(box,maximum=100);self.progress.grid(row=7,column=0,columnspan=2,sticky='ew',pady=8)
        self.log=tk.Text(box,background='#152338',foreground='#e2e8f0',font=('Consolas',10),state='disabled',wrap='word');self.log.grid(row=8,column=0,columnspan=2,sticky='nsew')
        self.status=ttk.Label(box,wraplength=950);self.status.grid(row=9,column=0,columnspan=2,sticky='w',pady=12)
        self.translate();root.after(80,self.pump)
    def translate(self):
        w=TEXT[self.language];self.root.title(w['title']);self.title.configure(text=w['heading'])
        for widget,key in ((self.lang,'lang'),(self.label,'file'),(self.browse,'browse'),(self.ack,'safe'),(self.mode,'write'),(self.warning,'warning'),(self.start,'start')):widget.configure(text=w[key])
        self.folder.configure(text=w['folder'])
    def open_folder(self):
        import os
        path=self.last_session or self.base/'sessions';path.mkdir(parents=True,exist_ok=True);os.startfile(path)
    def switch(self):
        if self.busy:return
        self.language='en' if self.language=='ko' else 'ko';self.translate()
        try:(self.base/'preferences.json').write_text(json.dumps({'language':self.language}),encoding='utf-8')
        except OSError:pass
    def choose(self):
        p=self.dialog.askopenfilename(filetypes=[('MTTL-W01 FWR','*.fwr')])
        if p:self.file.set(p)
    def close(self):
        if self.busy:self.message.showwarning('MTTL-W01',TEXT[self.language]['close'])
        else:self.root.destroy()
    def run(self):
        if self.busy:return
        w=TEXT[self.language]
        if not self.safety.get():self.message.showwarning('MTTL-W01',w['need']);return
        self.busy=True
        for widget in (self.start,self.browse,self.entry,self.ack,self.mode,self.lang):widget.configure(state='disabled')
        self.status.configure(text=w['busy']);firmware=self.file.get();writing=self.write.get()
        self.progress['value']=0
        def worker():
            session=None
            try:
                session=self.base/'sessions'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+__import__('uuid').uuid4().hex[:8]);session.mkdir(parents=True,exist_ok=False)
                self.last_session=session
                with (session/'openocd.log').open('x',encoding='utf-8') as logfile:
                    lock=threading.Lock()
                    def emit(line):
                        with lock:logfile.write(line+'\n');logfile.flush()
                        self.events.put(('log',line))
                        if line in STAGES[self.language]:self.events.put(('stage',STAGES[self.language][line]))
                        elif line.startswith('WRITE '):self.events.put(('stage',('복구 기록 및 검증: ' if self.language=='ko' else 'Writing and verifying: ')+line[6:]))
                    self.events.put(('log',w['working']+str(session)))
                    emit('RUNTIME');ensure_dependencies(self.base,emit);verify_runtime(self.base)
                    backend=OpenOCD(self.base,session,emit)
                    recover(backend,session,firmware,writing,emit,lambda n,total,phase:self.events.put(('progress',(phase-1)*25+n/total*25)))
                self.events.put(('progress',100));self.events.put(('done',w['done'] if writing else w['backup']))
            except Exception as error:
                if session:
                    try:(session/'error.txt').write_text(str(error),encoding='utf-8')
                    except OSError:pass
                self.events.put(('log','ERROR: '+str(error)));self.events.put(('done',w['failed']+'\n'+str(error)))
        threading.Thread(target=worker,daemon=True).start()
    def pump(self):
        while not self.events.empty():
            kind,value=self.events.get()
            if kind=='log':self.log.configure(state='normal');self.log.insert('end',value+'\n');self.log.see('end');self.log.configure(state='disabled')
            elif kind=='progress':self.progress['value']=value
            elif kind=='stage':self.status.configure(text=value+' · '+TEXT[self.language]['busy'])
            else:
                self.busy=False;self.status.configure(text=value)
                for widget in (self.start,self.browse,self.entry,self.ack,self.mode,self.lang):widget.configure(state='normal')
        self.root.after(80,self.pump)

if __name__=='__main__':
    import tkinter as tk
    if '--self-test' in sys.argv:
        import subprocess
        from core import decode_fwr,sha
        base=home();ensure_dependencies(base,lambda _:None);raw=decode_fwr((base/'firmware/comMTTL-W01_1.0.66.fwr').read_bytes())
        checked=verify_runtime(base)
        version=subprocess.run([str(base/'tools/openocd/bin/openocd.exe'),'--version'],capture_output=True,timeout=15,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if version.returncode:raise RecoveryError('OpenOCD version check failed')
        root=tk.Tk();root.withdraw();app=App(root);root.update_idletasks();app.switch();root.update_idletasks();root.destroy()
        report={'self_test':'passed','runtime_files_verified':checked,'gui_languages':['ko','en'],'firmware_decoded_bytes':len(raw),'openocd_version_only':True,'usb_accessed':False,'device_written':False,'home':str(base)}
        (base/'self-test.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    else:
        root=tk.Tk();App(root);root.mainloop()
