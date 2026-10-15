"""Windows GUI and optional CLI for the portable builder."""
from pathlib import Path
import argparse,json,os,queue,sys,threading,time,traceback
from engine import Engine,Cancelled
from i18n import translate

def bundle():return Path(getattr(sys,'_MEIPASS',Path(__file__).parent))
def home():return Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).parent/'local-test'

class App:
    def __init__(self,root,base,lock,source=''):
        import tkinter as tk
        from tkinter import ttk,filedialog,messagebox
        self.tk=tk;self.ttk=ttk;self.dialog=filedialog;self.message=messagebox;self.root=root;self.base=base;self.lock=lock
        self.events=queue.Queue();self.cancel=threading.Event();self.busy=False;self.close_after=False;self.logfile=None
        self.language='ko'
        try:self.language=json.loads((base/'preferences.json').read_text()).get('language','ko')
        except (OSError,ValueError):pass
        if self.language not in ('ko','en'):self.language='ko'
        self.source=tk.StringVar(value=source);self.status=tk.StringVar(value='소스를 선택하고 환경을 준비하세요.');self.accept=tk.BooleanVar(value=False)
        root.title('MTTL-W01 Firmware Builder · 1.0.0');root.geometry('1100x740');root.minsize(1000,640)
        style=ttk.Style();style.theme_use('clam');style.configure('.',font=('Malgun Gothic',10));style.configure('TFrame',background='#f1f5f9');style.configure('TLabel',background='#f1f5f9',foreground='#172b44');style.configure('Title.TLabel',font=('Malgun Gothic',20,'bold'));style.configure('TButton',padding=(13,9));style.configure('TCheckbutton',background='#f1f5f9');style.configure('Accent.TButton',background='#172b44',foreground='white');style.map('Accent.TButton',background=[('active','#29435f')])
        main=ttk.Frame(root,padding=22);main.pack(fill='both',expand=True);main.columnconfigure(0,weight=1);main.rowconfigure(7,weight=1)
        ttk.Label(main,text='MTTL-W01 Firmware Builder',style='Title.TLabel').grid(row=0,column=0,sticky='w')
        self.language_button=ttk.Button(main,text='English',command=self.switch_language);self.language_button.grid(row=0,column=0,sticky='e')
        ttk.Label(main,text='Windows x64').grid(row=1,column=0,sticky='w',pady=(4,18))
        ttk.Label(main,text='소스 폴더 (mttl-source.json이 있는 폴더)').grid(row=2,column=0,sticky='w')
        picker=ttk.Frame(main);picker.grid(row=3,column=0,sticky='ew',pady=(6,10));picker.columnconfigure(0,weight=1)
        self.entry=ttk.Entry(picker,textvariable=self.source);self.entry.grid(row=0,column=0,sticky='ew',ipady=7)
        self.choose=ttk.Button(picker,text='폴더 선택',command=self.choose_source);self.choose.grid(row=0,column=1,padx=(8,0))
        self.import_button=ttk.Button(picker,text='소스 ZIP 가져오기',command=self.import_zip);self.import_button.grid(row=0,column=2,padx=(8,0))
        terms=ttk.Frame(main);terms.grid(row=4,column=0,sticky='ew')
        self.agree=ttk.Checkbutton(terms,text='공식 배포처에서 필수 도구를 다운로드하며 제3자 라이선스가 적용됨을 확인했습니다.',variable=self.accept);self.agree.pack(side='left')
        self.notices=ttk.Button(terms,text='라이선스 안내',command=lambda:os.startfile(str(self.base/'THIRD_PARTY_NOTICES.md')));self.notices.pack(side='right')
        actions=ttk.Frame(main);actions.grid(row=5,column=0,sticky='ew',pady=14)
        self.prepare=ttk.Button(actions,text='1. 환경 준비 / 확인',command=lambda:self.start('prepare'));self.prepare.pack(side='left')
        self.build=ttk.Button(actions,text='2. 펌웨어 빌드',style='Accent.TButton',command=lambda:self.start('build'));self.build.pack(side='left',padx=8)
        self.cancel_button=ttk.Button(actions,text='취소',state='disabled',command=self.cancel.set);self.cancel_button.pack(side='left')
        ttk.Button(actions,text='결과 폴더',command=lambda:self.open_folder('output')).pack(side='right')
        ttk.Button(actions,text='로그 폴더',command=lambda:self.open_folder('logs')).pack(side='right',padx=8)
        self.bar=ttk.Progressbar(main,mode='indeterminate');self.bar.grid(row=6,column=0,sticky='ew',pady=(0,10))
        logframe=ttk.Frame(main);logframe.grid(row=7,column=0,sticky='nsew');logframe.columnconfigure(0,weight=1);logframe.rowconfigure(0,weight=1)
        self.text=tk.Text(logframe,wrap='word',font=('Consolas',10),background='#152238',foreground='#e2e8f0',relief='flat',padx=12,pady=10,state='disabled');self.text.grid(row=0,column=0,sticky='nsew');scroll=ttk.Scrollbar(logframe,command=self.text.yview);scroll.grid(row=0,column=1,sticky='ns');self.text.configure(yscrollcommand=scroll.set)
        ttk.Label(main,textvariable=self.status,wraplength=920).grid(row=8,column=0,sticky='w',pady=(12,5))
        ttk.Label(main,text='전용 폴더만 사용 · 시스템 PATH/환경 변수/레지스트리 변경 없음 · 짧은 영문 경로 권장').grid(row=9,column=0,sticky='w')
        total=sum(x['bytes'] for x in lock['artifacts'])/1048576
        self.append(f'작업 위치: {base}\n최초 다운로드 약 {total:.1f} MiB · 준비 후 오프라인 빌드 가능\n소스는 실행 가능한 코드입니다. 신뢰하는 소스만 선택하세요.\n')
        if Engine(base,lock).ready():self.status.set('환경 준비됨 · 소스를 선택한 뒤 빌드하세요.')
        self.widget_texts=[]
        def collect(widget):
            try:
                value=widget.cget('text')
                if value and widget is not self.language_button:self.widget_texts.append((widget,value))
            except tk.TclError:pass
            for child in widget.winfo_children():collect(child)
        collect(main);self.apply_language()
        root.protocol('WM_DELETE_WINDOW',self.close);root.after(100,self.pump)
    def t(self,text):return translate(text,self.language)
    def apply_language(self):
        for widget,text in self.widget_texts:widget.configure(text=self.t(text))
        self.language_button.configure(text='한국어' if self.language=='en' else 'English')
        value=self.status.get()
        if self.language=='ko':
            from i18n import MESSAGES
            for ko,en in sorted(MESSAGES.items(),key=lambda x:len(x[1]),reverse=True):value=value.replace(en,ko)
        self.status.set(self.t(value))
    def switch_language(self):
        self.language='en' if self.language=='ko' else 'ko';self.apply_language()
        try:
            self.base.mkdir(parents=True,exist_ok=True)
            (self.base/'preferences.json').write_text(json.dumps({'language':self.language}),encoding='utf-8')
        except OSError:pass
    def append(self,line):
        self.text.configure(state='normal');self.text.insert('end',self.t(line)+'\n');self.text.see('end');self.text.configure(state='disabled')
    def choose_source(self):
        value=self.dialog.askdirectory(title=self.t('mttl-source.json이 있는 소스 폴더 선택'))
        if value:self.source.set(value)
    def open_folder(self,name):
        p=self.base/name;p.mkdir(parents=True,exist_ok=True);os.startfile(str(p))
    def import_zip(self):
        value=self.dialog.askopenfilename(title=self.t('소스 ZIP 선택'),filetypes=[('Source ZIP','*.zip')])
        if not value:return
        try:
            dest=self.base/'source'/('import-'+time.strftime('%Y%m%d-%H%M%S'))
            if dest.exists():raise RuntimeError('같은 시각에 가져온 소스가 있습니다. 잠시 뒤 다시 시도하세요.')
            Engine(self.base,self.lock).extract(Path(value),dest,'source')
            candidates=list(dest.rglob('mttl-source.json'))
            if len(candidates)!=1:raise RuntimeError('소스 manifest가 하나여야 합니다.')
            self.source.set(str(candidates[0].parent));self.append('소스 가져오기: '+str(candidates[0].parent))
        except Exception as error:self.message.showerror(self.t('가져오기 실패'),self.t(str(error)))
    def start(self,action):
        if self.busy:return
        if not self.accept.get():self.message.showinfo(self.t('확인 필요'),self.t('라이선스 안내를 확인하고 체크해 주세요.'));return
        source=self.source.get()
        if action=='build' and not source:self.message.showinfo(self.t('소스 선택'),self.t('먼저 소스 폴더를 선택하세요.'));return
        self.busy=True;self.cancel.clear();self.status.set(self.t('환경 준비 중…' if action=='prepare' else '빌드 중…'));self.bar.start(12)
        for widget in (self.entry,self.choose,self.import_button,self.prepare,self.build,self.agree):widget.configure(state='disabled')
        self.cancel_button.configure(state='normal')
        logdir=self.base/'logs';logdir.mkdir(parents=True,exist_ok=True);self.logfile=(logdir/(time.strftime('%Y%m%d-%H%M%S')+'-'+action+'.log')).open('w',encoding='utf-8')
        def worker():
            try:
                engine=Engine(self.base,self.lock,log=lambda s:self.events.put(('log',s)),cancel=self.cancel)
                if action=='prepare':engine.prepare();result='환경 준비 완료 · 이제 펌웨어를 빌드할 수 있습니다.'
                else:result='빌드 성공: '+str(engine.build(source))
                self.events.put(('done',result))
            except Cancelled as e:self.events.put(('cancelled',str(e)))
            except Exception as e:self.events.put(('log',traceback.format_exc()));self.events.put(('error',str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def pump(self):
        while True:
            try:kind,value=self.events.get_nowait()
            except queue.Empty:break
            if kind=='log':
                self.append(value)
                if self.logfile:self.logfile.write(value+'\n');self.logfile.flush()
            else:
                self.append(value);self.status.set(self.t(value));self.busy=False;self.bar.stop()
                for widget in (self.entry,self.choose,self.import_button,self.prepare,self.build,self.agree):widget.configure(state='normal')
                self.cancel_button.configure(state='disabled')
                if self.logfile:self.logfile.write(value+'\n');self.logfile.close();self.logfile=None
                if self.close_after:self.root.destroy();return
        self.root.after(100,self.pump)
    def close(self):
        if self.busy:
            if self.message.askyesno(self.t('작업 중'),self.t('진행 중인 작업을 취소하고 종료할까요?')):
                self.close_after=True;self.cancel.set();self.status.set(self.t('취소 후 종료 중…'))
        else:self.root.destroy()

def main():
    if sys.stdout and hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    parser=argparse.ArgumentParser();parser.add_argument('--home',type=Path);parser.add_argument('--source',default='');parser.add_argument('--prepare',action='store_true');parser.add_argument('--build',action='store_true');parser.add_argument('--accept-licenses',action='store_true');args=parser.parse_args()
    base=(args.home or home()).resolve();lock=json.loads((bundle()/'dependencies.lock.json').read_text(encoding='utf-8'))
    if args.prepare or args.build:
        if not args.accept_licenses:raise SystemExit('Use --accept-licenses after reading the notices.')
        logdir=base/'logs';logdir.mkdir(parents=True,exist_ok=True)
        with (logdir/(time.strftime('%Y%m%d-%H%M%S')+'-cli.log')).open('w',encoding='utf-8') as out:
            def log(s):
                if sys.stdout:print(s,flush=True)
                out.write(s+'\n');out.flush()
            engine=Engine(base,lock,log=log)
            try:
                if args.prepare:engine.prepare()
                if args.build:engine.build(args.source)
            except Exception:log(traceback.format_exc());raise SystemExit(1)
    else:
        import tkinter as tk
        root=tk.Tk();App(root,base,lock,args.source);root.mainloop()
if __name__=='__main__':main()
