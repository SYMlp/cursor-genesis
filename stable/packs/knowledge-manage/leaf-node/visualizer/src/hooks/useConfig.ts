import { useState, useEffect } from 'react';
import yaml from 'yaml';
import type { VisualizerConfig, TreeNode, DimensionConfig } from '../core/types';
import { validateVisualizerConfig } from '../core/configSchema';

/** 旧版配置格式（向后兼容） */
interface LegacyConfig {
  project: { name: string; description: string; version?: string };
  perspectives?: Array<{
    id: string;
    name: string;
    description: string;
    highlight: string[];
    flow: string;
    color?: string;
  }>;
  flows?: Array<{ id?: string; from: string; to: string; type: string; label: string; color?: string }>;
  annotations?: Record<string, { label: string; icon?: string; description?: string; color?: string }>;
  structure?: TreeNode[];
}

function convertLegacyToDimensions(legacy: LegacyConfig): DimensionConfig[] {
  if (!legacy.perspectives?.length) return [];

  return [
    {
      id: 'perspectives',
      type: 'highlight-groups',
      name: '使用者视角',
      description: '从不同使用者角色理解项目结构',
      groups: legacy.perspectives.map((p) => ({
        id: p.id,
        name: p.name,
        description: p.description,
        highlight: p.highlight,
        flow_direction: p.flow as 'inbound' | 'outbound' | 'bidirectional',
        color: p.color,
      })),
    },
  ];
}

function normalizeConfig(parsed: LegacyConfig & Partial<VisualizerConfig>): VisualizerConfig {
  const hasNewFormat = Array.isArray(parsed.dimensions) && parsed.dimensions.length > 0;
  const dimensions = hasNewFormat
    ? parsed.dimensions!
    : convertLegacyToDimensions(parsed as LegacyConfig);

  const flows = (parsed.flows || []).map((flow, index) => ({
    ...flow,
    id: flow.id || `flow-${index}`,
    type: (flow.type || 'bidirectional') as 'inbound' | 'outbound' | 'bidirectional',
  }));

  return {
    engine: parsed.engine || { version: '1.0.0' },
    project: parsed.project!,
    dimensions,
    flows,
    annotations: parsed.annotations || {},
    structure: parsed.structure,
  };
}

export function useConfig(configPath: string) {
  const [config, setConfig] = useState<VisualizerConfig | null>(null);
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadConfig() {
      try {
        setLoading(true);
        const response = await fetch(configPath);
        if (!response.ok) {
          throw new Error(`Failed to load config: ${response.statusText}`);
        }
        const text = await response.text();
        const parsed = yaml.parse(text) as LegacyConfig & Partial<VisualizerConfig>;
        const normalized = normalizeConfig(parsed);

        const validationErrors = validateVisualizerConfig(normalized);
        if (validationErrors.length > 0) {
          console.warn('[leaf-visualizer] 配置校验警告:', validationErrors);
        }

        setConfig(normalized);

        if (parsed.structure && parsed.structure.length > 0) {
          const root = Array.isArray(parsed.structure) ? parsed.structure[0] : parsed.structure;
          setTree(convertStructureToTree(root));
        } else {
          setTree(null);
        }

        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    loadConfig();
  }, [configPath]);

  return { config, tree, loading, error };
}

/** 将 structure 数组格式转换为 TreeNode */
function convertStructureToTree(
  item: { name: string; type: string; children?: unknown[] },
  parentPath = ''
): TreeNode {
  const path = parentPath ? `${parentPath}/${item.name}` : item.name;
  const node: TreeNode = {
    name: item.name,
    path,
    type: item.type === 'directory' ? 'directory' : 'file',
  };

  if (item.type === 'directory' && Array.isArray(item.children) && item.children.length > 0) {
    node.children = item.children.map((child) =>
      convertStructureToTree(child as { name: string; type: string; children?: unknown[] }, path)
    );
  }

  return node;
}
