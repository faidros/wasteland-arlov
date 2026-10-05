// Test helpers: a small synthetic street grid for the game logic, and access to the installed city
// pack (public/city → cities/<slug>/pack) for tests that check real generated tiles.
import {existsSync,readFileSync} from 'node:fs';
import {CITY} from '../../src/city-config.js';

export const cityDir=new URL('../../public/city/',import.meta.url);
export const installed=existsSync(new URL('tiles/tiles.json',cityDir));
export const skipWithoutCity=installed?false:'no city installed (python3 wasteland.py play <slug> --no-serve)';
export const readCity=path=>readFileSync(new URL(path,cityDir));
export const cityJSON=path=>JSON.parse(readCity(path));

// Streets every 60 m (z = 2.5 + 60k and x = 30 + 60k), 10 m wide, with a building block in each cell.
export function gridMap(){
  const roads=[],buildings=[],span=240;
  for(let k=-4;k<=4;k++){
    roads.push({id:`ew${k}`,name:`Row ${k}`,kind:'residential',w:10,p:[[-span,2.5+60*k],[span,2.5+60*k]]});
    roads.push({id:`ns${k}`,name:`Column ${k}`,kind:'residential',w:10,p:[[30+60*k,-span],[30+60*k,span]]});
  }
  for(let i=-4;i<4;i++)for(let j=-4;j<4;j++){
    const x0=30+60*i+9,x1=30+60*(i+1)-9,z0=2.5+60*j+9,z1=2.5+60*(j+1)-9;
    buildings.push([[x0,z0],[x1,z0],[x1,z1],[x0,z1]]);
  }
  const land=[[-span-30,-span-30],[span+30,-span-30],[span+30,span+30],[-span-30,span+30]];
  return {roads,buildings,land:[land],areas:[{k:'land',p:[land]}]};
}

// The engine's original test layout: spawn on an east–west street, heading west.
export function useGridCity(){
  Object.assign(CITY,{name:'Testville',spawn:{x:-5,z:2.5,heading:Math.PI/2},bounds:{minX:-270,maxX:270,minZ:-270,maxZ:270},
    crates:[[-100,2.5],[48,62.5],[150,-57.5]],fires:[[-43,2.5],[45,62.5]],labels:[],districts:[],squares:[]});
  return gridMap();
}
