# AI 开发工作流程指南

## ⚠️ 核心原则

### 1. 文档优先级（最高优先级）

**在每次 AI 开发前，必须先读取 `docs/` 目录中的相关文档。**

`docs/` 目录中的文档是**官方教程和规范**，具有最高优先级，**必须优先于** `src/` 目录下 AI 生成的 markdown 文档。

### 2. Issue 修改原则（**必须严格遵守**）

**在修改任何 Issue 时，AI 必须先阅读：**
- [`docs/AI_ISSUE_MODIFICATION_GUIDELINES.md`](./AI_ISSUE_MODIFICATION_GUIDELINES.md) - Issue 修改指南

**核心原则：**
- ✅ **只修改与当前 Issue 直接相关的内容**
- ❌ **不要修改与当前 Issue 无关的文件**，即使它们存在技术问题
- ❌ **不要因为发现其他问题而偏离 Issue 目标**

**如果发现与 Issue 无关的问题：**
1. 不要修改
2. 在回复中说明发现了问题
3. 建议在单独的 Issue 中处理

---

## 开发流程

### 步骤 1: 理解 Issue 需求

**在开始任何开发任务前，必须：**
1. 阅读 Issue 描述和测试计划
2. 明确 Issue 的目标和范围
3. 理解需要修改的功能模块
4. 识别与 Issue 相关的文件

### 步骤 2: 查阅 `docs/` 目录文档（**必需**）

**在编写代码前，必须先查阅 `docs/` 目录中的相关文档。**

#### 文档结构

```
docs/
├── CodeExplanation/          # 代码解释文档（最重要）
│   ├── subnetwork-blueprint.md
│   ├── authentication.md
│   ├── canvasSlice.md
│   └── ...
├── Design/                    # 设计文档
├── SRS/                       # 需求规格说明
└── DevelopmentPlan/           # 开发计划
```

#### 查找相关文档

根据任务类型，查找相关文档：
- **Subnetwork 开发**：`docs/CodeExplanation/subnetwork-blueprint.md`
- **认证系统**：`docs/CodeExplanation/authentication.md`
- **Canvas 状态管理**：`docs/CodeExplanation/canvasSlice.md`
- **端口变量逻辑**：`docs/CodeExplanation/portVariableDataLogic.md`
- **图表保存**：`docs/CodeExplanation/save-diagram.md`

**完整索引**：参考 [`docs/CODE_EXPLANATION_INDEX.md`](./CODE_EXPLANATION_INDEX.md)

### 步骤 3: 判断文件是否与 Issue 相关

**在修改任何文件前，必须判断：**
- ✅ 文件是否在 Issue 的测试计划中提到？
- ✅ 文件是否直接影响 Issue 要修复的功能？
- ✅ 文件是否在 Issue 相关的代码路径中？

**如果文件与 Issue 无关：**
- ❌ **不要修改**

### 步骤 4: 实现代码

**遵循原则：**
1. 遵循 `docs/` 文档中的规范
2. 使用文档中定义的数据结构
3. 实现文档中描述的工作流程
4. **只修改与 Issue 相关的文件**

### 步骤 5: 测试实现

**详细测试步骤请参考：[测试指南](./TESTING_GUIDE.md)**

测试指南包含：
- 如何启动三个终端（Django Server, Celery Worker, Main App）
- 如何验证所有服务正在运行
- 完整的测试流程
- 常见问题解答

### 步骤 6: 创建 Pull Request（**必须遵守**）

**⚠️ 重要：所有代码更改必须通过 Pull Request 流程，禁止直接 merge 到目标分支。**

#### 6.1 提交并推送代码

在 feature branch 上完成开发和测试后：

```bash
# 1. 检查当前分支状态
git status
git branch

# 2. 提交所有更改
git add .
git commit -m "描述性的提交信息"

# 3. 推送 feature branch 到远程
git push origin <feature-branch-name>
```

#### 6.2 在 GitHub 上创建 Pull Request

1. **访问仓库页面**：`https://github.com/bluehydrogenplant123/capstone`

2. **创建 PR**：
   - 点击 "Pull requests" 标签页
   - 点击 "New pull request" 按钮
   - **Base repository**: `bluehydrogenplant123/capstone`（确认是这个，不是 `bibigan/capstone`）
   - **Base branch**: 目标分支（例如 `feature/stable-version5.0` 或 `main`）
   - **Compare branch**: 你的 feature branch（例如 `dev/issue28-duplicate-import-export`）

3. **填写 PR 信息**：
   - **Title**: 清晰的标题，描述更改内容
   - **Description**: 详细描述更改、测试情况、相关 Issue
   - **Link to Issue**: 关联相关的 GitHub Issue

4. **添加 Reviewers**：添加团队成员作为 reviewer

#### 6.3 处理 PR 中的冲突（如果有）

如果 PR 显示有冲突：

```bash
# 1. 切换到 feature branch
git checkout <feature-branch-name>

# 2. 拉取最新的目标分支
git fetch origin <target-branch-name>

# 3. Merge 或 rebase 目标分支到 feature branch
git merge origin/<target-branch-name>
# 或
git rebase origin/<target-branch-name>

# 4. 解决冲突
# 编辑冲突文件，解决冲突标记

# 5. 提交解决后的更改
git add .
git commit -m "resolve conflicts with <target-branch-name>"

# 6. 推送更新
git push origin <feature-branch-name>
```

