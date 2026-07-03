// 目录树节点
export interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: TreeNode[];
  expanded?: boolean;
}

// 视角定义
export interface Perspective {
  id: string;
  name: string;
  description: string;
  highlight: string[];  // 高亮的路径列表
  flow: 'inbound' | 'outbound' | 'bidirectional';
  color?: string;
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

// 完整配置
export interface VisualizerConfig {
  project: ProjectMeta;
  perspectives: Perspective[];
  flows: Flow[];
  annotations: Record<string, Annotation>;
}

// 应用状态
export interface AppState {
  config: VisualizerConfig | null;
  tree: TreeNode | null;
  selectedPath: string | null;
  activePerspective: string | null;
  expandedPaths: Set<string>;
}
