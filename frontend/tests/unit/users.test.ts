import { describe, it, expect } from 'vitest'
import { 
  USERS, 
  validateUser, 
  findUserByUsername, 
  PERMISSIONS,
  type UserConfig 
} from '../../src/config/users'

describe('用户配置管理系统测试', () => {
  
  describe('用户配置数据完整性', () => {
    it('应该包含5个用户', () => {
      expect(USERS).toHaveLength(5)
    })

    it('所有用户应该有唯一的ID', () => {
      const ids = USERS.map(u => u.id)
      const uniqueIds = [...new Set(ids)]
      expect(uniqueIds).toHaveLength(USERS.length)
    })

    it('所有用户应该有唯一的用户名', () => {
      const usernames = USERS.map(u => u.username)
      const uniqueUsernames = [...new Set(usernames)]
      expect(uniqueUsernames).toHaveLength(USERS.length)
    })

    it('应该包含4个启用账号', () => {
      const enabledUsers = USERS.filter(u => u.enabled)
      expect(enabledUsers).toHaveLength(4)
    })

    it('应该包含1个禁用账号', () => {
      const disabledUsers = USERS.filter(u => !u.enabled)
      expect(disabledUsers).toHaveLength(1)
      expect(disabledUsers[0].username).toBe('guest')
    })
  })

  describe('权限定义测试', () => {
    it('管理员应该有所有权限', () => {
      expect(PERMISSIONS.admin).toContain('all')
      expect(PERMISSIONS.admin).toContain('upload')
      expect(PERMISSIONS.admin).toContain('edit')
      expect(PERMISSIONS.admin).toContain('delete')
      expect(PERMISSIONS.admin).toContain('view')
      expect(PERMISSIONS.admin).toContain('manage')
    })

    it('教师应该有基本权限', () => {
      expect(PERMISSIONS.teacher).toContain('upload')
      expect(PERMISSIONS.teacher).toContain('edit')
      expect(PERMISSIONS.teacher).toContain('view')
      expect(PERMISSIONS.teacher).not.toContain('delete')
      expect(PERMISSIONS.teacher).not.toContain('manage')
    })

    it('学生应该只有查看权限', () => {
      expect(PERMISSIONS.student).toEqual(['view'])
    })
  })

  describe('工具函数测试', () => {
    it('findUserByUsername 应该找到存在的用户', () => {
      const user = findUserByUsername('jiwei')
      expect(user).not.toBeUndefined()
      expect(user?.name).toBe('籍伟')
    })

    it('findUserByUsername 应该返回 undefined 对于不存在的用户', () => {
      const user = findUserByUsername('nonexistent')
      expect(user).toBeUndefined()
    })

    it('validateUser 应该验证正确的密码', () => {
      const user = validateUser('jiwei', 'test123')
      expect(user).not.toBeNull()
      expect(user?.name).toBe('籍伟')
    })

    it('validateUser 应该拒绝错误的密码', () => {
      const user = validateUser('jiwei', 'wrongpassword')
      expect(user).toBeNull()
    })

    it('validateUser 应该拒绝不存在的用户', () => {
      const user = validateUser('nobody', 'anypassword')
      expect(user).toBeNull()
    })

    it('validateUser 应该拒绝禁用的用户', () => {
      const user = validateUser('guest', 'guest123')
      expect(user).toBeNull()
    })
  })

  describe('具体用户测试', () => {
    it('jiwei 应该是管理员', () => {
      const user = findUserByUsername('jiwei')
      expect(user?.role).toBe('admin')
      expect(user?.enabled).toBe(true)
      expect(user?.permissions).toEqual(PERMISSIONS.admin)
    })

    it('zhangsan 应该是教师', () => {
      const user = findUserByUsername('zhangsan')
      expect(user?.role).toBe('teacher')
      expect(user?.enabled).toBe(true)
      expect(user?.permissions).toEqual(PERMISSIONS.teacher)
    })

    it('lisi 应该是教师', () => {
      const user = findUserByUsername('lisi')
      expect(user?.role).toBe('teacher')
      expect(user?.enabled).toBe(true)
    })

    it('wangwu 应该是学生', () => {
      const user = findUserByUsername('wangwu')
      expect(user?.role).toBe('student')
      expect(user?.enabled).toBe(true)
      expect(user?.permissions).toEqual(PERMISSIONS.student)
    })

    it('guest 应该是禁用的学生', () => {
      const user = findUserByUsername('guest')
      expect(user?.role).toBe('student')
      expect(user?.enabled).toBe(false)
    })
  })

  describe('UserConfig 接口测试', () => {
    it('所有用户应该符合 UserConfig 接口', () => {
      USERS.forEach(user => {
        expect(user).toHaveProperty('id')
        expect(user).toHaveProperty('username')
        expect(user).toHaveProperty('name')
        expect(user).toHaveProperty('role')
        expect(user).toHaveProperty('permissions')
        expect(user).toHaveProperty('enabled')
        
        expect(typeof user.id).toBe('string')
        expect(typeof user.username).toBe('string')
        expect(typeof user.name).toBe('string')
        expect(['admin', 'teacher', 'student']).toContain(user.role)
        expect(Array.isArray(user.permissions)).toBe(true)
        expect(typeof user.enabled).toBe('boolean')
      })
    })
  })
})
