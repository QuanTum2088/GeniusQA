import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { directive } from '/@/directive/index';
import other from '/@/utils/other';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import '/@/theme/index.scss';
import { initStores } from "/@/stores";
import NtestercCard from '/@/components/ntesterc/NtestercCard.vue';
import NtestercDialog from '/@/components/ntesterc/NtestercDialog.vue';
import NtestercDrawer from '/@/components/ntesterc/NtestercDrawer.vue';
import NtestercUploadImages from '/@/components/ntesterc/NtestercUploadImages.vue';
import NtestercUploadFiles from '/@/components/ntesterc/NtestercUploadFiles.vue';
import { ElMessage } from 'element-plus';

// 全局 JS 错误弹窗：所有未捕获的错误都通过 ElMessage.error 显示
window.addEventListener('error', (event) => {
	if (event.error) {
		ElMessage.error({
			message: `JS错误: ${event.error.message || '未知错误'}`,
			duration: 5000,
		});
	}
});

window.addEventListener('unhandledrejection', (event) => {
	const message = event.reason?.message || event.reason?.msg || String(event.reason) || 'Promise 未处理异常';
	ElMessage.error({
		message: `异步错误: ${message}`,
		duration: 5000,
	});
});

async function initApplication() {
	const app = createApp(App);

	const namespace = `${import.meta.env.VITE_APP_NAMESPACE}`;
	await initStores(app, { namespace })

	// 全局注册 ntesterc 组件（支持 <ntestercCard> / <NtestercCard> 等写法）
	app.component('ntestercCard', NtestercCard);
	app.component('NtestercCard', NtestercCard);
	app.component('NtestercDialog', NtestercDialog);
	app.component('NtestercDrawer', NtestercDrawer);
	app.component('NtestercUploadImages', NtestercUploadImages);
	app.component('NtestercUploadFiles', NtestercUploadFiles);

	directive(app);
	other.apiPublicAssembly(app)
	app.use(router)
	app.use(ElementPlus)
	app.mount('#app');
}

initApplication()