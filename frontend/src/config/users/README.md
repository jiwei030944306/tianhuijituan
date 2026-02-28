# 用户管理配置说明

## 文件结构

```
frontend/src/
├── config/
│   └── users.ts          # 用户配置文件（在此添加/修改用户）
└── stores/
    └── user.ts           # 用户状态管理（一般不需要修改）
```

## 如何添加新用户

编辑 `frontend/src/config/users.ts`，在 `USERS` 数组中添加新用户：

```typescript
{
  id: 'user-006',              // 唯一ID
  username: 'newuser',         // 登录用户名
  password: 'password123',     // 登录密码
  name: '新用户',              // 显示名称
  role: 'teacher',             // 角色: admin | teacher | student
  permissions: [...],          // 权限列表
  enabled: true,               // 是否启用
  remark: '备注信息'           // 可选备注
}
```

## 角色说明

| 角色 | 说明 | 默认权限 |
|------|------|----------|
| `admin` | 管理员 | 所有权限 |
| `teacher` | 教师 | 上传、编辑、查看 |
| `student` | 学生 | 仅查看 |

## 权限列表

### 管理员权限 (PERMISSIONS.admin)
```typescript
['all', 'upload', 'edit', 'delete', 'view', 'manage']
```

### 教师权限 (PERMISSIONS.teacher)
```typescript
['upload', 'edit', 'view']
```

### 学生权限 (PERMISSIONS.student)
```typescript
['view']
```

## 自定义权限

如果需要自定义权限，可以直接在用户的 `permissions` 数组中添加：

```typescript
{
  username: 'special',
  name: '特殊用户',
  role: 'teacher',
  permissions: ['upload', 'edit', 'view', 'custom_permission'],
  enabled: true
}
```

## 测试账号

| 用户名 | 密码 | 姓名 | 角色 |
|--------|------|------|------|
| jiwei | test123 | 籍伟 | admin |
| zhangsan | test123 | 张三 | teacher |
| lisi | test123 | 李四 | teacher |
| wangwu | test123 | 王五 | student |

## 注意事项

1. **密码安全**: 当前密码存储在前端配置中，仅用于测试。生产环境应该由后端验证。
2. **ID唯一性**: 每个用户的 `id` 必须唯一。
3. **启用状态**: 设置 `enabled: false` 可禁用账号。
4. **权限检查**: 在组件中使用 `userStore.hasPermission('permission_name')` 检查权限。
