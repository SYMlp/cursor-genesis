import { motion } from 'framer-motion';
import { LayoutGrid, Layers, GitBranch, Tag } from 'lucide-react';
import type { DimensionConfig, DimensionType } from '../../core/types';

const dimensionIcons: Record<DimensionType, React.ComponentType<{ size?: number }>> = {
  'highlight-groups': LayoutGrid,
  'layer-stack': Layers,
  'flow-sequence': GitBranch,
  'tag-map': Tag,
  custom: LayoutGrid,
};

interface DimensionSwitcherProps {
  dimensions: DimensionConfig[];
  activeDimensionId: string | null;
  onDimensionSelect: (id: string | null) => void;
}

export function DimensionSwitcher({
  dimensions,
  activeDimensionId,
  onDimensionSelect,
}: DimensionSwitcherProps) {
  return (
    <div className="dimension-switcher">
      <div className="switcher-header">
        <span className="switcher-label">理解维度</span>
      </div>
      <div className="switcher-tabs">
        {dimensions.map((dim) => {
          const Icon = dimensionIcons[dim.type];
          const isActive = activeDimensionId === dim.id;
          return (
            <motion.button
              key={dim.id}
              className={`switcher-tab ${isActive ? 'active' : ''}`}
              onClick={() => onDimensionSelect(dim.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {Icon && <Icon size={14} />}
              <span>{dim.name}</span>
              {isActive && (
                <motion.div
                  className="tab-indicator"
                  layoutId="dimensionTabIndicator"
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