推送后，PR 会自动更新，冲突标记会消失。

#### 6.4 等待 Review 和 Approval

- **必须等待至少一名团队成员 review 和 approve**
- Review 关注点：
  - **Functionality**: 代码是否按预期工作
  - **Code Quality**: 代码是否清晰、可维护
- 根据 review 反馈进行修改（如果需要）

#### 6.5 通过 PR 界面 Merge

**⚠️ 重要：必须通过 GitHub PR 界面 merge，禁止在本地直接 merge 并推送。**

1. PR 被 approve 后，在 GitHub PR 页面点击 "Merge pull request"
2. 选择 merge 方式（通常使用 "Squash and merge" 或 "Create a merge commit"）
3. 确认 merge
4. 删除 feature branch（GitHub 会提示，建议删除以保持仓库整洁）

#### 6.6 禁止的操作

**❌ 以下操作是禁止的：**

1. **禁止直接 merge 到目标分支**：
   ```bash
   # ❌ 错误：不要这样做
   git checkout feature/stable-version5.0
   git merge dev/issue28-duplicate-import-export
   git push origin feature/stable-version5.0
   ```

2. **禁止跳过 PR 流程**：
   - 即使代码已经测试通过，也必须通过 PR 流程
   - PR 流程确保代码被 review，团队了解所有更改

3. **禁止在本地直接 merge 后推送**：
   - 所有 merge 必须通过 GitHub PR 界面完成
   - 这确保有完整的 PR 历史记录和 review 记录

---

## 文档优先级规则

### 优先级排序（从高到低）

1. **`docs/` 目录中的文档**（最高优先级）
2. **`dev-docs/` 目录中的文档**
3. **`src/` 目录下的 AI 生成的 markdown 文档**（最低优先级）

### 冲突处理

如果 `src/` 目录下的 AI 生成文档与 `docs/` 文档冲突：
- **必须遵循 `docs/` 文档**

---

## AI 开发提示词模板

在请求 AI 帮助时，使用以下模板：

```
我已经阅读了以下文档：
- Issue 描述和测试计划
- docs/CodeExplanation/[相关文档].md

根据 Issue 和文档中的规范，我需要实现 [任务描述]。

请：
1. 只修改与 Issue 相关的文件
2. 遵循 docs/ 文档中的设计规范
3. 使用文档中定义的数据结构
4. 不要修改与 Issue 无关的文件
```

---

## 检查清单

### 开发前检查清单

- [ ] 已阅读 Issue 描述和测试计划
- [ ] 已阅读 `docs/` 目录中的相关文档
- [ ] 已判断哪些文件与 Issue 相关
- [ ] 已明确只修改与 Issue 相关的文件
- [ ] 已准备好向 AI 提供上下文信息
- [ ] 已创建 feature branch（从目标分支创建）

### 测试前检查清单

- [ ] 已启动三个终端（Django Server, Celery Worker, Main App）
- [ ] 所有服务都在正常运行
- [ ] Docker 容器都在运行

**详细测试步骤请参考：[测试指南](./TESTING_GUIDE.md)**

### PR 前检查清单

- [ ] 代码已完成开发和测试
- [ ] 所有更改已提交到 feature branch
- [ ] Feature branch 已推送到远程仓库
- [ ] 已确认 PR 的目标仓库是 `bluehydrogenplant123/capstone`（不是 `bibigan/capstone`）
- [ ] 已确认 PR 的目标分支正确（例如 `feature/stable-version5.0`）
- [ ] PR 描述清晰，已关联相关 Issue
- [ ] 已添加团队成员作为 reviewer
- [ ] **确认不会在本地直接 merge 到目标分支**

---

## 相关文档

### 开发文档

- [`docs/AI_ISSUE_MODIFICATION_GUIDELINES.md`](./AI_ISSUE_MODIFICATION_GUIDELINES.md) - **Issue 修改指南（必读）**
- [`docs/CODE_EXPLANATION_INDEX.md`](./CODE_EXPLANATION_INDEX.md) - 代码解释文档索引
- `docs/CodeExplanation/` - 所有代码解释文档
- `docs/Design/` - 设计文档
- `docs/SRS/` - 需求规格说明

### 测试文档

- **[测试指南](./TESTING_GUIDE.md)** - 用户测试指南（包含三个终端启动步骤）
- **[启动指南](./STARTUP_GUIDE.md)** - 环境准备与首次/更新启动流程

---

## 注意事项

1. **严格遵循 Issue 范围**：只修改与 Issue 相关的文件
2. **不要跳过文档阅读**：即使任务看起来简单，也可能有重要的设计细节
3. **文档是权威来源**：`docs/` 目录中的文档是经过团队审核的官方文档
4. **发现无关问题时**：不要修改，建议在单独的 Issue 中处理
5. **必须通过 PR 流程**：所有代码更改必须通过 Pull Request，禁止直接 merge 到目标分支
6. **PR 必须被 review**：至少需要一名团队成员 review 和 approve 后才能 merge
7. **通过 PR 界面 merge**：所有 merge 必须通过 GitHub PR 界面完成，不在本地直接 merge