<template>
  <el-scrollbar class="menu-scrollbar">
    <el-menu
      class="layout-menu"
      :background-color="menuBackgroundColor"
      :text-color="menuTextColor"
      :active-text-color="menuActiveTextColor"
      :default-active="activeMenu"
      :class="{ 'is-collapse': isCollapse }"
      :collapse="isCollapse"
      :collapse-transition="false"
      :unique-opened="expandOneMenu"
    >
      <menu-item 
        v-for="(menu, index) in visibleRoutes" 
        :key="`menu-${menu.path}-${index}`" 
        :menu="menu" 
      />
    </el-menu>
  </el-scrollbar>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import MenuItem from './MenuItem.vue'

export default defineComponent({
  name: 'LayoutMenu',
  components: {
    MenuItem
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()
    
    // 状态管理
    const isCollapse = computed(() => store.state.app.isCollapse)
    const expandOneMenu = computed(() => store.state.app.expandOneMenu)
    
    // 权限相关
    const isAdmin = localStorage.getItem('isAdmin') === '1'
    const userPermissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    
    // 主题配置
    const menuBackgroundColor = computed(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--theme-menuBar') || '#2b2f3a'
    })
    
    const menuTextColor = computed(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--theme-menuBarColor') || '#eaeaea'
    })
    
    const menuActiveTextColor = computed(() => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--theme-menuBarActiveColor') || '#409eff'
    })
    
    // 过滤菜单权限
    const filterMenuByPermission = (routes: any[], parentPath = ''): void => {
      routes.forEach(route => {
        // 检查隐藏标记
        if (route.hideMenu || route.meta?.hideMenu || route.meta?.hidden) {
          route.hideMenu = true
          return
        }
        
        // 检查权限
        const fullPath = route.redirect ? route.path : `${parentPath}/${route.path}`.replace(/\/+/g, '/')
        if (!isAdmin && route.redirect && !userPermissions.includes(route.path)) {
          route.hideMenu = true
          return
        }
        
        if (!isAdmin && !route.redirect && !userPermissions.includes(fullPath)) {
          route.hideMenu = true
          return
        }
        
        // 递归处理子菜单
        if (route.children?.length) {
          filterMenuByPermission(route.children, route.path)
        }
      })
    }
    
    // 获取可见路由
    const visibleRoutes = computed(() => {
      const routes = JSON.parse(JSON.stringify(router.options.routes))
      filterMenuByPermission(routes)
      return routes.filter((route: any) => !route.hideMenu)
    })
    
    // 当前激活菜单
    const activeMenu = computed(() => {
      const { meta, path } = route
      return meta.activeMenu || path
    })
    
    return {
      isCollapse,
      expandOneMenu,
      visibleRoutes,
      activeMenu,
      menuBackgroundColor,
      menuTextColor,
      menuActiveTextColor
    }
  }
})
</script>

<style lang="scss" scoped>
// 菜单滚动容器
.menu-scrollbar {
  height: 100%;
  background-color: var(--theme-menuBar, #2b2f3a);
  
  // 滚动条样式
  :deep(.el-scrollbar__wrap) {
    overflow-x: hidden;
    overflow-y: auto;
  }
  
  :deep(.el-scrollbar__view) {
    min-height: 100%;
  }
}

// 菜单主容器
.layout-menu {
  width: 100%;
  min-height: 100%;
  border: none;
  background-color: var(--theme-menuBar, #2b2f3a);
  
  // 折叠状态
  &.is-collapse {
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      padding: 0 20px !important;
      justify-content: center;
      
      .el-icon {
        margin-right: 0 !important;
        width: 12px;
        height: 12px;
        font-size: 12px;
      }
      
      // 隐藏子菜单箭头
      .el-sub-menu__icon-arrow {
        display: none !important;
      }
      
      // 隐藏文字
      span {
        display: none;
      }
    }
    
    // 确保折叠状态下的弹出菜单正常显示
    :deep(.el-sub-menu__popup) {
      .el-menu-item,
      .el-sub-menu__title {
        padding: 0 20px !important;
        justify-content: flex-start;
        
        .el-icon {
          margin-right: 8px !important;
          width: 16px !important;
          height: 16px !important;
          font-size: 16px !important;
        }
        
        span {
          display: inline !important;
        }
      }
    }
  }
  
  // 全局菜单样式
  :deep() {
    // 菜单项基础样式
    .el-menu-item,
    .el-sub-menu {
      background-color: var(--theme-menuBar, #2b2f3a) !important;
      color: var(--theme-menuBarColor, #eaeaea) !important;
    }
    
    // 图标样式 - 展开状态使用标准尺寸
    .el-icon {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      flex-shrink: 0 !important;
      width: 16px !important;
      height: 16px !important;
      margin-right: 8px !important;
      font-size: 16px !important;
      color: inherit !important;
      
      svg {
        display: block !important;
        width: 100% !important;
        height: 100% !important;
        fill: currentColor !important;
      }
    }
    
    // 菜单项图标颜色
    .el-menu-item .el-icon,
    .el-sub-menu__title .el-icon {
      color: var(--theme-menuBarColor, #eaeaea) !important;
    }
    
    // 激活状态
    .el-menu-item.is-active,
    .el-sub-menu.is-active > .el-sub-menu__title {
      background-color: var(--theme-menuBarActiveColor, #409eff) !important;
      color: #ffffff !important;
      
      .el-icon {
        color: #ffffff !important;
      }
    }
    
    // 悬停状态
    .el-menu-item:hover,
    .el-sub-menu__title:hover {
      background-color: var(--theme-menuBar-light-1, #2f3349) !important;
    }
    
    // 子菜单样式
    .el-sub-menu {
      .el-menu-item {
        background-color: var(--theme-menuBar-light-1, #2f3349) !important;
        
        &.is-active {
          background-color: var(--theme-menuBarActiveColor, #409eff) !important;
          color: #ffffff !important;
          
          .el-icon {
            color: #ffffff !important;
          }
        }
      }
      
      // 子菜单展开箭头 - 单独控制大小为 12x12
      .el-sub-menu__icon-arrow {
        width: 12px !important;
        height: 12px !important;
        font-size: 12px !important;
        margin-left: auto !important;
      }
    }
    
    // 子菜单标题
    .el-sub-menu__title {
      color: var(--theme-menuBarColor, #eaeaea) !important;
    }
  }
}
</style>
