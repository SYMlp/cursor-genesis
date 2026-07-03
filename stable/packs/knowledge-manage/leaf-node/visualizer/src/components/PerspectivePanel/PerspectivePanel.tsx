import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownLeft, ArrowLeftRight, Eye } from 'lucide-react';
import type { Perspective } from '../../types';
import './PerspectivePanel.css';

interface PerspectivePanelProps {
  perspectives: Perspective[];
  activePerspective: string | null;
  onSelect: (id: string | null) => void;
}

const flowIcons = {
  inbound: ArrowDownLeft,
  outbound: ArrowUpRight,
  bidirectional: ArrowLeftRight,
};

export function PerspectivePanel({
  perspectives,
  activePerspective,
  onSelect,
}: PerspectivePanelProps) {
  return (
    <div className="perspective-panel">
      <div className="panel-header">
        <Eye size={16} />
        <span>使用者视角</span>
      </div>

      <div className="perspective-list">
        <motion.button
          className={`perspective-item ${activePerspective === null ? 'active' : ''}`}
          onClick={() => onSelect(null)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="perspective-icon" style={{ background: '#64748b' }}>
            <Eye size={14} />
          </div>
          <div className="perspective-info">
            <span className="perspective-name">全景视图</span>
            <span className="perspective-desc">查看完整项目结构</span>
          </div>
        </motion.button>

        {perspectives.map((perspective) => {
          const FlowIcon = flowIcons[perspective.flow];
          const isActive = activePerspective === perspective.id;

          return (
            <motion.button
              key={perspective.id}
              className={`perspective-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelect(perspective.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                borderColor: isActive ? perspective.color : 'transparent',
              }}
            >
              <div
                className="perspective-icon"
                style={{ background: perspective.color }}
              >
                <FlowIcon size={14} />
              </div>
              <div className="perspective-info">
                <span className="perspective-name">{perspective.name}</span>
                <span className="perspective-desc">{perspective.description}</span>
              </div>
              {isActive && (
                <motion.div
                  className="active-indicator"
                  layoutId="activeIndicator"
                  style={{ background: perspective.color }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
