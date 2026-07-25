<template>
  <div class="mini-page">
    <!-- 左侧菜单树 -->
    <div class="tree-aside">
      <div class="tree-header">
        <span class="tree-title">小程序自动化</span>
        <el-tooltip content="刷新">
          <el-icon class="tree-action" @click="loadMenu"><Refresh /></el-icon>
        </el-tooltip>
      </div>
      <!-- 项目选择 -->
      <div class="tree-project-select">
        <el-select
          v-model="currentProjectId"
          placeholder="选择项目（可选）"
          clearable
          size="small"
          style="width:100%"
          @change="onProjectChange"
        >
          <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
      <div class="tree-search">
        <el-input v-model="filterText" placeholder="搜索脚本" clearable size="small" prefix-icon="Search" />
      </div>
      <el-scrollbar class="tree-scroll">
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="{ children: 'children', label: 'name' }"
          :filter-node-method="filterNode"
          node-key="id"
          highlight-current
          @node-click="onNodeClick"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-icon class="node-icon">
                <Folder v-if="data.type === 0" />
                <FolderOpened v-else-if="data.type === 1" />
                <Document v-else />
              </el-icon>
              <span class="node-label">{{ data.name }}</span>
              <el-dropdown trigger="click" @command="(cmd: string) => onNodeCmd(cmd, data)" @click.stop>
                <el-icon class="node-more"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="add" :disabled="data.type === 2">
                      <el-icon><Plus /></el-icon> 新增子节点
                    </el-dropdown-item>
                    <el-dropdown-item command="rename"><el-icon><Edit /></el-icon> 重命名</el-dropdown-item>
                    <el-dropdown-item command="copy" :disabled="data.type !== 2">
                      <el-icon><CopyDocument /></el-icon> 复制脚本
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided><el-icon><Delete /></el-icon> 删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-tree>
      </el-scrollbar>
      <div class="tree-footer">
        <el-button size="small" type="primary" plain @click="showAddRoot = true">
          <el-icon><Plus /></el-icon> 新增根目录
        </el-button>
      </div>
    </div>

    <!-- 右侧内容区 -->
    <div class="content-area">
      <div v-if="!currentNode" class="empty-state">
        <el-empty description="请从左侧选择脚本节点" :image-size="120" />
      </div>

      <template v-else>
        <!-- 编辑器头部 -->
        <div class="editor-header">
          <div class="editor-title">
            <el-icon><Document /></el-icon>
            <span>{{ currentNode.name }}</span>
          </div>
          <div class="editor-actions">
            <!-- 平台选择 -->
            <el-select v-model="scriptForm.platform" size="small" style="width:110px"
              placeholder="平台" @change="onPlatformChange">
              <el-option v-for="(fws, p) in platforms" :key="p" :label="platformLabels[p] || p" :value="p" />
            </el-select>
            <!-- 框架选择 -->
            <el-select v-model="scriptForm.framework" size="small" style="width:120px" placeholder="框架">
              <el-option v-for="f in currentFrameworks" :key="f" :label="f" :value="f" />
            </el-select>
            <el-button size="small" @click="showConfigDialog = true">
              <el-icon><Setting /></el-icon> 平台配置
            </el-button>
            <el-button size="small" type="primary" @click="saveScript">
              <el-icon><Check /></el-icon> 保存
            </el-button>
            <el-button size="small" type="success" @click="openRunDialog">
              <el-icon><VideoPlay /></el-icon> 执行
            </el-button>
          </div>
        </div>

        <!-- 步骤列表 -->
        <div class="steps-area">
          <div class="steps-toolbar">
            <span class="steps-count">共 {{ scriptForm.script.length }} 个步骤</span>
            <el-dropdown @command="addStep">
              <el-button size="small" type="primary" plain>
                <el-icon><Plus /></el-icon> 添加步骤
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="t in stepTypes" :key="t.type" :command="t.type">
                    {{ t.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <el-scrollbar class="steps-scroll">
            <div v-if="!scriptForm.script.length" class="steps-empty">
              <el-empty description="暂无步骤，点击「添加步骤」开始编写" :image-size="80" />
            </div>
            <div
              v-for="(step, idx) in scriptForm.script"
              :key="idx"
              class="step-card"
              :class="{ 'step-active': activeStepIdx === idx }"
              @click="activeStepIdx = idx"
            >
              <div class="step-card-header">
                <div class="step-index">{{ idx + 1 }}</div>
                <el-tag size="small" :type="getStepTagType(step.type)" effect="light">
                  {{ getStepLabel(step.type) }}
                </el-tag>
                <el-input v-model="step.name" size="small" placeholder="步骤名称"
                  style="flex:1;margin:0 8px" />
                <el-icon class="step-del" @click.stop="removeStep(idx)"><Delete /></el-icon>
              </div>

              <div v-if="activeStepIdx === idx" class="step-card-body">
                <!-- 启动 type=0 -->
                <template v-if="step.type === 0">
                  <el-alert type="info" :closable="false" show-icon
                    :description="`将使用 ${scriptForm.framework} 框架启动 ${platformLabels[scriptForm.platform] || scriptForm.platform} 小程序`"
                    style="margin-bottom:8px" />
                </template>
                <!-- 导航 type=1 -->
                <template v-else-if="step.type === 1">
                  <el-form-item label="页面路径">
                    <el-input v-model="step.page_path" placeholder="如 /pages/index/index" />
                  </el-form-item>
                </template>
                <!-- 点击/输入/获取文本 type=2/3/4 -->
                <template v-else-if="[2,3,4].includes(step.type)">
                  <el-form-item label="选择器类型">
                    <el-select v-model="step.selector_type" style="width:140px">
                      <el-option label="CSS选择器" value="css" />
                      <el-option label="XPath" value="xpath" />
                      <el-option label="accessibility_id" value="accessibility_id" />
                      <el-option label="ID" value="id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="选择器">
                    <el-input v-model="step.selector" placeholder="元素选择器" />
                  </el-form-item>
                  <el-form-item v-if="step.type === 3" label="输入内容">
                    <el-input v-model="step.value" placeholder="要输入的文本" />
                  </el-form-item>
                  <el-form-item v-if="step.type === 4" label="断言文本">
                    <el-input v-model="step.assert_text" placeholder="期望包含的文本" />
                  </el-form-item>
                </template>
                <!-- 图像断言 type=5 -->
                <template v-else-if="step.type === 5">
                  <el-form-item label="模板图像路径">
                    <el-input v-model="step.assert_img" placeholder="服务器上的图像绝对路径" />
                  </el-form-item>
                </template>
                <!-- 等待 type=6 -->
                <template v-else-if="step.type === 6">
                  <el-form-item label="等待时间(秒)">
                    <el-input-number v-model="step.value" :min="0.1" :step="0.5" :precision="1" />
                  </el-form-item>
                </template>
                <!-- 调用API type=7 -->
                <template v-else-if="step.type === 7">
                  <el-form-item label="API名称">
                    <el-input v-model="step.api_name" placeholder="如 getSystemInfo" />
                  </el-form-item>
                  <el-form-item label="参数(JSON)">
                    <el-input v-model="step.api_params_str" type="textarea" :rows="2"
                      placeholder='{"key": "value"}' @blur="parseApiParams(step)" />
                  </el-form-item>
                </template>
                <!-- 执行JS type=8 -->
                <template v-else-if="step.type === 8">
                  <el-form-item label="JS代码">
                    <el-input v-model="step.js_code" type="textarea" :rows="3"
                      placeholder="document.title 或 wx.getSystemInfo({})" />
                  </el-form-item>
                </template>
                <!-- 滑动 type=9 -->
                <template v-else-if="step.type === 9">
                  <el-form-item label="滑动方向">
                    <el-radio-group v-model="step.direction">
                      <el-radio value="up">向上</el-radio>
                      <el-radio value="down">向下</el-radio>
                      <el-radio value="left">向左</el-radio>
                      <el-radio value="right">向右</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="滑动距离(px)">
                    <el-input-number v-model="step.distance" :min="50" :step="50" />
                  </el-form-item>
                </template>

                <!-- 通用等待 -->
                <el-form-item v-if="![6,10].includes(step.type)" label="步骤后等待(秒)">
                  <el-input-number v-model="step.wait" :min="0" :step="0.5" :precision="1" style="width:120px" />
                </el-form-item>
              </div>
            </div>
          </el-scrollbar>
        </div>
      </template>
    </div>

    <!-- 新增节点对话框 -->
    <el-dialog v-model="showAddDialog" :title="addDialogTitle" width="400px" destroy-on-close>
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="addForm.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="addForm.type">
            <el-radio :value="0">目录</el-radio>
            <el-radio :value="1">脚本组</el-radio>
            <el-radio :value="2">脚本</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAdd">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog v-model="showRenameDialog" title="重命名" width="360px" destroy-on-close>
      <el-input v-model="renameValue" placeholder="请输入新名称" />
      <template #footer>
        <el-button @click="showRenameDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>

    <!-- 平台配置对话框 -->
    <el-dialog v-model="showConfigDialog" title="平台配置" width="560px" destroy-on-close>
      <el-alert type="info" :closable="false" show-icon style="margin-bottom:16px"
        :description="`当前平台：${platformLabels[scriptForm.platform] || scriptForm.platform}，框架：${scriptForm.framework}`" />
      <el-form :model="scriptForm.platform_config" label-width="130px">
        <!-- minium 配置 -->
        <template v-if="scriptForm.framework === 'minium'">
          <el-form-item label="开发者工具路径">
            <el-input v-model="scriptForm.platform_config.dev_tool_path"
              placeholder="微信开发者工具可执行文件路径" />
          </el-form-item>
          <el-form-item label="小程序项目路径">
            <el-input v-model="scriptForm.platform_config.project_path"
              placeholder="小程序项目目录" />
          </el-form-item>
          <el-form-item label="AppID">
            <el-input v-model="scriptForm.platform_config.appid" placeholder="小程序 AppID（可选）" />
          </el-form-item>
          <el-form-item label="运行平台">
            <el-select v-model="scriptForm.platform_config.platform" style="width:100%">
              <el-option label="模拟器(ide)" value="ide" />
              <el-option label="Android" value="android" />
              <el-option label="iOS" value="ios" />
            </el-select>
          </el-form-item>
        </template>
        <!-- appium 配置 -->
        <template v-else-if="scriptForm.framework === 'appium'">
          <el-form-item label="Appium 服务地址">
            <el-input v-model="scriptForm.platform_config.appium_server"
              placeholder="http://127.0.0.1:4723" />
          </el-form-item>
          <el-form-item label="设备ID">
            <el-input v-model="scriptForm.platform_config.device_id"
              placeholder="adb devices 中的序列号" />
          </el-form-item>
          <el-form-item label="系统类型">
            <el-select v-model="scriptForm.platform_config.platform_name" style="width:100%">
              <el-option label="Android" value="Android" />
              <el-option label="iOS" value="iOS" />
            </el-select>
          </el-form-item>
          <el-form-item label="宿主App包名">
            <el-input v-model="scriptForm.platform_config.app_package"
              :placeholder="platformPackagePlaceholder" />
          </el-form-item>
        </template>
        <!-- playwright 配置 -->
        <template v-else-if="scriptForm.framework === 'playwright'">
          <el-form-item label="浏览器类型">
            <el-select v-model="scriptForm.platform_config.browser" style="width:100%">
              <el-option label="Chromium" value="chromium" />
              <el-option label="WebKit" value="webkit" />
              <el-option label="Firefox" value="firefox" />
            </el-select>
          </el-form-item>
          <el-form-item label="小程序入口URL">
            <el-input v-model="scriptForm.platform_config.mini_url"
              placeholder="H5小程序入口地址" />
          </el-form-item>
          <el-form-item label="无头模式">
            <el-switch v-model="scriptForm.platform_config.headless" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="showConfigDialog = false; saveScript()">保存配置</el-button>
      </template>
    </el-dialog>

    <!-- 执行对话框 -->
    <el-dialog v-model="showRunDialog" title="执行配置" width="480px" destroy-on-close>
      <el-form :model="runForm" label-width="90px">
        <el-form-item label="任务名称">
          <el-input v-model="runForm.task_name" placeholder="可选" />
        </el-form-item>
        <el-form-item label="平台">
          <el-select v-model="runForm.platform" style="width:100%">
            <el-option v-for="(fws, p) in platforms" :key="p" :label="platformLabels[p] || p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="框架">
          <el-select v-model="runForm.framework" style="width:100%">
            <el-option v-for="f in currentFrameworks" :key="f" :label="f" :value="f" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRunDialog = false">取消</el-button>
        <el-button type="success" :loading="running" @click="confirmRun">
          <el-icon><VideoPlay /></el-icon> 开始执行
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行结果抽屉 -->
    <el-drawer v-model="showResultDrawer" title="执行结果" direction="rtl" size="520px" destroy-on-close>
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between;width:100%">
          <span style="font-weight:600">执行结果</span>
          <el-tag :type="resultRunning ? 'warning' : 'success'" effect="light">
            {{ resultRunning ? '执行中...' : '已完成' }}
          </el-tag>
        </div>
      </template>

      <div class="result-summary" v-if="resultSummary">
        <div class="summary-item"><div class="sv">{{ resultSummary.total }}</div><div class="sl">总步骤</div></div>
        <div class="summary-item pass"><div class="sv">{{ resultSummary.passed }}</div><div class="sl">通过</div></div>
        <div class="summary-item fail"><div class="sv">{{ resultSummary.fail }}</div><div class="sl">失败</div></div>
        <div class="summary-item rate"><div class="sv">{{ resultSummary.percent }}%</div><div class="sl">通过率</div></div>
      </div>
      <el-progress v-if="resultSummary" :percentage="resultSummary.percent"
        :color="[{color:'#f56c6c',percentage:99.99},{color:'#67c23a',percentage:100}]"
        :stroke-width="8" :show-text="false" style="margin-bottom:16px" />

      <el-timeline>
        <el-timeline-item
          v-for="(item, i) in resultSteps"
          :key="i"
          :type="item.status === 1 ? 'success' : item.status === 0 ? 'danger' : 'primary'"
          :timestamp="item.create_time"
          placement="top"
        >
          <div style="display:flex;align-items:center;gap:6px">
            <el-icon :style="{ color: item.status === 1 ? '#67c23a' : item.status === 0 ? '#f56c6c' : '#409eff' }">
              <Check v-if="item.status === 1" /><Close v-else-if="item.status === 0" /><Timer v-else />
            </el-icon>
            <span style="font-size:13px;font-weight:500">{{ item.name }}</span>
          </div>
          <div v-if="item.log" style="font-size:12px;color:var(--el-text-color-secondary);margin-top:4px;padding-left:20px">
            {{ item.log }}
          </div>
          <div v-if="item.before_img || item.after_img" style="display:flex;margin-top:8px;padding-left:20px;gap:8px">
            <el-image v-if="item.before_img" :src="item.before_img" :preview-src-list="[item.before_img]"
              fit="cover" style="width:100px;height:70px;border-radius:4px" />
            <el-image v-if="item.after_img" :src="item.after_img" :preview-src-list="[item.after_img]"
              fit="cover" style="width:100px;height:70px;border-radius:4px" />
          </div>
        </el-timeline-item>
      </el-timeline>

      <template #footer>
        <el-button v-if="resultRunning" type="danger" @click="stopCurrentRun">停止执行</el-button>
        <el-button @click="showResultDrawer = false">关闭</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Refresh, Folder, FolderOpened, Document, MoreFilled, Plus, Edit, Delete,
  Check, Close, VideoPlay, ArrowDown, Setting, Timer, CopyDocument,
} from '@element-plus/icons-vue';
import { useMiniAutomationApi } from '/@/api/v1/testing/miniprogramAutomation';
import { getProjectList } from '/@/api/v1/projects/project';

const api = useMiniAutomationApi();

// ── 项目选择 ──────────────────────────────────────────────
const projectList = ref<any[]>([]);
const currentProjectId = ref<number | null>(null);

const loadProjects = async () => {
  try {
    const res: any = await getProjectList({ page: 1, page_size: 100 });
    projectList.value = res.data?.content || res.data?.items || res.data || [];
  } catch { projectList.value = []; }
};

const onProjectChange = () => {
  currentNode.value = null;
  loadMenu();
};

// ── 平台/框架元数据 ───────────────────────────────────────
const platforms = ref<Record<string, string[]>>({
  wechat: ['minium', 'appium'],
  alipay: ['appium', 'playwright'],
  douyin: ['appium'],
  baidu:  ['appium'],
  generic: ['appium', 'playwright'],
});
const platformLabels: Record<string, string> = {
  wechat: '微信小程序', alipay: '支付宝小程序',
  douyin: '抖音小程序', baidu: '百度小程序', generic: '通用',
};
const platformPackagePlaceholder = computed(() => {
  const map: Record<string, string> = {
    wechat: 'com.tencent.mm', alipay: 'com.eg.android.AlipayGphone',
    douyin: 'com.ss.android.ugc.aweme', baidu: 'com.baidu.searchbox',
  };
  return map[scriptForm.value.platform] || '宿主App包名';
});

const loadMeta = async () => {
  const res: any = await api.get_platforms();
  if (res.data) platforms.value = res.data;
};

const currentFrameworks = computed(() =>
  platforms.value[scriptForm.value.platform] || ['appium']
);

const onPlatformChange = () => {
  const fws = currentFrameworks.value;
  if (!fws.includes(scriptForm.value.framework)) {
    scriptForm.value.framework = fws[0];
  }
};

// ── 菜单树 ────────────────────────────────────────────────
const treeRef = ref();
const treeData = ref<any[]>([]);
const filterText = ref('');
const currentNode = ref<any>(null);

watch(filterText, v => treeRef.value?.filter(v));
const filterNode = (val: string, data: any) => !val || data.name.includes(val);

const loadMenu = async () => {
  const res: any = await api.get_menu({ project_id: currentProjectId.value || undefined });
  treeData.value = res.data || [];
};

const onNodeClick = async (data: any) => {
  if (data.type !== 2) return;
  currentNode.value = data;
  await loadScript(data.id);
};

// ── 脚本编辑 ──────────────────────────────────────────────
const scriptForm = ref<{
  platform: string; framework: string;
  script: any[]; platform_config: Record<string, any>;
}>({
  platform: 'wechat', framework: 'minium',
  script: [], platform_config: {},
});
const activeStepIdx = ref<number | null>(null);

const loadScript = async (menuId: number) => {
  const res: any = await api.get_script({ id: menuId });
  scriptForm.value = {
    platform: res.data?.platform || 'wechat',
    framework: res.data?.framework || 'minium',
    script: res.data?.script || [],
    platform_config: res.data?.platform_config || {},
  };
  activeStepIdx.value = null;
};

const saveScript = async () => {
  if (!currentNode.value) return;
  await api.save_script({
    id: currentNode.value.id,
    platform: scriptForm.value.platform,
    framework: scriptForm.value.framework,
    script: scriptForm.value.script,
    platform_config: scriptForm.value.platform_config,
  });
  ElMessage.success('保存成功');
};

// ── 步骤类型 ──────────────────────────────────────────────
const stepTypes = [
  { type: 0,  label: '启动小程序' },
  { type: 1,  label: '导航到页面' },
  { type: 2,  label: '点击元素' },
  { type: 3,  label: '输入文本' },
  { type: 4,  label: '获取文本(断言)' },
  { type: 5,  label: '图像断言' },
  { type: 6,  label: '等待' },
  { type: 7,  label: '调用小程序API' },
  { type: 8,  label: '执行JS' },
  { type: 9,  label: '滑动' },
  { type: 10, label: '关闭小程序' },
];
const stepTagTypes: Record<number, string> = {
  0: 'success', 1: 'primary', 2: '', 3: 'warning',
  4: 'info', 5: 'danger', 6: 'info', 7: '', 8: '', 9: 'primary', 10: 'danger',
};
const getStepLabel = (type: number) => stepTypes.find(t => t.type === type)?.label || '未知';
const getStepTagType = (type: number) => stepTagTypes[type] || '';

const addStep = (type: number) => {
  scriptForm.value.script.push({
    name: getStepLabel(type), type,
    selector: '', selector_type: 'css',
    value: type === 6 ? 1 : '',
    page_path: '', api_name: '', api_params: null, api_params_str: '',
    js_code: '', assert_text: '', assert_img: '',
    direction: 'down', distance: 300, wait: 0.5,
  });
  activeStepIdx.value = scriptForm.value.script.length - 1;
};

const removeStep = (idx: number) => {
  scriptForm.value.script.splice(idx, 1);
  if (activeStepIdx.value === idx) activeStepIdx.value = null;
};

const parseApiParams = (step: any) => {
  try {
    step.api_params = JSON.parse(step.api_params_str || '{}');
  } catch {
    step.api_params = {};
  }
};

// ── 菜单操作 ──────────────────────────────────────────────
const showAddDialog = ref(false);
const showAddRoot = ref(false);
const addDialogTitle = ref('新增节点');
const addForm = ref({ name: '', type: 0, pid: 0 });
const showRenameDialog = ref(false);
const renameValue = ref('');
const renameTarget = ref<any>(null);
const showConfigDialog = ref(false);

const onNodeCmd = (cmd: string, data: any) => {
  if (cmd === 'add') {
    addForm.value = { name: '', type: 0, pid: data.id, project_id: currentProjectId.value };
    addDialogTitle.value = `在「${data.name}」下新增`;
    showAddDialog.value = true;
  } else if (cmd === 'rename') {
    renameTarget.value = data;
    renameValue.value = data.name;
    showRenameDialog.value = true;
  } else if (cmd === 'copy') {
    ElMessageBox.prompt('请输入复制后的脚本名称', '复制脚本', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: `${data.name}_copy`,
      inputValidator: (v) => !!v?.trim() || '名称不能为空',
    }).then(async ({ value }) => {
      await api.copy_script({ id: data.id, name: value.trim() });
      ElMessage.success('复制成功');
      await loadMenu();
    });
  } else if (cmd === 'delete') {
    ElMessageBox.confirm(`确认删除「${data.name}」？`, '提示', { type: 'warning' })
      .then(async () => {
        await api.del_menu({ id: data.id });
        ElMessage.success('删除成功');
        await loadMenu();
        if (currentNode.value?.id === data.id) currentNode.value = null;
      });
  }
};

