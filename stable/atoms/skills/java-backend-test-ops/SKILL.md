---
name: java-backend-test-ops
description: >-
  Java 后端集成测试运维方法论 — Testcontainers 资源治理（避免 InnoDB EAGAIN）、
  Spring Boot 3.x Null-Safety 规范（MockMvc @NonNull 参数）、共享测试基类变更传播。
  适用于任何 Java + Maven + Spring Boot + Testcontainers + Docker Desktop 的项目。
  触发关键词：Testcontainers、testcontainers、mysql container、docker、ryuk、EAGAIN、InnoDB、AIO、
  aio-max-nr、Spring Boot 3、MockMvc、@NonNull、APPLICATION_JSON_VALUE、共享测试基类、
  AbstractCrud、BaseIntegrationTest、变更传播、surefire。
metadata:
  version: "1.0"
  freedom_level: low
scope: base
package:
  id: java-backend-test-ops
  version: "1.0.0"
  maturity: stable
  owner: "template-maintainers"
  tags: ["java", "spring-boot", "testcontainers", "maven", "test-ops", "docker"]
platform:
  runtimes: ["cursor"]
dependencies:
  skills: []
  mcp: []
---

# Skill: Java Backend Test Ops

## 目标

为 Java 后端工程提供两类高复用度的测试运维方法论：

1. **Testcontainers 资源治理** — 避免本地 Docker Desktop 的 InnoDB AIO 槽位被留守容器耗尽，引发 `EAGAIN` 错误导致集成测试连续失败。
2. **Spring Boot 3.x Null-Safety 规范** — 处理 Spring Framework 6.1 / Boot 3.2+ 给 MockMvc API 加的 `@NonNull` 参数注解带来的告警，避免一处不慎扩散到 10+ 个测试类。

附带一节通用方法论：**共享测试基类的变更传播规则**（grep 全部继承者再动手 + 代码生成器模板同步）。

适用范围：Java 17+ / Maven / Spring Boot 3.2+ / Testcontainers / Docker Desktop（Windows / macOS / Linux）。
不适用：纯 JUnit 单元测试（无 Spring 上下文）、纯前端测试、Docker 不在 Desktop 模式（如 CI 远程 daemon）。

## 一、Spring Boot 3.x Null-Safety 规范

### 1.1 背景

Spring Framework 6.1 / Spring Boot 3.2+ 给 MockMvc API 批量加了 `@NonNull` 参数注解（如 `MockHttpServletRequestBuilder.contentType(@NonNull MediaType)`）。若项目未启用包级 `@NonNullApi`，IDE 会对每一个传入的可空表达式弹出告警。

### 1.2 错误 / 正确写法对照

| 场景 | 错误写法 | 正确写法 |
|:---|:---|:---|
| contentType | `MediaType.APPLICATION_JSON` | `MediaType.APPLICATION_JSON_VALUE` |
| 测试类级注解 | 无 | `@SuppressWarnings("null")` |

### 1.3 原理

- `MediaType.APPLICATION_JSON` 是 `MediaType` 对象（无 `@NonNull` 标注），传给 `contentType(@NonNull MediaType)` 重载会触发 IDE null-safety 告警。
- `MediaType.APPLICATION_JSON_VALUE` 是 `String` 常量 `"application/json"`，走 `contentType(String)` 重载，无此问题。
- `@SuppressWarnings("null")` 用于压制其余第三方库返回值（`String.format`、Hamcrest `Matcher` 等）与 `@NonNull` 参数之间的类型安全告警，避免一行修不完散落各处的告警海。

### 1.4 关联：共享测试基类

如果项目中有多个测试类继承自一个公共测试基类（如 `AbstractCrudControllerTest` / `BaseIntegrationTest`），改基类常量或方法签名会级联到所有子类，1 个告警瞬间扩散为 10+ 个。详见 §三的变更传播规则。

### 1.5 适用版本

- Spring Boot 3.2 ~ 3.x：本规范适用。
- Spring Boot 4.x（启用包级 `@NonNullApi` 后）：规范可能简化，请重新评估。

## 二、Testcontainers 资源治理

### 2.1 为什么会留：Testcontainers + ryuk 语义

Testcontainers 默认行为是「测试结束后停止容器，但不删除容器」，配合 ryuk 看门狗在特定情况下清理。下表列出常见触发场景：

