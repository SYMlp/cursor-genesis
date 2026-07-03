import { motion, AnimatePresence } from 'framer-motion';
import { X, Folder, File, Info, Tag, ArrowRight } from 'lucide-react';
import type { Annotation, Flow } from '../../core/types';
import './DetailPanel.css';

interface RelatedGroup {
  id: string;
  name: string;
  description?: string;
  color?: string;
}

interface DetailPanelProps {
  path: string | null;
  annotation: Annotation | null;
  relatedGroups: RelatedGroup[];
  relatedFlows: Flow[];
  onClose: () => void;
}

export function DetailPanel({
  path,
  annotation,
  relatedGroups,
  relatedFlows,
  onClose,
}: DetailPanelProps) {
  const isDirectory = path?.endsWith('/') || !path?.includes('.');
  const fileName = path?.split('/').pop() || '';

  return (
    <AnimatePresence>
      {path && (
        <motion.div
          className="detail-panel"
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 300, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        >
          <div className="detail-header">
            <div className="detail-title">
              {isDirectory ? <Folder size={18} /> : <File size={18} />}
              <span>{fileName}</span>
            </div>
            <button className="close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>

          <div className="detail-path">{path}</div>

          {annotation && (
            <div className="detail-section">
              <div className="section-header">
                <Info size={14} />
                <span>说明</span>
              </div>
              <div className="section-content">
                {annotation.label && (
                  <div className="detail-label" style={{ color: annotation.color }}>
                    <Tag size={12} />
                    {annotation.label}
                  </div>
                )}
                {annotation.description && (
                  <p className="detail-description">{annotation.description}</p>
                )}
              </div>
            </div>
          )}

          {relatedGroups.length > 0 && (
            <div className="detail-section">
              <div className="section-header">
                <ArrowRight size={14} />
                <span>相关维度</span>
              </div>
              <div className="section-content">
                {relatedGroups.map((g) => (
                  <div
                    key={g.id}
                    className="related-item"
                    style={{ borderLeftColor: g.color }}
                  >
                    <span className="related-name">{g.name}</span>
                    {g.description && (
                      <span className="related-desc">{g.description}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {relatedFlows.length > 0 && (
            <div className="detail-section">
              <div className="section-header">
                <ArrowRight size={14} />
                <span>相关流向</span>
              </div>
              <div className="section-content">
                {relatedFlows.map((f) => (
                  <div
                    key={f.id}
                    className="related-item"
                    style={{ borderLeftColor: f.color }}
                  >
                    <span className="related-name">{f.label}</span>
                    <span className="related-desc">
                      {f.from} → {f.to}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
