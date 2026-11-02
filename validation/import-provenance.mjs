import {createHash} from 'node:crypto'

// Explicit compiler-anchor compensations introduced in 5fa112f. Reconstruct
// the exact original import, including every footprint/model byte, rather than
// accepting arbitrary edits to these wrappers or refreshing the upstream hash.
const insertions = {
  'imports/RFANT3216120A5T/RFANT3216120A5T.tsx':
    '        // Core now anchors at footprint origin; preserve the validated CAD pose.\n        positionOffset: { x: 0.026035, y: 0, z: 0 },\n',
  'imports/X201632MKB4SI/X201632MKB4SI.tsx':
    '        // Preserve the validated CAD pose with footprint-origin anchoring.\n        positionOffset: { x: -0.000127, y: 0, z: 0 },\n',
}
const sha = bytes => createHash('sha256').update(bytes).digest('hex')
export function verifyImportedFile(file, bytes) {
  if (sha(bytes) === file.sha256) return 'original'
  const insertion = insertions[file.path], source = bytes.toString('utf8')
  if (!insertion || source.split(insertion).length !== 2 ||
      sha(source.replace(insertion, '')) !== file.sha256)
    throw new Error(`Imported file changed: ${file.path}`)
  return 'compiler-anchor-compensation'
}
