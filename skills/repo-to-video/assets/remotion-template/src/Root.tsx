import React from 'react';
import {Composition} from 'remotion';
import {getFps, getTotalDurationFrames} from './duration';
import {Explainer} from './Video';
import './fonts';
import type {Manifest} from './types';
import manifest from '../public/manifest.json';

const typedManifest = manifest as Manifest;
const fps = getFps(typedManifest);
const width = typedManifest.meta?.width ?? 1920;
const height = typedManifest.meta?.height ?? 1080;
const totalFrames = getTotalDurationFrames(typedManifest);

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Explainer"
      component={Explainer}
      durationInFrames={totalFrames}
      fps={fps}
      width={width}
      height={height}
      defaultProps={{manifest: typedManifest}}
    />
  );
};
