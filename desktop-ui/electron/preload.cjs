const {contextBridge,ipcRenderer}=require("electron");
contextBridge.exposeInMainWorld("duoDesktop",Object.freeze({
  platform:process.platform,
  shell:"electron",
  backend:Object.freeze({
    invoke:(method,args={})=>ipcRenderer.invoke("duo:backend",method,args)
  })
}));
