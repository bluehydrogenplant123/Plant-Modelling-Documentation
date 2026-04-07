# Capstone AI 开发流程（2026-03 更新）

本文档定义 AI 在 Capstone 仓库内的执行顺序、文档优先级和落地方法。

## 1. 文档优先级（强制）

### P0（最高优先级，必须先读）

1. `docs/` 下的官方文档（不含 `docs/usercustom/`）
2. `docs/usercustom/saved/` 下文档（你维护的高优先级知识）

### P1（次级参考）

1. `docs/usercustom/` 下除 `saved/` 外的文档  
   说明：这些多为 AI 生成或阶段性记录，只作为参考，不可覆盖 P0。

### P2（低优先级参考）

1. `dev-docs/`
2. `src/` 或其他目录中的零散 markdown 说明

### 冲突裁决

1. 先按 `P0 > P1 > P2` 决策。
2. 若文档与当前代码冲突，以“当前代码 + 当前测试结果”为准，并回写文档差异。
3. P1/P2 不能推翻 P0 的接口、数据结构和流程约束。

## 2. 任务开始前固定读取顺序

1. 先读 Issue 描述、验收标准、测试计划。
2. 读取相关 P0 文档：
   - `../../AI_ISSUE_MODIFICATION_GUIDELINES.md`
   - `../../CodeExplanation/` 相关文件
   - 若涉及兼容性：`../../Compatibility/COMPAT_CHECK.md` 与 `../../Compatibility/SCHEMASNAPSHOT.md`
3. 再读相关代码（接口定义、数据结构、现有测试）。
4. 最后才查看 P1/P2 参考文档，且只用于补充，不用于改写核心规则。

## 3. 融入 vibecodingcn 的可执行原则

### 3.1 胶水编程（glue coding）默认策略

1. 默认优先复用现有实现，而不是重写。
2. 新增代码优先做“适配/封装/连接”，避免写大段新业务内核。
3. 对第三方成熟实现，优先通过 wrapper/adapter 接入，不直接改上游源码。
4. 任何“从零重写”都需要给出不能复用的理由。

### 3.2 官方文档优先

1. 涉及框架、库、协议行为时，先查官方文档再写代码。
2. 项目内规则冲突时，以 Capstone 的 P0 文档优先；外部行为细节以对应官方文档优先。

### 3.3 成熟实现优先

1. 先找仓库内现有实现（同类路由、同类 slice、同类工具函数）。
2. 再找官方示例或主流成熟实现。
3. 选型前检查最小项：维护活跃度、许可证、复杂度、可测试性、与现架构兼容性。

## 4. 标准执行流程（理解 -> 计划 -> 执行 -> 验证）

1. 理解：明确边界、输入输出、不可改范围。
2. 计划：拆成小步骤，每步可验证。
3. 执行：优先最小改动，先复用后新增。
4. 验证：至少覆盖核心路径、回归路径、兼容路径。
5. 记录：把关键设计取舍和已知风险写入文档或 PR 描述。

## 5. 兼容性改动的额外约束（Issue 82/83 相关）

1. 涉及 schema/version 变更时，必须同步评估：
   - 旧版本数据是否仍可读取
   - 升级后是否生成独立实例（避免引用串联）
   - 备份数据是否可追溯且默认不参与自动更新
2. `compatibility check prompt` 可用于辅助生成兼容补丁，但前提是你已经完成目标改动并提供真实 diff。
3. 兼容性改动后必须跑一次最小回归：加载旧图、升级、保存、重新打开、重新计算。

## 6. AI 提示词模板（可直接复用）

```text
你在 Capstone 仓库执行任务，请严格遵守以下顺序：
1) 先读取 P0 文档：docs 官方文档 + docs/usercustom/saved/*
2) docs/usercustom 非 saved 文档仅作参考，不能覆盖 P0
3) 先查官方文档，再查仓库内成熟实现，再决定是否新增代码
4) 默认采用胶水编程：优先复用，最小适配，避免重写

任务：<填写任务>
验收：<填写验收标准>

输出时必须包含：
- 读取过的 P0 文档清单
- 复用了哪些现有实现
- 新增代码为什么不可避免
- 验证步骤和结果
```

