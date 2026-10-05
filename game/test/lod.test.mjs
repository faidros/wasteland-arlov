import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {MeshoptSimplifier} from 'three/addons/libs/meshopt_simplifier.module.js';
import {simplifyLevels} from '../src/lod.js';
import {copyPositions} from '../src/bvh-builder.js';
import {skipWithoutCity,cityJSON,readCity} from './fixtures/city.mjs';

test('Distant LODs of the densest generated tile reuse its vertices and never add triangles',{skip:skipWithoutCity},async()=>{
  await MeshoptSimplifier.ready;
  const densest=cityJSON('tiles/tiles.json').tiles.filter(t=>t.id!=='base').sort((a,b)=>b.tris-a.tris)[0];
  const buffer=readCity(`tiles/${densest.id}.glb`);
  const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),'');
  gltf.scene.updateMatrixWorld(true);
  let full=0,near=0,far=0;
  gltf.scene.traverse(mesh=>{
    if(!mesh.isMesh)return;
    const position=copyPositions(mesh.geometry.attributes.position),index=mesh.geometry.index.array.slice(),scale=new THREE.Vector3();
    mesh.matrixWorld.decompose(new THREE.Vector3(),new THREE.Quaternion(),scale);
    const [nearLevel,silhouette]=simplifyLevels(MeshoptSimplifier,position,index,scale.toArray(),[{ratio:.25,error:.01},{ratio:.05,error:.08,compact:true}]);
    const vertices=position.length/3;full+=index.length/3;near+=nearLevel.index.length/3;far+=silhouette.index.length/3;
    // The near LOD indexes the mesh's own vertex buffers.
    assert(nearLevel.index.every(v=>v<vertices));assert.equal(nearLevel.index.length%3,0);
    if(vertices<=65536)assert(nearLevel.index instanceof Uint16Array);
    // The silhouette carries only vertices it uses, each an exact copy of an original vertex.
    const originals=new Set();for(let i=0;i<vertices;i++)originals.add(`${position[i*3]},${position[i*3+1]},${position[i*3+2]}`);
    const used=new Set(silhouette.index);assert.equal(used.size,silhouette.positions.length/3);
    for(let i=0;i<silhouette.positions.length;i+=3)assert(originals.has(`${silhouette.positions[i]},${silhouette.positions[i+1]},${silhouette.positions[i+2]}`));
  });
  // Generated cities are already low-poly boxes; the simplifier may keep most of them within its error bound.
  assert(full>1000,`tile has ${full} triangles`);
  assert(near<=full&&far<=near,`near ${near}, silhouette ${far} of ${full}`);
});
