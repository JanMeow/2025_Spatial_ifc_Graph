declare module 'react-plotly.js' {
  import * as React from 'react';
  import { Layout, Data, Config, Frames } from 'plotly.js';

  export interface PlotParams {
    data: Data[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    frames?: Frames[];
    onInitialized?: (figure: any) => void;
    onUpdate?: (figure: any) => void;
    onPurge?: (figure: any) => void;
    useResizeHandler?: boolean;
    style?: React.CSSProperties;
    className?: string;
    debug?: boolean;
    divId?: string;
    revision?: number;
  }

  export default class Plot extends React.Component<PlotParams> {}
} 