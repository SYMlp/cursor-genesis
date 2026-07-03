import { useState, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Loader2, AlertCircle } from 'lucide-react';
import { useConfig } from './hooks/useConfig';
import { TreeView } from './components/TreeView';
import { FlowDiagram } from './components/FlowDiagram';
import { DetailPanel } from './components/DetailPanel';
import { DimensionSwitcher } from './components/DimensionSwitcher';
import { DimensionRegistry } from './core/DimensionRegistry';
import './dimensions/shared.css';
import './App.css';

// 注册内置维度（副作用导入）
import './dimensions';

function App() {
  // 配置路径：优先使用 /config.yaml（叶子节点部署时放置），否则使用示例配置
const configPath = '/config.yaml';
const { config, tree, loading, error } = useConfig(configPath);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [activeDimensionId, setActiveDimensionId] = useState<string | null>(null);
  const [activeGroupId, setActiveGroupId] = useState<string | null>(null);
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set());

  const projectName = config?.project.name || 'project';
  const rootPath = tree?.name || projectName;

  // 初始化展开根路径
  const effectiveExpandedPaths = useMemo(() => {
    const paths = new Set(expandedPaths);
    if (rootPath && !paths.size) paths.add(rootPath);
    return paths;
  }, [expandedPaths, rootPath]);

  // 当前选中的维度配置
  const activeDimension = useMemo(() => {
    if (!config || !activeDimensionId) return null;
    return config.dimensions.find((d) => d.id === activeDimensionId) || null;
  }, [config, activeDimensionId]);

  // 默认选中第一个维度
  const defaultDimensionId = config?.dimensions?.[0]?.id ?? null;
  const effectiveDimensionId = activeDimensionId ?? defaultDimensionId;
  const effectiveDimension = activeDimension ?? config?.dimensions?.[0] ?? null;

  // 获取当前维度的高亮路径
  const highlightPaths = useMemo(() => {
    if (!effectiveDimension || !config) return [];
    return DimensionRegistry.getHighlightPaths(effectiveDimension, activeGroupId);
  }, [effectiveDimension, activeGroupId, config]);

  // 获取当前维度相关的流向
  const activeFlowIds = useMemo(() => {
    if (!effectiveDimension || !config) return [];
    if (effectiveDimension.type === 'highlight-groups' && activeGroupId) {
      const group = (effectiveDimension as { groups: Array<{ id: string; flow_direction?: string; highlight: string[] }> }).groups.find(
        (g) => g.id === activeGroupId
      );
      if (!group) return [];
      return config.flows
        .filter((flow) => {
          if (group.flow_direction === 'inbound' && flow.type === 'inbound') return true;
          if (group.flow_direction === 'outbound' && flow.type === 'outbound') return true;
          if (group.flow_direction === 'bidirectional') return true;
          return group.highlight.some(
            (h) => flow.to.includes(h.split('/')[0]) || flow.from.includes(h.split('/')[0])
          );
        })
        .map((f) => f.id);
    }
    return config.flows.map((f) => f.id);
  }, [effectiveDimension, activeGroupId, config]);

  // 获取选中路径的注解
  const selectedAnnotation = useMemo(() => {
    if (!selectedPath || !config) return null;
    const normalizedPath = selectedPath.replace(/^[^/]+\//, '');
    return config.annotations[normalizedPath] || config.annotations[normalizedPath + '/'] || null;
  }, [selectedPath, config]);

  // 获取选中路径相关的维度组（用于详情面板）
  const relatedGroups = useMemo(() => {
    if (!selectedPath || !config) return [];
    const normalizedPath = selectedPath.replace(/^[^/]+\//, '');
    const result: Array<{ id: string; name: string; description?: string; color?: string }> = [];

    for (const dim of config.dimensions) {
      if (dim.type === 'highlight-groups') {
        const groups = (dim as { groups: Array<{ id: string; name: string; description?: string; color?: string; highlight: string[] }> }).groups;
        for (const g of groups) {
          if (
            g.highlight.some(
              (h) =>
                normalizedPath.startsWith(h.replace(/\/$/, '')) || h.replace(/\/$/, '').startsWith(normalizedPath)
            )
          ) {
            result.push({ id: g.id, name: g.name, description: g.description, color: g.color });
          }
        }
      } else if (dim.type === 'layer-stack') {
        const layers = (dim as { layers: Array<{ id: string; name: string; description?: string; color?: string; paths: string[] }> }).layers;
        for (const l of layers) {
          if (l.paths.some((p) => normalizedPath.startsWith(p.replace(/\/$/, '')) || p.replace(/\/$/, '').startsWith(normalizedPath))) {
            result.push({ id: l.id, name: l.name, description: l.description, color: l.color });
          }
        }
      } else if (dim.type === 'flow-sequence') {
        const stages = (dim as { stages: Array<{ id: string; name: string; description?: string; color?: string; paths: string[] }> }).stages;
        for (const s of stages) {
          if (s.paths.some((p) => normalizedPath.startsWith(p.replace(/\/$/, '')) || p.replace(/\/$/, '').startsWith(normalizedPath))) {
            result.push({ id: s.id, name: s.name, description: s.description, color: s.color });
          }
        }
      } else if (dim.type === 'tag-map') {
        const tags = (dim as { tags: Array<{ id: string; name: string; color?: string; paths: string[] }> }).tags;
        for (const t of tags) {
          if (t.paths.some((p) => normalizedPath.startsWith(p.replace(/\/$/, '')) || p.replace(/\/$/, '').startsWith(normalizedPath))) {
            result.push({ id: t.id, name: t.name, color: t.color });
          }
        }
      }
    }
    return result;
  }, [selectedPath, config]);

  // 获取选中路径相关的流向
  const relatedFlows = useMemo(() => {
    if (!selectedPath || !config) return [];
    const normalizedPath = selectedPath.replace(/^[^/]+\//, '');
    const firstPart = normalizedPath.split('/')[0];
    return config.flows.filter(
      (f) => f.to.includes(firstPart) || f.from.includes(firstPart)
    );
  }, [selectedPath, config]);

  const handleToggle = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  }, []);

  const handleDimensionSelect = useCallback((dimId: string | null) => {
    setActiveDimensionId(dimId);
    setActiveGroupId(null);
  }, []);

  const handleGroupSelect = useCallback(
    (groupId: string | null) => {
      setActiveGroupId(groupId);
      if (groupId && effectiveDimension && config) {
        const paths = DimensionRegistry.getHighlightPaths(effectiveDimension, groupId);
        if (paths.length > 0) {
          setExpandedPaths((prev) => {
            const next = new Set(prev);
            next.add(rootPath);
            paths.forEach((p) => {
              const parts = p.split('/').filter(Boolean);
              let current = rootPath;
              next.add(current);
              parts.forEach((part) => {
                current += '/' + part;
                next.add(current);
              });
            });
            return next;
          });
        }
      }
    },
    [effectiveDimension, config, rootPath]
  );

  if (loading) {
    return (
      <div className="loading-container">
        <Loader2 className="spinner" size={32} />
        <span>加载配置中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <AlertCircle size={32} />
        <span>加载失败: {error}</span>
      </div>
    );
  }

  if (!config || !tree) {
    return (
      <div className="error-container">
        <AlertCircle size={32} />
        <span>配置或结构数据缺失</span>
      </div>
    );
  }

  const dimensionComponent = effectiveDimension
    ? DimensionRegistry.get(effectiveDimension.type)
    : null;

  const SidebarPanel = dimensionComponent?.SidebarPanel;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-title">{config.project.name}</h1>
          <span className="app-version">{config.project.version || ''}</span>
        </div>
        <p className="app-description">{config.project.description}</p>
      </header>

      <div className="app-content">
        <aside className="sidebar">
          <DimensionSwitcher
            dimensions={config.dimensions}
            activeDimensionId={effectiveDimensionId}
            onDimensionSelect={handleDimensionSelect}
          />

          {config.dimensions.length > 0 && effectiveDimension && SidebarPanel && (
            <motion.div
              key={effectiveDimension.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <SidebarPanel
                config={effectiveDimension}
                projectName={projectName}
                highlightPaths={highlightPaths}
                activeGroupId={activeGroupId}
                onGroupSelect={handleGroupSelect}
              />
            </motion.div>
          )}

          <FlowDiagram flows={config.flows} activeFlowIds={activeFlowIds} projectName={projectName} />
        </aside>

        <main className="main-content">
          <motion.div
            className="tree-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <TreeView
              node={tree}
              annotations={config.annotations}
              highlightPaths={highlightPaths}
              selectedPath={selectedPath}
              expandedPaths={effectiveExpandedPaths}
              onSelect={setSelectedPath}
              onToggle={handleToggle}
            />
          </motion.div>
        </main>

        <DetailPanel
          path={selectedPath}
          annotation={selectedAnnotation}
          relatedGroups={relatedGroups}
          relatedFlows={relatedFlows}
          onClose={() => setSelectedPath(null)}
        />
      </div>
    </div>
  );
}

export default App;