watch(showAddRoot, v => {
  if (v) {
    addForm.value = { name: '', type: 0, pid: 0, project_id: currentProjectId.value };
    addDialogTitle.value = '新增根节点';
    showAddDialog.value = true;
    showAddRoot.value = false;
  }
});

const confirmAdd = async () => {
  if (!addForm.value.name.trim()) return ElMessage.warning('请输入名称');
  await api.add_menu(addForm.value);
  ElMessage.success('新增成功');
  showAddDialog.value = false;
  await loadMenu();
};

const confirmRename = async () => {
  if (!renameValue.value.trim()) return ElMessage.warning('请输入名称');
  await api.rename_menu({ id: renameTarget.value.id, name: renameValue.value });
  ElMessage.success('重命名成功');
  showRenameDialog.value = false;
  await loadMenu();
};

// ── 执行 ──────────────────────────────────────────────────
const showRunDialog = ref(false);
const running = ref(false);
const runForm = ref({ task_name: '', platform: 'wechat', framework: 'minium' });

const openRunDialog = () => {
  runForm.value.platform = scriptForm.value.platform;
  runForm.value.framework = scriptForm.value.framework;
  runForm.value.task_name = currentNode.value?.name || '';
  showRunDialog.value = true;
};

const currentResultId = ref('');
const showResultDrawer = ref(false);
const resultRunning = ref(false);
const resultSteps = ref<any[]>([]);
const resultSummary = ref<any>(null);
let pollTimer: any = null;

