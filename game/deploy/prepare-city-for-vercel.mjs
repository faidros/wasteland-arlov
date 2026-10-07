import {cp, lstat, readFile, realpath} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const gameRoot=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const repoRoot=resolve(gameRoot,'..');
const slug=process.env.WASTELAND_CITY||'arlov-borggatan';
if(!/^[a-z0-9-]+$/.test(slug))throw new Error(`Invalid WASTELAND_CITY slug: ${slug}`);

const source=resolve(repoRoot,'cities',slug,'pack');
const sourceConfig=JSON.parse(await readFile(resolve(source,'config.json'),'utf8'));
if(sourceConfig.slug!==slug)throw new Error(`City pack slug mismatch: expected ${slug}, got ${sourceConfig.slug}`);
const target=resolve(gameRoot,'public','city');

let targetStat;
try{targetStat=await lstat(target);}catch(error){if(error.code!=='ENOENT')throw error;}
if(targetStat?.isSymbolicLink()){
  if(await realpath(target)===await realpath(source)){
    console.log(`City link already points to ${slug}.`);
    process.exit(0);
  }
  throw new Error(`game/public/city links to another city. Install ${slug} before building.`);
}
if(targetStat){
  if(targetStat.isDirectory()){
    const installed=JSON.parse(await readFile(resolve(target,'config.json'),'utf8'));
    if(installed.slug===slug){
      console.log(`${slug} is already materialized in game/public/city.`);
      process.exit(0);
    }
  }
  throw new Error('game/public/city exists but is not the requested city pack.');
}

await cp(source,target,{recursive:true});
console.log(`Copied ${slug} pack into game/public/city for the Vercel build.`);