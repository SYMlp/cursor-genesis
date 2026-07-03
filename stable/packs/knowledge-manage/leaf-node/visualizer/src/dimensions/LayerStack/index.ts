import { LayerStackPanel } from './LayerStackPanel';
import type { LayerStackDimensionConfig } from '../../core/types';

function getHighlightPaths(
  config: LayerStackDimensionConfig,
  activeGroupId: string | null
): string[] {
  if (!activeGroupId) return [];
  const layer = config.layers.find((l) => l.id === activeGroupId);
  return layer?.paths || [];
}

export const LayerStackDimension = {
  type: 'layer-stack' as const,
  SidebarPanel: LayerStackPanel as import('../../core/types').DimensionComponent<LayerStackDimensionConfig>['SidebarPanel'],
  getHighlightPaths,
};
