import { HighlightGroupsPanel } from './HighlightGroupsPanel';
import type { HighlightGroupsDimensionConfig } from '../../core/types';

function getHighlightPaths(
  config: HighlightGroupsDimensionConfig,
  activeGroupId: string | null
): string[] {
  if (!activeGroupId) return [];
  const group = config.groups.find((g) => g.id === activeGroupId);
  return group?.highlight || [];
}

export const HighlightGroupsDimension = {
  type: 'highlight-groups' as const,
  SidebarPanel: HighlightGroupsPanel as import('../../core/types').DimensionComponent<HighlightGroupsDimensionConfig>['SidebarPanel'],
  getHighlightPaths,
};
