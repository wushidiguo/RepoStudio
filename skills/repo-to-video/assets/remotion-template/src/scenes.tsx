import React, {useMemo} from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import type {Manifest, Scene, Visual} from './types';

const C = {
  bg: '#0f172a',
  panel: '#1e293b',
  ink: '#f1f5f9',
  muted: '#94a3b8',
  accent: '#38bdf8',
  line: '#334155',
};

const LABELS: Record<string, string> = {
  title: 'Title',
  hook: 'Hook',
  architecture: 'Architecture',
  datamodel: 'Data model',
  flow: 'Flow',
  demo: 'Live demo',
  code: 'Code',
  insight: 'Insight',
  outro: 'Outro',
};

const FadeIn: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const y = interpolate(frame, [0, 12], [24, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        transform: `translateY(${y}px)`,
        display: 'flex',
      }}
    >
      {children}
    </div>
  );
};

const Chip: React.FC<{children: React.ReactNode}> = ({children}) => (
  <span
    style={{
      background: C.panel,
      border: `1px solid ${C.line}`,
      color: C.muted,
      borderRadius: 999,
      padding: '10px 26px',
      fontSize: 30,
      fontFamily: 'Inter, system-ui, sans-serif',
    }}
  >
    {children}
  </span>
);

const Caption: React.FC<{text: string; bottom?: number}> = ({text, bottom = 0}) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      bottom,
      padding: '24px 60px',
      background: 'rgba(2,6,23,0.78)',
      color: C.ink,
      fontSize: 34,
      fontFamily: 'Inter, system-ui, sans-serif',
    }}
  >
    {text}
  </div>
);

const KenBurnsImage: React.FC<{src: string; durationInFrames: number}> = ({
  src,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const progress = durationInFrames > 1 ? frame / (durationInFrames - 1) : 0;
  const scale = interpolate(progress, [0, 1], [1, 1.08], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const translateX = interpolate(progress, [0, 1], [0, -24], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div style={{flex: 1, overflow: 'hidden', minWidth: 0, minHeight: 0, position: 'relative'}}>
      <Img
        src={staticFile(src)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          transform: `scale(${scale}) translateX(${translateX}px)`,
        }}
      />
    </div>
  );
};

const VisualItem: React.FC<{
  visual: Visual;
  big?: boolean;
  durationInFrames: number;
}> = ({visual, big, durationInFrames}) => {
  if (visual.code) {
    return (
      <pre
        style={{
          flex: 1,
          margin: 0,
          padding: big ? '48px 64px' : '36px',
          background: C.panel,
          color: C.ink,
          fontSize: big ? 34 : 26,
          lineHeight: big ? 1.55 : 1.5,
          fontFamily: '"JetBrains Mono", "Fira Code", monospace',
          whiteSpace: 'pre-wrap',
          borderLeft: big ? `8px solid ${C.accent}` : undefined,
          minWidth: 0,
          minHeight: 0,
          overflow: 'hidden',
        }}
      >
        {visual.code}
      </pre>
    );
  }
  if (visual.src) {
    return <KenBurnsImage src={visual.src} durationInFrames={durationInFrames} />;
  }
  return null;
};

const VisualBlock: React.FC<{scene: Scene; durationInFrames: number}> = ({
  scene,
  durationInFrames,
}) => {
  const visuals = scene.visuals ?? [];
  if (visuals.length === 0) {
    return null;
  }
  const captionBottom = scene.narration?.trim() ? 104 : 0;
  if (visuals.length === 1) {
    const v = visuals[0];
    return (
      <>
        <VisualItem visual={v} big durationInFrames={durationInFrames} />
        {v.caption ? <Caption text={v.caption} bottom={captionBottom} /> : null}
      </>
    );
  }
  return (
    <div
      style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: 24,
        padding: 40,
        minWidth: 0,
        minHeight: 0,
      }}
    >
      {visuals.map((v, i) => (
        <div
          key={i}
          style={{position: 'relative', display: 'flex', minWidth: 0, minHeight: 0}}
        >
          <VisualItem visual={v} durationInFrames={durationInFrames} />
        </div>
      ))}
    </div>
  );
};

const PointsCard: React.FC<{points: string[]; big?: boolean}> = ({points, big}) => (
  <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 28, padding: '0 120px'}}>
    {points.map((point, i) => (
      <div key={i} style={{display: 'flex', alignItems: 'center', gap: 28}}>
        <div
          style={{
            width: big ? 28 : 20,
            height: big ? 28 : 20,
            borderRadius: 999,
            background: C.accent,
            flexShrink: 0,
          }}
        />
        <div
          style={{
            color: C.ink,
            fontSize: big ? 60 : 46,
            lineHeight: 1.3,
            fontFamily: 'Inter, system-ui, sans-serif',
            fontWeight: 500,
          }}
        >
          {point}
        </div>
      </div>
    ))}
  </div>
);