## 7. 开发检查清单

### 开发前

- [ ] 已阅读 Issue 与测试计划
- [ ] 已阅读相关 P0 文档（含 `docs/usercustom/saved/`）
- [ ] 已确认改动范围仅覆盖当前 Issue
- [ ] 已评估可复用实现，形成“先复用后新增”的方案

### 开发后

- [ ] 关键路径功能可用
- [ ] 回归路径无明显退化
- [ ] 兼容路径（如旧版本升级）已验证
- [ ] 文档优先级与实际实现保持一致

## 8. 相关入口

- `../../AI_ISSUE_MODIFICATION_GUIDELINES.md`
- `../../Compatibility/COMPAT_CHECK.md`
- `../../Compatibility/SCHEMASNAPSHOT.md`
- `../../CodeExplanation/`
- `./DUMMY_SERVER_QUICKSTART.md`
- `./REAL_SERVER_QUICKSTART.md`

## 9. Database Debugging via CLI (Required for Compute/Data-Loss Bugs)

When duplicated/imported networks fail to compute, or when `compat-check`
suspects Excel/library drift, do not rely only on UI state. Verify database
state directly from CLI.

### 9.1 Quick Rule

1. Identify the change classification first:
   - `schema-only`
   - `library-additive`
   - `library-rename`
   - `library-delete`
   - `mixed`
2. If Excel/library definitions changed, run `compat-check` before release or
   shared testing.
3. Decide how old diagram data will be handled before claiming the change is
   safe:
   - additive: only explicit `library refresh` / `upgrade` should add new vars
     into persisted diagram data
   - delete / rename: keep warning, auto-unverify, and require manual
     reselection
4. Treat Excel/library edits that affect saved-diagram compatibility as a new
   compatibility version on the shared version axis, for example
   `alpha4 -> alpha5`, even when the persisted shape does not change.
5. Capture the minimum identifiers before querying:
   - `diagramId`
   - `nodeId`
   - `modelName`
   - `modelVersion`
   - affected variable names when known
6. Run a baseline DB truth check first:
   - current Postgres truth for the changed model/version
   - smallest relevant Mongo spot-check for one affected diagram/node
7. Escalate only if the classification requires it.
8. Keep Postgres truth and Mongo persisted truth separate in the report.

### 9.2 Baseline Queries

Run from `capstone/src`:

```powershell
@'
const { PrismaClient: MongoClient } = require('./generated/mongodb-client');
const { PrismaClient: PostgresClient } = require('./generated/postgres-client');
const mongo = new MongoClient();
const postgres = new PostgresClient();

(async () => {
  const [modelName, modelVersionName, diagramId, nodeId] = process.argv.slice(2);
  if (!modelName || !modelVersionName) {
    throw new Error('Usage: node script <modelName> <modelVersionName> [diagramId] [nodeId]');
  }

  const version = await postgres.modelVersion.findFirst({
    where: {
      model_version_name: modelVersionName,
      models: { model_name: modelName },
    },
    include: {
      models: { select: { model_name: true } },
      ports: { select: { id: true, port_name: true, port_var_name: true, port_location: true } },
      varNames: { select: { id: true, name: true, ports_id: true } },
    },
  });

  let mongoSummary = null;
  if (diagramId) {
    const diagram = await mongo.diagram.findUnique({
      where: { id: diagramId },
      select: { id: true, name: true, type: true, canvas: true },
    });

    const node = nodeId
      ? await mongo.node.findFirst({
          where: { diagramId, nodeId },
          select: { id: true, nodeId: true, modelVersion: true },
        })
      : null;

    mongoSummary = { diagram, node };
  }

  console.log(JSON.stringify({
    postgres: {
      foundVersion: !!version,
      modelName,
      modelVersionName,
      portCount: version?.ports?.length ?? 0,
      varNameCount: version?.varNames?.length ?? 0,
      ports: version?.ports ?? [],
      varNames: version?.varNames ?? [],
    },
    mongo: mongoSummary,
  }, null, 2));

  await mongo.$disconnect();
  await postgres.$disconnect();
})().catch(async (e) => {
  console.error(e);
  await mongo.$disconnect();
  await postgres.$disconnect();
  process.exit(1);
});
'@ | node - MIXER BASE 69b1d0e2cbde4ff9dec80f37 507f1f77bcf86cd799439011
```

