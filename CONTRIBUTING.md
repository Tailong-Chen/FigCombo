# FigCombo 项目贡献指南

## Git 提交规则

### 提交人信息
- **Name**: Tailong-Chen
- **Email**: tailong.chen@example.com

### 提交频率
**每次修改后必须提交 GitHub**，保持代码版本历史清晰。

### 提交流程

```bash
# 1. 查看修改状态
git status

# 2. 添加所有修改
git add -A

# 3. 提交（使用规范格式）
git commit -m "type: description"

# 4. 推送到 GitHub
git push origin main
```

### 提交信息规范

格式：`type: description`

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```
feat: add volcano plot type
fix: correct panel label position
docs: update README with API examples
style: format code with black
```

### 设置 Git 用户信息

```bash
git config user.name "Tailong-Chen"
git config user.email "tailong.chen@example.com"
```

## 开发流程

1. 修改代码
2. 测试功能
3. 提交到 GitHub
4. 记录变更

## 分支策略

- `main`: 主分支，稳定版本
- 所有修改直接提交到 main 分支
