import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownLeft, ArrowLeftRight, Eye } from 'lucide-react';
import type { HighlightGroupsDimensionConfig, HighlightGroup, DimensionProps } from '../../core/types';

const flowIcons = {
  inbound: ArrowDownLeft,
  outbound: ArrowUpRight,
  bidirectional: ArrowLeftRight,
};

export function HighlightGroupsPanel({
  config,
  activeGroupId,
  onGroupSelect,
}: DimensionProps<HighlightGroupsDimensionConfig>) {
  return (
    <div className="dimension-panel highlight-groups-panel">
      <div className="panel-header">
        <Eye size={16} />
        <span>{config.name}</span>
      </div>
      {config.description && (
        <p className="panel-description">{config.description}</p>
      )}

      <div className="group-list">
        <motion.button
          className={`group-item ${activeGroupId === null ? 'active' : ''}`}
          onClick={() => onGroupSelect(null)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="group-icon" style={{ background: '#64748b' }}>
            <Eye size={14} />
          </div>
          <div className="group-info">
            <span className="group-name">全景视图</span>
            <span className="group-desc">查看完整项目结构</span>
          </div>
        </motion.button>

        {config.groups.map((group: HighlightGroup) => {
          const FlowIcon = flowIcons[group.flow_direction || 'bidirectional'];
          const isActive = activeGroupId === group.id;

          return (
            <motion.button
              key={group.id}
              className={`group-item ${isActive ? 'active' : ''}`}
              onClick={() => onGroupSelect(group.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                borderColor: isActive ? group.color : 'transparent',
              }}
            >
              <div
                className="group-icon"
                style={{ background: group.color || '#64748b' }}
              >
                <FlowIcon size={14} />
              </div>
              <div className="group-info">
                <span className="group-name">{group.name}</span>
                <span className="group-desc">{group.description || ''}</span>
              </div>
              {isActive && (
                <motion.div
                  className="active-indicator"
                  layoutId={`highlight-${config.id}`}
                  style={{ background: group.color }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
