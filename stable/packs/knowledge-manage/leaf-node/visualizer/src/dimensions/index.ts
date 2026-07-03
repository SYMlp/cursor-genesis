import { DimensionRegistry } from '../core/DimensionRegistry';
import { HighlightGroupsDimension } from './HighlightGroups';
import { LayerStackDimension } from './LayerStack';
import { FlowSequenceDimension } from './FlowSequence';
import { TagMapDimension } from './TagMap';

// 注册所有内置维度类型
DimensionRegistry.register({
  type: 'highlight-groups',
  component: HighlightGroupsDimension,
});

DimensionRegistry.register({
  type: 'layer-stack',
  component: LayerStackDimension,
});

DimensionRegistry.register({
  type: 'flow-sequence',
  component: FlowSequenceDimension,
});

DimensionRegistry.register({
  type: 'tag-map',
  component: TagMapDimension,
});

export { HighlightGroupsDimension, LayerStackDimension, FlowSequenceDimension, TagMapDimension };
