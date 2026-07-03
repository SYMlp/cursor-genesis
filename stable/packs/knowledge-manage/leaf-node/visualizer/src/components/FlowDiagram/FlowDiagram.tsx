import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, ArrowLeftRight, GitBranch } from 'lucide-react';
import type { Flow } from '../../core/types';
import './FlowDiagram.css';

interface FlowDiagramProps {
  flows: Flow[];
  activeFlowIds?: string[];
  projectName?: string;
}

export function FlowDiagram({ flows, activeFlowIds, projectName = 'project' }: FlowDiagramProps) {
  return (
    <div className="flow-diagram">
      <div className="flow-header">
        <GitBranch size={16} />
        <span>信息流向</span>
      </div>

      <div className="flow-container">
        {/* 上游区域 */}
        <div className="flow-zone upstream">
          <div className="zone-label">上游</div>
          <div className="zone-entity">knowledge-graph</div>
        </div>

        {/* 中心区域 - 当前项目 */}
        <div className="flow-zone center">
          <div className="zone-label">当前项目</div>
          <div className="zone-entity current">{projectName}</div>

          {/* 流向箭头 */}
          <div className="flow-arrows">
            {flows.map((flow) => {
              const isActive = activeFlowIds?.includes(flow.id);
              const isUpstream = flow.from === 'knowledge-graph' || flow.to.includes('upstream');
              const isDownstream = flow.from.includes('downstream') || flow.to === 'downstream-projects';

              return (
                <motion.div
                  key={flow.id}
                  className={`flow-arrow ${isActive ? 'active' : ''} ${isUpstream ? 'upstream' : ''} ${isDownstream ? 'downstream' : ''}`}
                  initial={{ opacity: 0.3 }}
                  animate={{
                    opacity: isActive ? 1 : 0.4,
                    scale: isActive ? 1.05 : 1,
                  }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="arrow-line" style={{ borderColor: flow.color }}>
                    {flow.type === 'bidirectional' ? (
                      <ArrowLeftRight size={16} style={{ color: flow.color }} />
                    ) : flow.type === 'inbound' ? (
                      <ArrowLeft size={16} style={{ color: flow.color }} />
                    ) : (
                      <ArrowRight size={16} style={{ color: flow.color }} />
                    )}
                  </div>
                  <span className="arrow-label" style={{ color: flow.color }}>
                    {flow.label}
                  </span>

                  {/* 动画粒子 */}
                  {isActive && (
                    <motion.div
                      className="flow-particle"
                      style={{ background: flow.color }}
                      animate={{
                        x: flow.type === 'inbound' ? [40, -40] : [-40, 40],
                        opacity: [0, 1, 0],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: 'linear',
                      }}
                    />
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* 下游区域 */}
        <div className="flow-zone downstream">
          <div className="zone-label">下游</div>
          <div className="zone-entity">downstream-projects</div>
          <div className="zone-example">(anfu_test 等)</div>
        </div>
      </div>
    </div>
  );
}
