type DbListListener = () => void

const listeners = new Set<DbListListener>()


export function notifyDbListChanged() {
	listeners.forEach((fn) => {
		try { fn() } catch { /* ignore listener errors */ }
	})
}

export function onDbListChanged(listener: DbListListener) {
	listeners.add(listener)
	return () => { listeners.delete(listener) }
}
