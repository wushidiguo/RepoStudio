export type Visual = {
  kind?: string;
  src?: string;
  caption?: string;
  code?: string;
};

export type Scene = {
  id: string;
  type: string;
  title?: string;
  narration?: string;
  duration_s?: number;
  visuals?: Visual[];
  points?: string[];
  audio?: string;
};

export type Manifest = {
  repo?: {
    name?: string;
    url?: string;
    stars?: number;
    license?: string;
    language?: string;
  };
  meta?: {
    fps?: number;
    width?: number;
    height?: number;
  };
  scenes: Scene[];
};
