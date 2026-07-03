import { motion } from 'framer-motion';
import { Layers, ChevronRight } from 'lucide-react';
import type { LayerStackDimensionConfig, LayerItem, DimensionProps } from '../../core/types';

export function LayerStackPanel({
  config,
  activeGroupId,
  onGroupSelect,
}: DimensionProps<LayerStackDimensionConfig>) {
  return (
    <div className="dimension-panel layer-stack-panel">
      <div className="panel-header">
        <Layers size={16} />
        <span>{config.name}</span>
      </div>
      {config.description && (
        <p className="panel-description">{config.description}</p>
      )}

      <div className="layer-list">
        <motion.button
          className={`layer-item ${activeGroupId === null ? 'active' : ''}`}
          onClick={() => onGroupSelect(null)}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <span className="layer-name">全部显示</span>
        </motion.button>

        {config.layers.map((layer: LayerItem) => {
          const isActive = activeGroupId === layer.id;
          return (
            <motion.button
              key={layer.id}
              className={`layer-item ${isActive ? 'active' : ''}`}
              onClick={() => onGroupSelect(layer.id)}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              style={{
                borderLeftColor: isActive ? layer.color : 'transparent',
              }}
            >
              <div
                className="layer-color-bar"
                style={{ background: layer.color || '#64748b' }}
              />
              <div className="layer-content">
                <span className="layer-name">{layer.name}</span>
                {layer.description && (
                  <span className="layer-desc">{layer.description}</span>
                )}
              </div>
              <ChevronRight size={14} className="layer-chevron" />
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
