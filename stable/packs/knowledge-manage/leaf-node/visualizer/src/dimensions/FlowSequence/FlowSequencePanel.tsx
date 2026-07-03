import { motion } from 'framer-motion';
import { GitBranch, ArrowRight } from 'lucide-react';
import type { FlowSequenceDimensionConfig, StageItem, DimensionProps } from '../../core/types';

export function FlowSequencePanel({
  config,
  activeGroupId,
  onGroupSelect,
}: DimensionProps<FlowSequenceDimensionConfig>) {
  return (
    <div className="dimension-panel flow-sequence-panel">
      <div className="panel-header">
        <GitBranch size={16} />
        <span>{config.name}</span>
      </div>
      {config.description && (
        <p className="panel-description">{config.description}</p>
      )}

      <div className="stage-list">
        <motion.button
          className={`stage-item ${activeGroupId === null ? 'active' : ''}`}
          onClick={() => onGroupSelect(null)}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <span className="stage-name">全部阶段</span>
        </motion.button>

        {config.stages.map((stage: StageItem, index: number) => {
          const isActive = activeGroupId === stage.id;
          return (
            <div key={stage.id} className="stage-row">
              {index > 0 && (
                <div className="stage-connector">
                  <ArrowRight size={12} />
                </div>
              )}
              <motion.button
                className={`stage-item ${isActive ? 'active' : ''}`}
                onClick={() => onGroupSelect(stage.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  borderColor: isActive ? stage.color : 'transparent',
                }}
              >
                <div
                  className="stage-indicator"
                  style={{ background: stage.color || '#64748b' }}
                />
                <div className="stage-content">
                  <span className="stage-name">{stage.name}</span>
                  {stage.description && (
                    <span className="stage-desc">{stage.description}</span>
                  )}
                </div>
              </motion.button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
