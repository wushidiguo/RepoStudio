import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {SceneCard} from './scenes';

export type Scene = {
  id: string;
  type: string;
  title?: string;
  narration?: string;
  duration_s?: number;
  visuals?: Array<{kind?: string; src?: string; caption?: string; code?: string}>;
  points?: string[];
  audio?: string;
};

export type Manifest = {
  repo?: {name?: string; url?: string; stars?: number; license?: string; language?: string};
  meta?: {fps?: number};
  scenes: Scene[];
};

export const Explainer: React.FC<{manifest: Manifest}> = ({manifest}) => {
  const fps = manifest.meta?.fps ?? 30;
  let frame = 0;
  return (
    <AbsoluteFill style={{backgroundColor: '#0f172a'}}>
      {manifest.scenes.map((scene, index) => {
        const durationFrames = Math.max(1, Math.round((scene.duration_s ?? 5) * fps));
        const start = frame;
        frame += durationFrames;
        const audioSrc = scene.audio ? staticFile(scene.audio) : null;
        return (
          <Sequence
            key={scene.id ?? index}
            from={start}
            durationInFrames={durationFrames}
            name={scene.id}
          >
            <SceneCard scene={scene} repo={manifest.repo} />
            {audioSrc ? <Audio src={audioSrc} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
