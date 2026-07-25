import { defineStore } from 'pinia';
import { ref } from 'vue';

/**
 * 压测定时任务状态共享 Store
 *
 * 职责：
 *   - 持有 perf 定时任务列表快照（scheduler/index.vue 在 handleQuery 后同步，零额外请求）
 *   - 提供 refresh()：场景页 onMounted 时，若 store 尚无数据则主动拉取一次
 *   - 提供 pendingRefresh / notifySchedulerRefresh()：场景页在压测结束时通知调度页刷新
 */
export const usePerfSchedulerWatcher = defineStore('perfSchedulerWatcher', () => {
    const tasks = ref<any[]>([]);
    const lastChecked = ref<number>(0);
    // 场景页压测结束时置 true，调度页 watch 到后执行单次刷新
    const pendingRefresh = ref(false);

    // 场景页调用：通知调度页需要刷新一次任务状态
    function notifySchedulerRefresh() {
        pendingRefresh.value = true;
    }

    // 由 scheduler/index.vue 在 handleQuery 完成后调用，同步最新任务列表，无额外请求
    function updateTasks(newTasks: any[]) {
        tasks.value = newTasks;
        lastChecked.value = Date.now();
    }

    // 场景页 onMounted 时，若 store 无数据（lastChecked===0）则主动拉取一次定时任务列表
    async function refresh() {
        try {
            const { usePerformanceApi } = await import('/@/api/v1/testing/performance');
            const perfApi = usePerformanceApi();
            const res = await perfApi.getSchedulerList({ page: 1, page_size: 100 });
            tasks.value = res.data?.items ?? [];
            lastChecked.value = Date.now();
        } catch {
            // 忽略错误，不影响场景页主流程
        }
    }

    return { tasks, lastChecked, pendingRefresh, notifySchedulerRefresh, updateTasks, refresh };
});