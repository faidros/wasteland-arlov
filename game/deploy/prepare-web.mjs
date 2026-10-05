// Runs after `vite build`: writes dist/arena-config.json and the Apache .htaccess.
// ARENA_URL=wss://arena.example.com/ws npm run build   → online arena points at your relay.
// Without ARENA_URL the arena uses the same origin (/arena/ws), which only the dev server provides.
import {copyFile,writeFile} from 'node:fs/promises';

const url=process.env.ARENA_URL||'';
if(url&&new URL(url).protocol!=='wss:')throw new Error('The published arena URL must use wss:// (HTTPS sites cannot open ws://).');
await writeFile(new URL('../dist/arena-config.json',import.meta.url),JSON.stringify({url},null,2)+'\n');
await copyFile(new URL('web.htaccess',import.meta.url),new URL('../dist/.htaccess',import.meta.url));
console.log(url?`Publication prepared: online arena at ${url}`:'Publication prepared without an arena relay (set ARENA_URL=wss://… to enable online play).');
