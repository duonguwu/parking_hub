import { useState, useEffect } from 'react'
import { Star, CheckCircle2, Info, Timer, Droplets, UserSearch, Car, Zap, Truck, AlertTriangle, Edit2, MoreVertical, Check, X } from 'lucide-react'
import { garageApi } from '@/services/api'
import { BOOKING_STATUS_MAP } from '@/services/api'

export function GarageDashboard() {
  const [data, setData] = useState<any>(null)
  const [capacity, setCapacity] = useState<any>(null)
  const [queue, setQueue] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      garageApi.dashboardOverview(),
      garageApi.dashboardCapacity('24H'),
      garageApi.queue('all', 1, 3) // Get top 3 bookings for dashboard
    ]).then(([overviewRes, capacityRes, queueRes]) => {
      setData(overviewRes)
      setCapacity(capacityRes)
      setQueue(queueRes)
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [])

  if (loading || !data) {
    return (
      <div className="p-8 pb-12 max-w-[1400px] mx-auto min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-sm font-bold text-slate-400 uppercase tracking-widest">Loading Telemetry...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 pb-12 max-w-[1400px] mx-auto space-y-12">
      {/* Header Section */}
      <div className="flex justify-between items-end">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.2em] text-blue-500 font-bold">Operations Overview</p>
          <h1 className="text-4xl font-black text-slate-900 tracking-tighter">Daily Performance</h1>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs uppercase tracking-widest text-slate-400 font-bold">Status:</span>
          <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold border border-emerald-200 flex items-center gap-2 shadow-sm uppercase">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
            {data.status || 'LIVE'}
          </span>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* KPI 1 */}
        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm space-y-4 hover:border-blue-200 transition-colors">
          <p className="text-xs uppercase tracking-widest text-slate-500 font-bold">Today's Cars</p>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl md:text-[3.5rem] font-black tracking-tighter leading-none text-slate-900">{data.kpis.todays_cars.value}</span>
            <span className="text-blue-500 font-bold text-sm">{data.kpis.todays_cars.trend}</span>
          </div>
          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${data.kpis.todays_cars.capacity_percent}%` }}></div>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm space-y-4 hover:border-blue-200 transition-colors">
          <p className="text-xs uppercase tracking-widest text-slate-500 font-bold">Revenue</p>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl md:text-[3.5rem] font-black tracking-tighter leading-none text-slate-900">${(data.kpis.revenue.value / 1000).toFixed(1)}k</span>
            <span className="text-emerald-500 font-bold text-sm uppercase">{data.kpis.revenue.trend}</span>
          </div>
          <div className="flex items-end gap-1 h-5">
            {data.kpis.revenue.sparkline?.map((h: number, i: number) => (
              <div key={i} className={`w-2 rounded-sm ${i >= 3 ? 'bg-blue-600' : 'bg-blue-200'}`} style={{ height: `${h}%` }}></div>
            ))}
          </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm space-y-4 hover:border-blue-200 transition-colors">
          <p className="text-xs uppercase tracking-widest text-slate-500 font-bold">Current Score</p>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl md:text-[3.5rem] font-black tracking-tighter leading-none text-slate-900">{data.kpis.match_score.value?.toFixed(1) || 'N/A'}</span>
            <Star className="w-8 h-8 text-amber-400 fill-amber-400 shrink-0" />
          </div>
          <p className="text-xs text-slate-400 font-medium">Based on {data.kpis.match_score.total_reviews} reviews today</p>
        </div>

        {/* KPI 4 */}
        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm space-y-4 hover:border-blue-200 transition-colors">
          <p className="text-xs uppercase tracking-widest text-slate-500 font-bold">Fill Rate</p>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl md:text-[3.5rem] font-black tracking-tighter leading-none text-slate-900">{data.kpis.fill_rate.value}%</span>
            <CheckCircle2 className="w-8 h-8 text-emerald-500 shrink-0" />
          </div>
          <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold">
            <span>CAPACITY REMAINING: {data.kpis.fill_rate.remaining_capacity}%</span>
          </div>
        </div>
      </div>

      {/* Main Area: Chart & Queue */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
        
        {/* Large Capacity Bar Chart Area */}
        <div className="xl:col-span-8 bg-white border border-slate-200 rounded-[2.5rem] p-8 md:p-10 shadow-sm">
          <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-4 mb-12">
            <div>
              <h3 className="text-xl font-extrabold tracking-tight text-slate-900">Capacity Bar Chart</h3>
              <p className="text-sm font-medium text-slate-500 mt-1">Hourly traffic schematic & throughput</p>
            </div>
            <div className="flex gap-2 p-1 bg-slate-100 rounded-full">
              <button className={`px-5 py-2 rounded-full text-xs font-bold transition-colors ${capacity?.range === '24H' ? 'bg-white text-slate-900 shadow-sm' : 'hover:bg-slate-200 text-slate-500'}`}>24H</button>
              <button className={`px-5 py-2 rounded-full text-xs font-bold transition-colors ${capacity?.range === '7D' ? 'bg-white text-slate-900 shadow-sm' : 'hover:bg-slate-200 text-slate-500'}`}>7D</button>
            </div>
          </div>

          {/* Schematic Chart Mockup */}
          <div className="h-72 w-full flex items-end justify-between gap-1 relative pt-8 border-b border-slate-200">
            <div className="absolute -left-2 md:-left-6 h-full flex flex-col justify-between text-[10px] text-slate-300 font-bold pb-2">
              <span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span>
            </div>
            
            {/* Grid Lines */}
            <div className="absolute inset-x-0 top-0 h-full flex flex-col justify-between pointer-events-none pb-2">
              <div className="border-t border-slate-100 border-dashed w-full"></div>
              <div className="border-t border-slate-100 border-dashed w-full"></div>
              <div className="border-t border-slate-100 border-dashed w-full"></div>
              <div className="border-t border-slate-100 border-dashed w-full"></div>
            </div>

            {/* Bars */}
            <div className="flex-1 flex items-end justify-between h-[calc(100%-8px)] z-10 w-full pl-6 md:pl-0">
              {capacity?.data?.map((val: number, i: number) => (
                <div key={i} className="group relative h-full flex items-end w-full px-0.5 sm:px-1">
                  <div 
                    className={`w-full rounded-t flex-shrink-0 transition-all duration-300 hover:opacity-80 cursor-pointer ${
                      val >= 90 ? 'bg-blue-600' : val >= 40 ? 'bg-blue-400' : 'bg-slate-200'
                    }`}
                    style={{ height: `${val}%` }}
                  ></div>
                  <div className="opacity-0 group-hover:opacity-100 absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-slate-900 text-white text-[10px] px-2 py-1 rounded font-bold pointer-events-none whitespace-nowrap z-20 transition-opacity">
                    {val}% Capacity
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-4 flex justify-between text-[10px] text-slate-400 font-bold uppercase tracking-widest px-6 md:px-0">
            {capacity?.labels?.filter((_: string, i: number) => i % 4 === 0).map((lbl: string, i: number) => (
              <span key={i}>{lbl}</span>
            ))}
          </div>
        </div>

        {/* Right Sidebar: Booking Queue */}
        <div className="xl:col-span-4 space-y-8 flex flex-col">
          <div className="bg-white border border-slate-200 rounded-[2.5rem] p-8 h-full flex flex-col shadow-sm">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xl font-extrabold tracking-tight text-slate-900">Booking Queue</h3>
              <button className="text-blue-600 hover:text-blue-800 text-xs font-bold uppercase tracking-widest transition-colors">View All</button>
            </div>
            
            <div className="space-y-6 flex-1 pr-2">
              {queue?.items?.length === 0 ? (
                <div className="flex items-center justify-center h-40 text-sm font-bold text-slate-400 uppercase tracking-widest">
                  No Active Bookings
                </div>
              ) : queue?.items?.map((item: any, i: number) => (
                <div key={item.id} className="relative pl-6 pb-6 border-l border-slate-200 last:border-0 last:pb-0 group">
                  <div className={`absolute -left-[5px] top-0 w-[9px] h-[9px] rounded-full transition-transform ${item.status === 'in_progress' ? 'bg-blue-500 group-hover:scale-150 animate-pulse' : 'bg-slate-300'}`}></div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <h4 className="font-bold text-sm text-slate-900">{item.vehicle.name}</h4>
                        <p className="text-xs font-medium text-slate-500">ID: {item.id}</p>
                      </div>
                      <span className={`px-3 py-1 text-[10px] font-black rounded-full uppercase shrink-0 ${BOOKING_STATUS_MAP[item.status]?.color === 'blue' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>
                        {BOOKING_STATUS_MAP[item.status]?.label || item.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-xl border border-slate-100">
                      <div className="text-[10px]">
                        <p className="text-slate-400 font-bold uppercase tracking-tighter">ETA: {item.service?.eta || 'N/A'}</p>
                        <p className="text-slate-900 font-semibold mt-0.5">{item.service.name}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {queue?.ai_insight && (
              <div className="mt-8 pt-6 border-t border-slate-100">
                <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex gap-4">
                  <Info className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                  <p className="text-[11px] leading-relaxed text-amber-800 font-medium">
                    <strong className="block mb-1 text-xs font-black text-amber-900">{queue.ai_insight.title?.toUpperCase() || 'CAPACITY ALERT'}</strong>
                    {queue.ai_insight.message}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm hover:border-blue-200 transition-colors group">
          <div className="flex justify-between items-center mb-6">
            <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <Timer className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Efficiency</span>
          </div>
          <p className="text-sm font-bold text-slate-500">Avg. Wash Time</p>
          <p className="text-3xl font-black mt-1 tracking-tight text-slate-900">
            {Math.floor(data.bottom_stats.efficiency.avg_wash_time_seconds / 60)}m {data.bottom_stats.efficiency.avg_wash_time_seconds % 60}s
          </p>
          <p className="text-xs text-emerald-500 font-bold mt-2 uppercase">{data.bottom_stats.efficiency.trend_text}</p>
        </div>

        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm hover:border-blue-200 transition-colors group">
          <div className="flex justify-between items-center mb-6">
            <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <Droplets className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Resources</span>
          </div>
          <p className="text-sm font-bold text-slate-500">Water Usage (L)</p>
          <p className="text-3xl font-black mt-1 tracking-tight text-slate-900">{data.bottom_stats.resources.water_usage_liters.toLocaleString()}L</p>
          <p className="text-xs text-slate-400 font-bold mt-2 uppercase">{data.bottom_stats.resources.status}</p>
        </div>

        <div className="bg-white border border-slate-200 p-8 rounded-[2rem] shadow-sm hover:border-blue-200 transition-colors group">
          <div className="flex justify-between items-center mb-6">
            <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <UserSearch className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Conversion</span>
          </div>
          <p className="text-sm font-bold text-slate-500">New Subscriptions</p>
          <p className="text-3xl font-black mt-1 tracking-tight text-slate-900">{data.bottom_stats.conversion.new_subscriptions}</p>
          <p className="text-xs text-blue-500 font-bold mt-2 uppercase">{data.bottom_stats.conversion.trend_text}</p>
        </div>
      </div>
    </div>
  )
}
