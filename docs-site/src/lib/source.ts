// @ts-ignore
import { docs, meta } from '../../.source/server';
import { loader } from 'fumadocs-core/source';

const mappedDocs = docs.map((doc: any) => { return { type: 'page', path: doc.info.path, data: doc }; });
const mappedMeta = meta.map((m: any) => { return { type: 'meta', path: m.info.path, data: m }; });

export const source = loader({
  baseUrl: '/docs',
  source: {
    files: [...mappedDocs, ...mappedMeta] as any,
  },
});
