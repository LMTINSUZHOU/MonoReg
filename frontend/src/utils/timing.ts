export function debounce<T extends (...args: any[]) => void>(fn: T, wait = 240) {
  let timer: ReturnType<typeof setTimeout> | undefined
  return (...args: Parameters<T>) => {
    if (timer) window.clearTimeout(timer)
    timer = window.setTimeout(() => fn(...args), wait)
  }
}
