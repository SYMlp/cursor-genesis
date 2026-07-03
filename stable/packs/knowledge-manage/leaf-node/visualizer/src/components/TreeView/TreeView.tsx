import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronRight,
  Folder,
  FolderOpen,
  File,
  Brain,
  ArrowUp,
  ArrowDown,
  RefreshCw,
  Upload,
  GitPullRequest,
  Inbox,
  Package,
  Atom,
  FileCode,
  Layers,
  MessageCircle,
  BookOpen,
  List,
  FolderOpenDot,
  FileText,
  Info,
} from 'lucide-react';
import type { TreeNode, Annotation } from '../../core/types';
import './TreeView.css';

const iconMap: Record<string, React.ComponentType<{ size?: number }>> = {
  brain: Brain,
  'arrow-up': ArrowUp,
  'arrow-down': ArrowDown,
  'refresh-cw': RefreshCw,
  upload: Upload,
  'git-pull-request': GitPullRequest,
  inbox: Inbox,
  package: Package,
  'package-2': Package,
  atom: Atom,
  'file-code': FileCode,
  layers: Layers,
  'message-circle': MessageCircle,
  'book-open': BookOpen,
  list: List,
  'folder-open': FolderOpenDot,
  'file-text': FileText,
  info: Info,
};

interface TreeViewProps {
  node: TreeNode;
  annotations: Record<string, Annotation>;
  highlightPaths: string[];
  selectedPath: string | null;
  expandedPaths: Set<string>;
  onSelect: (path: string) => void;
  onToggle: (path: string) => void;
  depth?: number;
  parentPath?: string;
}

export function TreeView({
  node,
  annotations,
  highlightPaths,
  selectedPath,
  expandedPaths,
  onSelect,
  onToggle,
  depth = 0,
  parentPath = '',
}: TreeViewProps) {
  const currentPath = parentPath ? `${parentPath}/${node.name}` : node.name;
  const normalizedPath = currentPath.replace(/^[^/]+\//, ''); // 移除根目录名
  const isExpanded = expandedPaths.has(currentPath);
  const isSelected = selectedPath === currentPath;
  const isHighlighted = highlightPaths.some(
    (p) => normalizedPath.startsWith(p.replace(/\/$/, '')) || p.replace(/\/$/, '').startsWith(normalizedPath)
  );
  const isDirectHighlight = highlightPaths.some(
    (p) => normalizedPath === p.replace(/\/$/, '') || normalizedPath + '/' === p
  );

  // 查找注解
  const annotation = annotations[normalizedPath] || annotations[normalizedPath + '/'];
  const IconComponent = annotation?.icon ? iconMap[annotation.icon] : null;

  const handleClick = () => {
    onSelect(currentPath);
    if (node.type === 'directory') {
      onToggle(currentPath);
    }
  };

  return (
    <div className="tree-node">
      <motion.div
        className={`tree-item ${isSelected ? 'selected' : ''} ${isHighlighted ? 'highlighted' : ''} ${isDirectHighlight ? 'direct-highlight' : ''}`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={handleClick}
        initial={false}
        animate={{
          backgroundColor: isSelected
            ? 'rgba(99, 102, 241, 0.2)'
            : isDirectHighlight
              ? 'rgba(16, 185, 129, 0.15)'
              : isHighlighted
                ? 'rgba(16, 185, 129, 0.08)'
                : 'transparent',
        }}
        whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
      >
        {node.type === 'directory' && (
          <motion.span
            className="chevron"
            animate={{ rotate: isExpanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight size={14} />
          </motion.span>
        )}
        {node.type === 'file' && <span className="chevron-placeholder" />}

        <span className="icon">
          {IconComponent ? (
            <IconComponent size={16} />
          ) : node.type === 'directory' ? (
            isExpanded ? (
              <FolderOpen size={16} />
            ) : (
              <Folder size={16} />
            )
          ) : (
            <File size={16} />
          )}
        </span>

        <span className="name">{node.name}</span>

        {annotation?.label && (
          <span className="label" style={{ color: annotation.color }}>
            {annotation.label}
          </span>
        )}
      </motion.div>

      <AnimatePresence>
        {node.type === 'directory' && isExpanded && node.children && (
          <motion.div
            className="tree-children"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {node.children.map((child) => (
              <TreeView
                key={child.name}
                node={child}
                annotations={annotations}
                highlightPaths={highlightPaths}
                selectedPath={selectedPath}
                expandedPaths={expandedPaths}
                onSelect={onSelect}
                onToggle={onToggle}
                depth={depth + 1}
                parentPath={currentPath}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