| 触发场景 | 行为 |
|:---|:---|
| 测试 JVM **正常退出** | 容器 `Stopped` 但 **不 remove**（默认行为，Testcontainers 不主动删除）|
| 测试 JVM **崩溃 / kill -9** | ryuk 看门狗在 10s 后清理它标记的容器（`org.testcontainers.session_id` label 匹配）|
| `mvn surefire-plugin` **forkMode=once** 多测试类共享 JVM | 共享一个数据库容器，但 JVM 退出后容器仍 `Stopped` 不 remove |
| Maven Daemon / IDE 跑测试 | 同上，且 IDE 不重启时旧容器永不被清理 |

### 2.2 累积后果：AIO 槽位耗尽

每个 `Stopped` 状态的 `mysql:8.0` 容器的 InnoDB 仍然占用了 host 内核 AIO 槽位（Linux 路径 `/proc/sys/fs/aio-max-nr`），单容器初始化要 ~256 槽位。Windows Docker Desktop 默认 65536 总槽位 → **250+ 留守容器即可耗尽**。

耗尽后的典型报错：

```text
InnoDB: io_setup() failed with EAGAIN after 5 attempts.
InnoDB: You can disable Linux Native AIO by setting innodb_use_native_aio = 0 in my.cnf
```

后果：所有依赖 Testcontainers 启动数据库容器的集成测试类全部 `ExceptionInInitializerError`，需要逐个清理积压容器才能恢复。

### 2.3 清理白名单

清理前必须列出哪些容器**不能**删（项目主开发库 / 其他长期使用的命名容器），其他随机命名 mysql/postgres/redis 等都属于 Testcontainers 残留。

| 容器 | 是否保留 | 用途 |
|:---|:---:|:---|
| `<your-project-mysql>`（如 `myapp-mysql`，端口 3306）| ✅ 保留 | 项目主开发库（按本机情况扩白名单）|
| 其它命名容器（如同机器上其它项目的 named container）| ✅ 保留 | 用户态资源 |
| 随机命名 `mysql:8.0`（testcontainers 模式）| ❌ 删除 | testcontainers 残留 |
| `testcontainers-ryuk-*` | ❌ 删除 | testcontainers 看门狗，被自动重新拉起 |
| 各种 testcontainers 临时网络 | ❌ 删除 | `docker network prune -f` 清掉 |

### 2.4 PowerShell 清理函数（写进 `$PROFILE` 推荐）

```powershell
function Clear-Testcontainers {
    $keep = @('<your-named-mysql>')              # ← 按本机情况扩白名单
    $ids = docker ps -a --format '{{.ID}} {{.Names}}' |
        Where-Object { $keep -notcontains ($_ -split ' ')[1] } |
        ForEach-Object { ($_ -split ' ')[0] }
    if ($ids.Count -gt 0) {
        Write-Host "Removing $($ids.Count) containers..."
        docker rm -f $ids | Out-Null
    }
    docker network prune -f | Out-Null
    docker volume prune -f | Out-Null            # 仅清理无引用的卷；命名卷不动
    Write-Host "OK testcontainers cleanup done"
}
```

之后每次跑完集成测试只需：

```powershell
cd backend && mvn test "-Dtest=YourIntegrationTest"; Clear-Testcontainers
```

或者把它链进 maven 命令的 PowerShell 别名里（推荐）。

#### Bash 等价示例（macOS / Linux）

```bash
clear-testcontainers() {
    local keep=("<your-named-mysql>")
    local ids
    ids=$(docker ps -a --format '{{.ID}} {{.Names}}' | \
          awk -v keep="${keep[*]}" 'BEGIN{split(keep,k," "); for(i in k) m[k[i]]=1} !($2 in m) {print $1}')
    if [ -n "$ids" ]; then
        echo "Removing containers: $ids"
        docker rm -f $ids
    fi
    docker network prune -f
    docker volume prune -f
}
```

### 2.5 替代方案对比（为什么不用其它）

| 方案 | 为什么不用 |
|:---|:---|
| `docker container prune -a` | ❌ 会清掉项目主 MySQL 等所有非运行容器 |
| `docker system prune --volumes` | ❌ 会清掉项目主开发库数据卷，开发环境直接报废 |
| Testcontainers `withReuse(true)` | 部分场景可用，但若项目自定义测试基类做了共享 schema 初始化，语义可能改变；属架构改造 |
| `.testcontainers.properties` `testcontainers.reuse.enable=true` | 同上，且需要 host-level 配置 |
| 改基类加 `Runtime.addShutdownHook` 删容器 | Surefire fork 复用时反而会误删别的测试要用的容器 |

