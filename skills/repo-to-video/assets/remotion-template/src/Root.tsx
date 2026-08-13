import React from 'react';
import {Composition} from 'remotion';
import {Explainer} from './Video';
import manifest from '../public/manifest.json';

const meta = (manifest as {meta?: {fps?: number; width?: number; height?: number}}).meta ?? {};
const fps = meta.fps ?? 30;
const width = meta.width ?? 1920;
const height = meta.height ?? 1080;
const totalSeconds = (manifest as {scenes?: Array<{duration_s?: number}>}).scenes?.reduce(
  (acc: number, scene) => acc + (scene.duration_s ?? 5),
  0,
) ?? 20;
const totalFrames = Math.max(1, Math.round(totalSeconds * fps));

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Explainer"
      component={Explainer}
      durationInFrames={totalFrames}
      fps={fps}
      width={width}
      height={height}
      defaultProps={{manifest}}
    />
  );
};
