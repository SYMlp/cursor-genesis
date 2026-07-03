import type { DimensionType } from './types';

const VALID_DIMENSION_TYPES: DimensionType[] = [
  'highlight-groups',
  'layer-stack',
  'flow-sequence',
  'tag-map',
  'custom',
];

export interface ValidationError {
  path: string;
  message: string;
}

export function validateVisualizerConfig(config: unknown): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!config || typeof config !== 'object') {
    return [{ path: '', message: '配置必须是一个对象' }];
  }

  const c = config as Record<string, unknown>;

  if (!c.project || typeof c.project !== 'object') {
    errors.push({ path: 'project', message: '缺少 project 配置' });
  } else {
    const p = c.project as Record<string, unknown>;
    if (!p.name || typeof p.name !== 'string') {
      errors.push({ path: 'project.name', message: 'project.name 必须是非空字符串' });
    }
    if (!p.description || typeof p.description !== 'string') {
      errors.push({ path: 'project.description', message: 'project.description 必须是非空字符串' });
    }
  }

  if (!Array.isArray(c.dimensions) && !Array.isArray((c as { perspectives?: unknown }).perspectives)) {
    errors.push({
      path: 'dimensions',
      message: '缺少 dimensions 或 perspectives 配置（至少需要一种理解维度）',
    });
  }

  if (Array.isArray(c.dimensions)) {
    c.dimensions.forEach((dim: unknown, index: number) => {
      if (!dim || typeof dim !== 'object') {
        errors.push({ path: `dimensions[${index}]`, message: '维度配置必须是对象' });
        return;
      }
      const d = dim as Record<string, unknown>;
      if (!d.id || typeof d.id !== 'string') {
        errors.push({ path: `dimensions[${index}].id`, message: '维度 id 必须是非空字符串' });
      }
      if (!d.type || !VALID_DIMENSION_TYPES.includes(d.type as DimensionType)) {
        errors.push({
          path: `dimensions[${index}].type`,
          message: `维度 type 必须是以下之一: ${VALID_DIMENSION_TYPES.join(', ')}`,
        });
      }
      if (!d.name || typeof d.name !== 'string') {
        errors.push({ path: `dimensions[${index}].name`, message: '维度 name 必须是非空字符串' });
      }
    });
  }

  if (!Array.isArray(c.flows)) {
    errors.push({ path: 'flows', message: 'flows 必须是数组' });
  }

  if (c.annotations && typeof c.annotations !== 'object') {
    errors.push({ path: 'annotations', message: 'annotations 必须是对象' });
  }

  return errors;
}