const confirmRun = async () => {
  running.value = true;
  try {
    const res: any = await api.run_script({
      id: currentNode.value.id,
      task_name: runForm.value.task_name,
      platform: runForm.value.platform,
      framework: runForm.value.framework,
      platform_config: scriptForm.value.platform_config,
      project_id: currentProjectId.value || undefined,
    });
    currentResultId.value = res.data.result_id;
    showRunDialog.value = false;
    showResultDrawer.value = true;
    resultRunning.value = true;
    resultSteps.value = [];
    resultSummary.value = null;
    startPoll();
  } finally {
    running.value = false;
  }
};

let _pollInterval = 2000;

const startPoll = () => {
  stopPoll();
  _pollInterval = 2000;
  _schedulePoll();
};

const _schedulePoll = () => {
  pollTimer = setTimeout(async () => {
    await pollResult();
    if (resultRunning.value) {
      _pollInterval = Math.min(_pollInterval + 500, 5000);
      _schedulePoll();
    }
  }, _pollInterval);
};

const stopPoll = () => {
  if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
};

const pollResult = async () => {
  try {
    const statusRes: any = await api.run_status({ result_id: currentResultId.value });
    if (!statusRes.data?.is_running) {
      resultRunning.value = false;
      stopPoll();
    }
  } catch { /* 忽略 */ }

  const res: any = await api.result_detail({ result_id: currentResultId.value });
  resultSteps.value = res.data || [];
  const steps = resultSteps.value.filter((s: any) => !['开始执行', '执行结束', '执行异常'].includes(s.name));
  const passed = steps.filter((s: any) => s.status === 1).length;
  const fail = steps.filter((s: any) => s.status === 0).length;
  const total = steps.length;
  resultSummary.value = { total, passed, fail, percent: total > 0 ? Math.round(passed / total * 100) : 0 };
  const last = resultSteps.value[resultSteps.value.length - 1];
  if (last && ['执行结束', '执行异常'].includes(last.name)) {
    resultRunning.value = false;
    stopPoll();
  }
};

