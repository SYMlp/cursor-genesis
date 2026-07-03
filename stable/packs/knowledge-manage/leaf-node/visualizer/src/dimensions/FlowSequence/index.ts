import { FlowSequencePanel } from './FlowSequencePanel';
import type { FlowSequenceDimensionConfig } from '../../core/types';

function getHighlightPaths(
  config: FlowSequenceDimensionConfig,
  activeGroupId: string | null
): string[] {
  if (!activeGroupId) return [];
  const stage = config.stages.find((s) => s.id === activeGroupId);
  return stage?.paths || [];
}

export const FlowSequenceDimension = {
  type: 'flow-sequence' as const,
  SidebarPanel: FlowSequencePanel as import('../../core/types').DimensionComponent<FlowSequenceDimensionConfig>['SidebarPanel'],
  getHighlightPaths,
};
