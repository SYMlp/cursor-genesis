import type { DimensionConfig, DimensionType } from './types';

/** 维度组件注册项 */
export interface DimensionRegistration<T = unknown> {
  type: DimensionType;
  component: import('./types').DimensionComponent<T>;
}

/** 维度注册表 - 管理所有可用的维度类型 */
class DimensionRegistryClass {
  private registry = new Map<DimensionType, import('./types').DimensionComponent>();

  register<T>(registration: DimensionRegistration<T>): void {
    this.registry.set(registration.type, registration.component as import('./types').DimensionComponent);
  }

  get(type: DimensionType): import('./types').DimensionComponent | undefined {
    return this.registry.get(type);
  }

  has(type: DimensionType): boolean {
    return this.registry.has(type);
  }

  getHighlightPaths(config: DimensionConfig, activeGroupId: string | null): string[] {
    const component = this.registry.get(config.type);
    if (!component?.getHighlightPaths) return [];

    return component.getHighlightPaths(config as never, activeGroupId);
  }

  getAllTypes(): DimensionType[] {
    return Array.from(this.registry.keys());
  }
}

export const DimensionRegistry = new DimensionRegistryClass();
