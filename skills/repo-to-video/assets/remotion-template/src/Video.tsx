import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {getFps, getSceneDurationFrames} from './duration';
import {SceneCard} from './scenes';
import type {Manifest} from './types';

export const Explainer: React.FC<{manifest: Manifest}> = ({manifest}) => {
  const fps = getFps(manifest);
  let frame = 0;
  return (
    <AbsoluteFill style={{backgroundColor: '#0f172a'}}>
      {manifest.scenes.map((scene, index) => {
        const durationFrames = getSceneDurationFrames(scene, fps);
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
            <SceneCard scene={scene} repo={manifest.repo} durationInFrames={durationFrames} />
            {audioSrc ? <Audio src={audioSrc} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
