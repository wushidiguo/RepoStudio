import type {Manifest, Scene} from './types';

export const DEFAULT_FPS = 30;
export const DEFAULT_SCENE_SECONDS = 5;

export const getFps = (manifest: Manifest): number => manifest.meta?.fps ?? DEFAULT_FPS;

export const getSceneDurationFrames = (scene: Scene, fps: number): number =>
  Math.max(1, Math.round((scene.duration_s ?? DEFAULT_SCENE_SECONDS) * fps));

export const getTotalDurationFrames = (manifest: Manifest): number => {
  const fps = getFps(manifest);
  return manifest.scenes.reduce(
    (total, scene) => total + getSceneDurationFrames(scene, fps),
    0,
  );
};