const CountUp: React.FC<{value: string; durationInFrames: number}> = ({
  value,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  if (!/^[\d,]+$/.test(value)) {
    return <>{value}</>;
  }
  const target = parseInt(value.replace(/,/g, ''), 10);
  const progress = interpolate(
    frame,
    [0, Math.max(1, Math.round(durationInFrames * 0.6))],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  return <>{Math.round(target * progress).toLocaleString('en-US')}</>;
};

const splitCaptionTokens = (text: string): string[] => {
  const matches = text.match(
    /[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]|[^\s\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]+/g
  );
  return matches ?? [];
};

const NarrationCaption: React.FC<{text: string; durationInFrames: number}> = ({
  text,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const tokens = useMemo(() => splitCaptionTokens(text), [text]);
  if (tokens.length === 0) {
    return null;
  }
  const revealEnd = Math.max(1, Math.round(durationInFrames * 0.85));
  const progress = interpolate(frame, [0, revealEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const revealed = Math.floor(progress * tokens.length);
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 4,
        padding: '22px 60px 30px',
        background: 'rgba(2,6,23,0.85)',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0 10px',
      }}
    >
      {tokens.map((token, i) => (
        <span
          key={i}
          style={{
            fontSize: 30,
            lineHeight: 1.5,
            fontFamily: 'Inter, system-ui, sans-serif',
            color: i < revealed ? C.ink : 'rgba(148,163,184,0.28)',
          }}
        >
          {token}
        </span>
      ))}
    </div>
  );
};

export const SceneCard: React.FC<{
  scene: Scene;
  repo?: Manifest['repo'];
  durationInFrames: number;
}> = ({scene, repo, durationInFrames}) => {
  const {type, title, points, narration} = scene;
  const label = LABELS[type] ?? type;
  const showCaption = type !== 'title' && type !== 'outro' && Boolean(narration?.trim());

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <FadeIn>
        {type === 'title' || type === 'outro' ? (
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: 30, padding: 80, textAlign: 'center'}}>
            <div style={{color: C.accent, fontSize: 34, fontFamily: 'Inter, system-ui, sans-serif', textTransform: 'uppercase', letterSpacing: 6}}>
              {type === 'title' ? label : 'Thanks for watching'}
            </div>
            <div style={{color: C.ink, fontSize: 88, lineHeight: 1.12, fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 700, maxWidth: 1500}}>
              {title}
            </div>
            <div style={{color: C.muted, fontSize: 40, fontFamily: 'Inter, system-ui, sans-serif', maxWidth: 1400}}>
              {narration}
            </div>
            <div style={{display: 'flex', gap: 18, marginTop: 20, flexWrap: 'wrap', justifyContent: 'center'}}>
              {repo?.stars ? <Chip>★ {repo.stars.toLocaleString()}</Chip> : null}
              {repo?.license ? <Chip>{repo.license}</Chip> : null}
              {repo?.language ? <Chip>{repo.language}</Chip> : null}
              {type === 'outro' && repo?.url ? (
                <div style={{color: C.accent, fontSize: 30, fontFamily: 'Inter, system-ui, sans-serif', marginTop: 12}}>
                  {repo.url}
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        {type === 'hook' || type === 'flow' ? (
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 36, padding: '0 120px'}}>
            {title ? (
              <div style={{color: C.ink, fontSize: 64, lineHeight: 1.2, fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 700}}>
                {title}
              </div>
            ) : null}
            <PointsCard points={points ?? [narration ?? '']} />
          </div>
        ) : null}

        {type === 'insight' ? (
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: 40, padding: 80, textAlign: 'center'}}>
            {title ? (
              <div style={{color: C.muted, fontSize: 44, fontFamily: 'Inter, system-ui, sans-serif'}}>
                {title}
              </div>
            ) : null}
            <div style={{color: C.accent, fontSize: 150, lineHeight: 1, fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 800}}>
              <CountUp value={points?.[0] ?? ''} durationInFrames={durationInFrames} />
            </div>
            <div style={{color: C.ink, fontSize: 52, fontFamily: 'Inter, system-ui, sans-serif'}}>
              {points?.[1] ?? narration}
            </div>
          </div>
        ) : null}

        {type === 'architecture' || type === 'datamodel' || type === 'demo' || type === 'code' ? (
          <div style={{flex: 1, display: 'flex', position: 'relative'}}>
            {title ? (
              <div style={{position: 'absolute', top: 36, left: 60, zIndex: 2, color: C.ink, fontSize: 44, fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 700}}>
                {title}
              </div>
            ) : null}
            <div style={{flex: 1, display: 'flex', padding: title ? '110px 40px 40px 40px' : 40}}>
              <VisualBlock scene={scene} durationInFrames={durationInFrames} />
            </div>
          </div>
        ) : null}

        {!['title', 'outro', 'hook', 'flow', 'insight', 'architecture', 'datamodel', 'demo', 'code'].includes(type) ? (
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 24, padding: '0 120px'}}>
            {title ? (
              <div style={{color: C.ink, fontSize: 64, lineHeight: 1.2, fontFamily: 'Inter, system-ui, sans-serif', fontWeight: 700}}>
                {title}
              </div>
            ) : null}
            {narration ? (
              <div style={{color: C.muted, fontSize: 44, lineHeight: 1.4, fontFamily: 'Inter, system-ui, sans-serif'}}>
                {narration}
              </div>
            ) : null}
          </div>
        ) : null}
      </FadeIn>
      {showCaption ? <NarrationCaption text={narration ?? ''} durationInFrames={durationInFrames} /> : null}
    </AbsoluteFill>
  );
};
