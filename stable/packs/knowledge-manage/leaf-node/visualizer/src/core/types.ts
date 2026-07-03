import type { ComponentType } from 'react';

// 目录树节点
export interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: TreeNode[];
  expanded?: boolean;
}

// 目录注解
export interface Annotation {
  label: string;
  icon?: string;
  description?: string;
  color?: string;
}

// 项目元信息
export interface ProjectMeta {
  name: string;
  description: string;
  version?: string;
}

// 信息流定义
export interface Flow {
  id: string;
  from: string;
  to: string;
  type: 'inbound' | 'outbound' | 'bidirectional';
  label: string;
  color?: string;
}

// ========== 维度系统 ==========

/** 维度类型标识 */
export type DimensionType = 'highlight-groups' | 'layer-stack' | 'flow-sequence' | 'tag-map' | 'custom';

/** 维度配置基类 - 所有维度类型共享 */
export interface DimensionConfigBase {
  id: string;
  type: DimensionType;
  name: string;
  description?: string;
}

/** highlight-groups 维度：可切换的路径高亮分组 */
export interface HighlightGroup {
  id: string;
  name: string;
  description?: string;
  highlight: string[];
  flow_direction?: 'inbound' | 'outbound' | 'bidirectional';
  color?: string;
}

export interface HighlightGroupsDimensionConfig extends DimensionConfigBase {
  type: 'highlight-groups';
  groups: HighlightGroup[];
}

/** layer-stack 维度：分层堆叠视图 */
export interface LayerItem {
  id: string;
  name: string;
  description?: string;
  paths: string[];
  color?: string;
}

export interface LayerStackDimensionConfig extends DimensionConfigBase {
  type: 'layer-stack';
  layers: LayerItem[];
}

/** flow-sequence 维度：顺序流程视图 */
export interface StageItem {
  id: string;
  name: string;
  description?: string;
  paths: string[];
  color?: string;
}

export interface FlowSequenceDimensionConfig extends DimensionConfigBase {
  type: 'flow-sequence';
  stages: StageItem[];
}

/** tag-map 维度：标签分类视图 */
export interface TagItem {
  id: string;
  name: string;
  paths: string[];
  color?: string;
}

export interface TagMapDimensionConfig extends DimensionConfigBase {
  type: 'tag-map';
  tags: TagItem[];
}

/** 维度配置联合类型 */
export type DimensionConfig =
  | HighlightGroupsDimensionConfig
  | LayerStackDimensionConfig
  | FlowSequenceDimensionConfig
  | TagMapDimensionConfig;

/** 维度组件的 props 基类 */
export interface DimensionProps<T = unknown> {
  config: T;
  projectName: string;
  highlightPaths: string[];
  activeGroupId: string | null;
  onGroupSelect: (id: string | null) => void;
  onExpandPaths?: (paths: string[]) => void;
}

/** 维度组件接口 - 用于注册 */
export interface DimensionComponent<T = unknown> {
  type: DimensionType;
  SidebarPanel: ComponentType<DimensionProps<T>>;
  getHighlightPaths?: (config: T, activeGroupId: string | null) => string[];
}

/** 完整可视化配置 */
export interface VisualizerConfig {
  engine?: { version?: string };
  project: ProjectMeta;
  dimensions: DimensionConfig[];
  flows: Flow[];
  annotations: Record<string, Annotation>;
  structure?: TreeNode[];
}
