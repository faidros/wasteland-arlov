// Optimise the raw Blender tile export into the game's streamed city.
//   node pipeline/web/tiles.mjs <raw dir> <pack>/tiles
// Tiles: geometry + material names only (the game swaps in the materials from materials.glb).
// materials.glb: every texture once, WebP (base colour 1024, others 512). materials-mobile.glb: 256 px base colour only.
// Adapted from kalmar-kvarnholmen-web/tools/tiles.mjs and mobile.mjs. dedup keeps unique material names:
// the game looks materials up by name, so two identical-looking materials must not be merged.
import { NodeIO, Logger } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, weld, instance, reorder, quantize, meshopt, textureCompress, simplify, flatten, join, mergeDocuments, unpartition } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder, MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';
import { mkdirSync, readFileSync, writeFileSync, statSync, readdirSync, rmSync, renameSync } from 'node:fs';
import { join as pjoin } from 'node:path';

const [src, dst] = process.argv.slice(2);
if (!src || !dst) { console.error('usage: node tiles.mjs <raw dir> <out tiles dir>'); process.exit(2); }
await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready, MeshoptSimplifier.ready]);
const io = new NodeIO().setLogger(new Logger(Logger.Verbosity.ERROR)).registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });
const keep = { keepUniqueNames: true };

const meta = JSON.parse(readFileSync(pjoin(src, 'tiles.json'), 'utf8'));
const parts = readdirSync(src).filter((f) => /^materials_\d+\.glb$/.test(f)).sort();
if (parts.length !== meta.material_parts) throw new Error(`material parts: ${parts.length} of ${meta.material_parts}`);

// Write into a temporary folder and swap at the end, so a failed run never breaks a working city.
const tmp = dst + '.tmp';
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

{
  const doc = await io.read(pjoin(src, parts[0]));
  for (const f of parts.slice(1)) mergeDocuments(doc, await io.read(pjoin(src, f)));
  await doc.transform(unpartition(), dedup(keep), prune(),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 88, resize: [1024, 1024], slots: /^baseColor/ }),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 90, resize: [512, 512], slots: /^(normal|metallicRoughness|occlusion)/ }));
  await io.write(pjoin(tmp, 'materials.glb'), doc);
  console.log('materials', doc.getRoot().listMaterials().length, (statSync(pjoin(tmp, 'materials.glb')).size / 1e6).toFixed(1), 'MB');
}
{
  const doc = await io.read(pjoin(src, parts[0]));
  for (const f of parts.slice(1)) mergeDocuments(doc, await io.read(pjoin(src, f)));
  await doc.transform(unpartition());
  for (const m of doc.getRoot().listMaterials()) m.setNormalTexture(null).setMetallicRoughnessTexture(null).setOcclusionTexture(null);
  await doc.transform(dedup(keep), prune(),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 80, resize: [256, 256], slots: /^(baseColor|emissive)/ }));
  await io.write(pjoin(tmp, 'materials-mobile.glb'), doc);
}

let total = 0;
for (const t of meta.tiles) {
  const doc = await io.read(pjoin(src, `${t.id}.glb`));
  await doc.transform(
    dedup(keep), prune({ keepAttributes: true }), weld(),
    instance({ min: 3 }),
    simplify({ simplifier: MeshoptSimplifier, ratio: 0.0, error: 0.0001, lockBorder: true }),
    flatten(), join({ keepNamed: false }),
    reorder({ encoder: MeshoptEncoder }), quantize(),
  );
  for (const m of doc.getRoot().listMaterials()) {
    m.setBaseColorTexture(null).setNormalTexture(null).setMetallicRoughnessTexture(null).setOcclusionTexture(null).setEmissiveTexture(null);
  }
  await doc.transform(prune({ keepAttributes: true }), meshopt({ encoder: MeshoptEncoder, level: 'high' }));
  const out = pjoin(tmp, `${t.id}.glb`);
  await io.write(out, doc);
  t.bytes = statSync(out).size;
  total += t.bytes;
}
writeFileSync(pjoin(tmp, 'tiles.json'), JSON.stringify(meta));
rmSync(dst, { recursive: true, force: true });
renameSync(tmp, dst);
console.log(`${meta.tiles.length} tiles, ${(total / 1e6).toFixed(1)} MB, ${meta.tiles.reduce((a, t) => a + t.tris, 0).toLocaleString()} triangles`);
console.log('TILES_OK');
