const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("forgeDesktop", { platform: process.platform });