const stopCurrentRun = async () => {
  await api.stop_script({ result_id: currentResultId.value });
  resultRunning.value = false;
  stopPoll();
  ElMessage.success('已停止');
};

onMounted(async () => {
  await Promise.all([loadMenu(), loadMeta(), loadProjects()]);
});
onUnmounted(() => stopPoll());
</script>

<style scoped lang="scss">
.mini-page {
  display: flex;
  height: calc(100vh - 100px);
  background: var(--el-bg-color-page);
}

.tree-aside {
  width: 260px;
  flex-shrink: 0;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
}
.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.tree-title { font-size: 14px; font-weight: 600; color: var(--el-text-color-primary); }
.tree-action { cursor: pointer; color: var(--el-text-color-secondary); &:hover { color: var(--el-color-primary); } }
.tree-search { padding: 10px 12px; }
.tree-project-select { padding: 0 12px 10px; }
.tree-scroll { flex: 1; padding: 4px 8px; }
.tree-footer { padding: 10px 12px; border-top: 1px solid var(--el-border-color-lighter); }

.tree-node {
  display: flex; align-items: center; gap: 6px; width: 100%;
  .node-icon { font-size: 14px; color: var(--el-text-color-secondary); flex-shrink: 0; }
  .node-label { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .node-more { opacity: 0; cursor: pointer; color: var(--el-text-color-secondary); flex-shrink: 0; }
  &:hover .node-more { opacity: 1; }
}

.content-area {
  flex: 1; min-width: 0; display: flex; flex-direction: column; overflow: hidden;
}
.empty-state {
  flex: 1; display: flex; align-items: center; justify-content: center;
}
.editor-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px; background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter); gap: 12px;
}
.editor-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; color: var(--el-text-color-primary);
}
.editor-actions { display: flex; align-items: center; gap: 8px; }

