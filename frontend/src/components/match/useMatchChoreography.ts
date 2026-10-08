import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Trạng thái trình chiếu khi tìm bãi. Timeline cố định (~4 giây),
 * chỉ bắt đầu sau khi backend trả dữ liệu. Trong lúc chờ API ở lại SEARCHING.
 */
export type MatchStageName =
  | 'searching'   // chờ dữ liệu: vị trí người dùng nhấp nháy
  | 'candidates'  // bãi ứng viên hiện lần lượt
  | 'filtering'   // bãi không phù hợp mờ đi
  | 'routing'     // tuyến vẽ dần
  | 'analyzing'   // card camera (minh hoạ)
  | 'ranking'     // tuyến tốt nhất sáng lên
  | 'result'      // danh sách Top

/** Mốc thời gian (ms) tính từ lúc dữ liệu về. */
export const MATCH_TIMELINE: { stage: MatchStageName; at: number }[] = [
  { stage: 'candidates', at: 0 },
  { stage: 'filtering', at: 900 },
  { stage: 'routing', at: 1400 },
  { stage: 'analyzing', at: 2500 },
  { stage: 'ranking', at: 3300 },
  { stage: 'result', at: 3900 },
]

export function prefersReducedMotion() {
  return typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
}

export function useMatchChoreography(dataReady: boolean) {
  const [stage, setStage] = useState<MatchStageName>('searching')
  const timers = useRef<number[]>([])

  const clear = () => { timers.current.forEach(clearTimeout); timers.current = [] }

  useEffect(() => {
    clear()
    if (!dataReady) { setStage('searching'); return }
    if (prefersReducedMotion()) { setStage('result'); return }
    MATCH_TIMELINE.forEach(({ stage: s, at }) => {
      timers.current.push(window.setTimeout(() => setStage(s), at))
    })
    return clear
  }, [dataReady])

  const skip = useCallback(() => { clear(); setStage('result') }, [])

  return { stage, skip }
}
