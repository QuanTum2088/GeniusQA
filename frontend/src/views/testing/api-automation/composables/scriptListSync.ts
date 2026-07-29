type ScriptListListener = (serviceId: number) => void

const listeners = new Set<ScriptListListener>()


export function notifyNtestScriptsChanged(serviceId: number | string | null | undefined) {
	const id = Number(serviceId || 0)
	if (!id) return
	listeners.forEach((fn) => {
		try { fn(id) } catch { /* ignore listener errors */ }
	})
}

export function onNtestScriptsChanged(listener: ScriptListListener) {
	listeners.add(listener)
	return () => { listeners.delete(listener) }
}