.steps-area {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
  padding: 16px 20px; gap: 12px;
}
.steps-toolbar { display: flex; align-items: center; justify-content: space-between; }
.steps-count { font-size: 13px; color: var(--el-text-color-secondary); }
.steps-scroll { flex: 1; }
.steps-empty { padding: 40px 0; }

.step-card {
  background: var(--el-bg-color); border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px; margin-bottom: 8px; cursor: pointer; transition: border-color 0.2s;
  &:hover { border-color: var(--el-color-primary-light-5); }
  &.step-active { border-color: var(--el-color-primary); }
}
.step-card-header {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
}
.step-index {
  width: 22px; height: 22px; border-radius: 50%; background: var(--el-fill-color);
  color: var(--el-text-color-secondary); font-size: 11px; font-weight: 600;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-del {
  cursor: pointer; color: var(--el-text-color-placeholder);
  &:hover { color: var(--el-color-danger); }
}
.step-card-body {
  padding: 12px 14px; border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter); border-radius: 0 0 8px 8px;
  :deep(.el-form-item) { margin-bottom: 10px; }
  :deep(.el-form-item__label) { font-size: 12px; }
}

.result-summary {
  display: flex; gap: 12px; margin-bottom: 14px;
  .summary-item {
    flex: 1; text-align: center; background: var(--el-fill-color-light);
    border-radius: 8px; padding: 10px 6px;
    .sv { font-size: 22px; font-weight: 700; color: var(--el-text-color-primary); }
    .sl { font-size: 11px; color: var(--el-text-color-secondary); margin-top: 2px; }
    &.pass .sv { color: #67c23a; }
    &.fail .sv { color: #f56c6c; }
    &.rate .sv { color: var(--el-color-primary); }
  }
}
</style>