### 2.6 何时必须执行

- ✅ 跑完 **任何**用 Testcontainers 启动数据库容器的集成测试类（凡是 `@SpringBootTest` 启 web context + Testcontainers 的）
- ✅ Maven Daemon / IDE 重新跑测试前，发现 `docker ps -a` 已有 ≥ 5 个同型留守容器（如 mysql:8.0 / postgres:15）
- ⚠️ CI 环境通常每次 build 用全新 runner，容器不累积——可不执行；但本地 dev 必须执行

### 2.7 不触发的情况

- 仅跑前端测试（不依赖 Testcontainers）
- 仅跑后端单元测试（不继承任何 Testcontainers 启动型基类）
- 编译命令（`mvn compile` / `mvn test-compile`）—— 无运行时容器

## 三、共享测试基类变更传播

测试代码中常见「公共测试基类 + N 个继承子类」结构（如 `AbstractCrudControllerTest` 被 40+ 子类继承）。改基类的常量、方法签名、注解，会级联污染所有子类。

### 3.1 修改前先 grep 全部继承者

```bash
rg "extends <your-base-test-class>" <test-source-root>
```

确认影响范围后再动手。否则一个常量改名引起的告警可能从 1 个文件扩散到 10+ 个文件。

### 3.2 常量 / 方法签名 / 注解变更必须全量传播

不可只改基类不改子类。修完后再次 grep 确认无遗漏。

### 3.3 代码生成器模板同步

若项目有从 schema/yaml 自动生成测试类的脚本（如 `gen-test.js` / 自定义 mojo），变更涉及生成子类会引用的模式（如新增 import、新增 `@Override` 方法）时，必须同步更新生成器模板，否则下次重新生成会覆盖回旧模式，造成"修了又坏、坏了又修"的循环。

## 四、典型故障案例（参考事故复盘格式）

### 4.1 Testcontainers EAGAIN 事故

**场景**：跑了一个新加的集成测试类（21 个用例），全部 `ExceptionInInitializerError` 报 `InnoDB io_setup() failed with EAGAIN after 5 attempts`。

**排查**：

1. `docker ps -a | wc -l` 查容器总数 → 30+ 个 `mysql:8.0` 留守
2. 累计 InnoDB AIO 槽位占用 ≈ 30 × 256 = 7680 槽位（Windows Docker Desktop 总 65536）
3. 加上其他容器/缓存累积，到达耗尽边界

**修复**：执行 §2.4 `Clear-Testcontainers` 清掉 29 个留守容器 + `docker network prune -f`（一并回收 ~3.26GB 镜像层缓存），21 个测试一次跑过。

**根因**：测试 JVM 正常退出，容器 `Stopped` 不 remove；多次跑测试累积。

**预防**：把 `Clear-Testcontainers` 链进每次集成测试命令尾部。

### 4.2 共享基类 Null-Safety 扩散事故

**场景**：修改 `AbstractCrudControllerTest` 中某个常量后，9 个直接子类未同步引用，IDE 告警从 1 个文件扩散到 10 个文件。

**修复**：grep 所有继承者，逐个对齐常量引用；同时检查代码生成器模板（若有），避免下次生成又被覆盖回去。

**预防**：参考 §三 「修改基类前先 grep」+ 「生成器模板同步」。

## 五、来源与回链

- **抽离自**：`enterprise-soc/.cursor/skills/soc-test-ops/SKILL.md` §六「共享测试基础设施变更约束」+ §九「Testcontainers 资源治理」
- **派生原则**：`cross-project-workflow-belongs-to-leaf-node` —— 跨项目可复用的方法论应抽离到叶子节点 cursor-genesis，避免在每个项目内重复维护。
- **抽离评估**：`knowledge-graph/docs/learnings/rule-skill-phase4-extraction-assessment.md`（P4-1 PROBE 产出）
- **本 skill 不包含**：项目特有测试基类清单（`AbstractCrudControllerTest` 等命名）、项目特有事故的具体测试类名（`RefSearchApiTest` 等）、项目特有代码生成器（`gen-test.js`）。这些保留在 `soc-test-ops`（项目特化版）中。

如果你的项目也产生了同类通用方法论，欢迎通过 cursor-genesis 的 backflow 机制贡献：参见 `.knowledge/downstream/pending/README.md`。
