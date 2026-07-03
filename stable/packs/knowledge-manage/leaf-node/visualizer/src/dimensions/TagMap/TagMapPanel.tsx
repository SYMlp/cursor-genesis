import { motion } from 'framer-motion';
import { Tag, Hash } from 'lucide-react';
import type { TagMapDimensionConfig, TagItem, DimensionProps } from '../../core/types';

export function TagMapPanel({
  config,
  activeGroupId,
  onGroupSelect,
}: DimensionProps<TagMapDimensionConfig>) {
  return (
    <div className="dimension-panel tag-map-panel">
      <div className="panel-header">
        <Tag size={16} />
        <span>{config.name}</span>
      </div>
      {config.description && (
        <p className="panel-description">{config.description}</p>
      )}

      <div className="tag-list">
        <motion.button
          className={`tag-item ${activeGroupId === null ? 'active' : ''}`}
          onClick={() => onGroupSelect(null)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Hash size={14} />
          <span className="tag-name">全部标签</span>
        </motion.button>

        {config.tags.map((tag: TagItem) => {
          const isActive = activeGroupId === tag.id;
          return (
            <motion.button
              key={tag.id}
              className={`tag-item ${isActive ? 'active' : ''}`}
              onClick={() => onGroupSelect(tag.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                borderColor: isActive ? tag.color : 'transparent',
                borderLeftColor: tag.color,
              }}
            >
              <span
                className="tag-dot"
                style={{ background: tag.color || '#64748b' }}
              />
              <span className="tag-name">{tag.name}</span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
