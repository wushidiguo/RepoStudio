# Rendering

## Remotion (default engine)

The bundled template at `assets/remotion-template/` is a single Composition
(`Explainer`, 1920x1080 @ 30 fps) driven entirely by `public/manifest.json`.

1. Copy the template and install:

```bash
cp -r <skill-dir>/assets/remotion-template video
cd video
npm install
```

2. Stage the job's media:

```bash
cp ../manifest.json public/manifest.json
cp -r ../audio public/audio
cp -r ../captures public/captures
cp -r ../diagrams public/diagrams
```

3. Iterate visually (optional): `npx remotion studio`.
4. Render: `npx remotion render src/index.ts Explainer out.mp4`.

Scene rendering support in the template:

- `title`, `hook`, `outro`: typography-driven cards using `title`, `points`,
  and repo metadata.
- `architecture`, `datamodel`, `flow`, `demo`: full-bleed `visuals` image with
  optional caption bar.
- `code`: monospace block from `visual.code` (or image from `visual.src`).
- `insight`: large number/label card from `points`.
- Per-scene audio mounted at cumulative offsets; fade-in transitions between
  scenes.

Notes: requires Node 18+; first `npm install` takes 1-2 minutes and the first
render downloads a headless Chrome. To add new layouts, edit `src/scenes.tsx`
(React); keep everything manifest-driven.

## HyperFrames (alternative engine)

Use when the environment already exposes the hyperframes skills
(`hyperframes-core`, `hyperframes-cli`) or the user prefers HyperFrames.
Requires Node 22+ and FFmpeg.

1. Scaffold: `npx hyperframes init video --non-interactive --example=<name>`
   (see the hyperframes-cli skill for example names).
2. Translate the manifest into a composition: one clip per scene with
   `data-duration` from `duration_s`, `<img>` elements for visuals, and audio
   tracks per scene. Follow the composition contract in the hyperframes-core
   skill; run `npx hyperframes lint` after the first pass.
3. Gate: `npx hyperframes check`.
4. Render: `npx hyperframes render --quality high --output video/out.mp4`.

Read the hyperframes-cli and hyperframes-core skills before running commands in
this phase.

## Final verification

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 out.mp4
```

Duration must be 60-180 s. Also verify the file is non-empty and the audio
track is present (`ffprobe -show_streams`).