Use this baseline to answer:

1. Does the current Postgres library truth match the expected change?
2. Does one saved diagram/node already disagree with that truth?
3. Is a deeper query actually necessary?

### 9.3 `library-delete` Query Pattern

Use this path when variables, ports, or versions should disappear.

Required comparison:

1. Postgres `Ports` and `VarNames` for the target model/version.
2. Mongo `Node.modelVersion.ports_var` for the affected node.
3. Mongo `TpChanges.portVarName` for the affected node.
4. Mongo `TpNodeVers` only if version names also changed or TP selection is in
   doubt.

Expected interpretation:

1. Postgres no longer contains the variable, Mongo still does:
   `diagram stale`.
2. Postgres still contains the removed variable:
   `system-db stale`.
3. Both Postgres and Mongo still contain it:
   `mixed`.

Minimal Mongo follow-up:

```powershell
@'
const { PrismaClient } = require('./generated/mongodb-client');
const db = new PrismaClient();

(async () => {
  const [diagramId, nodeId] = process.argv.slice(2);
  if (!diagramId || !nodeId) {
    throw new Error('Usage: node script <diagramId> <nodeId>');
  }

  const node = await db.node.findFirst({
    where: { diagramId, nodeId },
    select: { id: true, nodeId: true, modelVersion: true },
  });

  const tpChanges = await db.tpChanges.findMany({
    where: { diagramId, nodeId },
    select: { timePeriodId: true, portName: true, portVarName: true, portLocation: true },
  });

  const tpNodeVers = await db.tpNodeVers.findMany({
    where: { diagramId, nodeId },
    select: { timePeriodId: true, modelVersion: true, fromTp: true, toTp: true },
  });

  console.log(JSON.stringify({ node, tpChanges, tpNodeVers }, null, 2));
  await db.$disconnect();
})().catch(async (e) => {
  console.error(e);
  await db.$disconnect();
  process.exit(1);
});
'@ | node - 69b1d0e2cbde4ff9dec80f37 507f1f77bcf86cd799439011
```

### 9.4 `library-rename` Query Pattern

Use this path when old and new names may coexist.

Required comparison:

1. Postgres current names for the target model/version.
2. Mongo `Node.modelVersion.ports_var` names.
3. Mongo `TpChanges.portVarName`.
4. Mongo `TpNodeVers.modelVersion` if version labels changed.
5. Any alias-handling code in the active reader/writer path.

Expected interpretation:

1. Postgres only has new names, Mongo still has old names, and no alias exists:
   `diagram stale`.
2. Postgres has both names unexpectedly:
   `system-db stale`.
3. Alias exists but save/export/import rewrites inconsistently:
   `mixed`.

### 9.5 `mixed` Query Pattern

Use this when both persisted schema and runtime library contract changed.

Rules:

1. Keep schema evidence and library evidence separate.
2. First prove the current Postgres truth for the target model/version.
3. Then inspect only the Mongo layers touched by the risk:
   - `Node.modelVersion`
   - `TpChanges`
   - `TpNodeVers` only when version-label drift matters
   - diagram `canvas` / snapshot only when the schema side changed there
4. Do not report one generic "pollution" label when two different causes are
   present.

### 9.6 Required Comparison for Duplicate/Import Bugs

For duplicate/import bugs, compare at least:

1. Source vs duplicated/imported diagram `canvas.nodes/edges` counts.
2. Wrapper node `diagramId` and `blueprintDiagramId`.
3. Instance `parentConnections.externalPorts[*].mapped.internalNodeId`.
4. `node` table records for the instance diagram (`nodeId` existence and remapped ID match).
5. Snapshot domain data required by translation/compute path.

### 9.7 Report Format (Issue/PR)

Include:

1. Repro URL and exact IDs.
2. Classification used: `schema-only`, `library-additive`, `library-rename`,
   `library-delete`, or `mixed`.
3. CLI query output summary:
   - Postgres truth
   - Mongo truth
   - smallest mismatch only
4. Root-cause hypothesis.
5. Fix diff and regression test scope.
