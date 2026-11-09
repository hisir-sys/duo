const {app,BrowserWindow,ipcMain}=require("electron");
const path=require("node:path");
const {spawn}=require("node:child_process");
const readline=require("node:readline");

const dev=!app.isPackaged;
let backend=null;
let backendReady=null;
let nextId=1;
const pending=new Map();

function rejectPending(message){
  for(const item of pending.values()) item.reject(new Error(message));
  pending.clear();
}
function startBackend(){
  if(backend && backend.exitCode===null) return backendReady;
  const script=dev
    ? path.join(__dirname,"backend_bridge.py")
    : path.join(process.resourcesPath,"backend","backend_bridge.py");
  const command=process.env.DUO_PYTHON || (process.platform==="win32"?"py":"python3");
  const args=process.env.DUO_PYTHON
    ? [script]
    : process.platform==="win32"?["-3","-u",script]:["-u",script];
  backend=spawn(command,args,{cwd:path.resolve(__dirname,"..",".."),windowsHide:true,stdio:["pipe","pipe","pipe"]});
  const child=backend;
  backendReady=new Promise((resolve,reject)=>{
    let settled=false;
    const timer=setTimeout(()=>{
      if(!settled){settled=true;reject(new Error("Python backend did not start in time."));}
    },10000);
    child.once("spawn",()=>{if(!settled){settled=true;clearTimeout(timer);resolve(true);}});
    child.once("error",error=>{
      if(!settled){settled=true;clearTimeout(timer);reject(new Error("Could not start Python backend: "+error.message));}
      rejectPending("Python backend process could not start.");
    });
  });
  const lines=readline.createInterface({input:child.stdout});
  lines.on("line",line=>{
    let message;
    try{message=JSON.parse(line);}catch{return;}
    const item=pending.get(message.id);
    if(!item)return;
    pending.delete(message.id);
    if(message.ok)item.resolve(message.result);
    else item.reject(new Error(message.error||"Backend request failed."));
  });
  child.stderr.on("data",data=>console.warn("[DuoAI Python]",String(data).slice(0,2000)));
  child.on("exit",(code,signal)=>{
    if(backend===child)backend=null;
    rejectPending("Python backend stopped ("+(code??signal??"unknown")+").");
  });
  return backendReady;
}
async function callBackend(method,args={}){
  if(typeof method!=="string"||method.length>80)throw new Error("Invalid backend operation.");
  if(!args||typeof args!=="object"||Array.isArray(args)||JSON.stringify(args).length>1_000_000)throw new Error("Invalid backend arguments.");
  await startBackend();
  if(!backend||backend.exitCode!==null)throw new Error("Python backend is not running.");
  const id=nextId++;
  return new Promise((resolve,reject)=>{
    pending.set(id,{resolve,reject});
    backend.stdin.write(JSON.stringify({id,method,args})+"\n",error=>{
      if(error){pending.delete(id);reject(error);}
    });
  });
}

function createWindow(){
  const win=new BrowserWindow({width:1480,height:940,minWidth:1120,minHeight:720,backgroundColor:"#F4F5F7",title:"DuoAI Studio",show:false,webPreferences:{preload:path.join(__dirname,"preload.cjs"),contextIsolation:true,nodeIntegration:false,sandbox:true,webSecurity:true,webviewTag:false}});
  win.once("ready-to-show",()=>win.show());
  win.webContents.setWindowOpenHandler(()=>({action:"deny"}));
  if(dev)win.loadURL("http://127.0.0.1:5173");
  else win.loadFile(path.join(__dirname,"..","dist","index.html"));
}
ipcMain.handle("duo:backend",(_event,method,args)=>callBackend(method,args));
app.whenReady().then(()=>{startBackend().catch(error=>console.warn("[DuoAI] "+error.message));createWindow();});
app.on("before-quit",()=>{if(backend){backend.stdin.end();backend.kill();backend=null;}});
app.on("window-all-closed",()=>{if(process.platform!=="darwin")app.quit();});
