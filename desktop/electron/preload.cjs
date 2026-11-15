const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("hephaestusDesktop", { platform: process.platform });
