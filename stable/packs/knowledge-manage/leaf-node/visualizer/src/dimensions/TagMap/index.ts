import { TagMapPanel } from './TagMapPanel';
import type { TagMapDimensionConfig } from '../../core/types';

function getHighlightPaths(
  config: TagMapDimensionConfig,
  activeGroupId: string | null
): string[] {
  if (!activeGroupId) return [];
  const tag = config.tags.find((t) => t.id === activeGroupId);
  return tag?.paths || [];
}

export const TagMapDimension = {
  type: 'tag-map' as const,
  SidebarPanel: TagMapPanel as import('../../core/types').DimensionComponent<TagMapDimensionConfig>['SidebarPanel'],
  getHighlightPaths,
};
