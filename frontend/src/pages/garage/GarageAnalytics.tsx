import { useState, useEffect } from 'react'
import { Calendar, Download, Printer } from 'lucide-react'
import { garageApi } from '@/services/api'

export function GarageAnalytics() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [range, setRange] = useState('30D')

  useEffect(() => {
    setLoading(true)
    garageApi.analytics(range).then(res => {
      setData(res)
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [range])

  if (!data && loading) {
    return (
      <div className="p-8 md:p-12 max-w-7xl mx-auto flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    )
  }

  // Generate dynamic path for the SVG line chart based on data.revenue_chart.data
  const generateSvgLine = () => {
    if (!data?.revenue_chart?.data?.length) return { path: '', fill: '' }
    const points = data.revenue_chart.data
    const max = Math.max(...points) * 1.1 || 100
    const min = 0
    const width = 1000
    const height = 250 // drawing bounded to 250
    const stepX = width / (points.length - 1 || 1)
    
    const coords = points.map((p: number, i: number) => {
      const x = i * stepX
      const y = height - ((p - min) / (max - min)) * height
      return `${x},${y}`
    })
    
    // Smooth or straight lines. L for straight lines
    const pathData = `M${coords.map((c: string, i: number) => i === 0 ? c : `L${c}`).join(' ')}`
    const fillData = `${pathData} L${width},300 L0,300 Z`
    
    return { path: pathData, fill: fillData }
  }

  const { path: strokePath, fill: fillPath } = generateSvgLine()

  const formatCurrency = (val: number) => {
    if (val >= 1000) return `$${(val / 1000).toFixed(1)}k`
    return `$${val}`
  }

  return (
    <div className="p-8 md:p-12 max-w-7xl mx-auto min-h-[calc(100vh-4rem)] flex flex-col">
      {/* Header Section */}
      <header className="flex flex-col md:flex-row justify-between md:items-end gap-6 mb-12">
        <div>
          <span className="text-[0.6875rem] font-bold uppercase tracking-[0.1em] text-blue-500">System Analytics</span>
          <h2 className="text-4xl md:text-5xl font-black tracking-tighter text-slate-900 mt-2 italic pr-2">Performance Metrics</h2>
        </div>
        <div className="flex flex-wrap gap-4">
          <div className="bg-white border border-slate-200 rounded-full flex items-center shadow-sm hover:border-blue-200 transition-colors cursor-pointer overflow-hidden leading-none relative">
            {loading && <div className="absolute inset-0 bg-white/50 z-10" />}
            <select 
              value={range}
              onChange={e => setRange(e.target.value)}
              className="appearance-none bg-transparent pl-10 pr-6 py-3.5 text-sm font-bold text-slate-700 outline-none cursor-pointer"
            >
              <option value="7D">Last 7 Days</option>
              <option value="30D">Last 30 Days</option>
              <option value="90D">Last 90 Days</option>
            </select>
            <Calendar className="w-4 h-4 text-blue-600 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
          <button className="bg-blue-100 text-blue-800 px-8 py-3 rounded-full font-bold hover:bg-blue-200 active:scale-95 transition-all outline-none">
            Export Report
          </button>
        </div>
      </header>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {data?.metrics && [
          { label: 'Gross Revenue', value: formatCurrency(data.metrics.gross_revenue.value), trend: data.metrics.gross_revenue.trend, up: data.metrics.gross_revenue.is_up },
          { label: 'Active Bookings', value: data.metrics.active_bookings.value.toLocaleString(), trend: data.metrics.active_bookings.trend, up: data.metrics.active_bookings.is_up },
          { label: 'Customer SAT', value: data.metrics.customer_sat.value, trend: data.metrics.customer_sat.trend, up: data.metrics.customer_sat.is_up },
          { label: 'Conversion Rate', value: `${data.metrics.conversion_rate.value}%`, trend: data.metrics.conversion_rate.trend, up: data.metrics.conversion_rate.is_up }
        ].map((metric, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-sm hover:border-blue-200 transition-colors">
            <span className="text-[0.6875rem] font-bold uppercase tracking-[0.1em] text-slate-400">{metric.label}</span>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-3xl md:text-4xl font-black text-slate-900">{metric.value}</span>
              <span className={`font-bold text-sm ${metric.up ? 'text-emerald-500' : 'text-rose-500'}`}>{metric.trend}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        {/* Revenue Over Time Line Chart */}
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-2xl p-8 md:p-10 shadow-sm flex flex-col relative overflow-hidden">
          {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
          <div className="flex justify-between items-center mb-10">
            <h3 className="text-xl font-black tracking-tight text-slate-900">Revenue Over Time</h3>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-200 border border-blue-400"></div>
              <span className="text-[0.6875rem] font-bold uppercase tracking-[0.05em] text-slate-500">Service Revenue</span>
            </div>
          </div>
          
          <div className="relative flex-grow min-h-[250px] flex items-end gap-1 pb-8">
            <div className="absolute inset-x-0 inset-y-0 bottom-8 flex flex-col justify-between pointer-events-none">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="border-t border-slate-100 border-dashed w-full"></div>
              ))}
            </div>
            
            <svg className="absolute bottom-8 left-0 w-full h-[80%] overflow-visible" viewBox="0 0 1000 300" preserveAspectRatio="none">
              {strokePath && (
                <>
                  <path d={strokePath} fill="none" stroke="#3b82f6" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4"></path>
                  <path d={fillPath} fill="url(#gradient)" opacity="0.15"></path>
                </>
              )}
              <defs>
                <linearGradient id="gradient" x1="0%" x2="0%" y1="0%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#3b82f6', stopOpacity: 1 }}></stop>
                  <stop offset="100%" style={{ stopColor: '#3b82f6', stopOpacity: 0 }}></stop>
                </linearGradient>
              </defs>
            </svg>
            
            <div className={`absolute bottom-0 left-0 w-full flex justify-between text-[0.6875rem] font-bold uppercase text-slate-400 px-2`}>
              {data?.revenue_chart?.labels?.map((m: string, idx: number, arr: string[]) => {
                // Show fewer labels if too many points to avoid crowding
                if (arr.length > 15 && idx % Math.ceil(arr.length / 7) !== 0 && idx !== arr.length -1 && idx !== 0) return <span key={m} className="invisible w-0">{m}</span>;
                return <span key={m}>{m}</span>
              })}
            </div>
          </div>
        </div>

        {/* New vs Returning Donut */}
        <div className="lg:col-span-4 bg-white border border-slate-200 rounded-2xl p-8 md:p-10 shadow-sm flex flex-col items-center relative overflow-hidden">
          {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
          <h3 className="text-xl font-black tracking-tight text-slate-900 mb-8 self-start">New vs. Returning</h3>
          
          <div className="relative w-48 h-48 mb-8 shrink-0 flex items-center justify-center">
            {data?.customer_retention && (
              <>
                <svg className="absolute inset-0 transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" fill="none" r="40" stroke="#f1f5f9" strokeWidth="12"></circle>
                  <circle 
                    cx="50" cy="50" fill="none" r="40" stroke="#3b82f6" 
                    strokeDasharray={`${(data.customer_retention.returning_percentage / 100) * 251} 251`} 
                    strokeWidth="12" strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  ></circle>
                </svg>
                <div className="flex flex-col items-center justify-center relative z-10 text-center">
                  <span className="text-3xl font-black text-slate-900 leading-none">{data.customer_retention.returning_percentage}%</span>
                  <span className="text-[0.6875rem] font-bold uppercase tracking-widest text-slate-400 mt-1">Returning</span>
                </div>
              </>
            )}
          </div>
          
          <div className="w-full space-y-4 mt-auto">
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="font-bold text-slate-700">Returning Clients</span>
              </div>
              <span className="font-black text-slate-900">{data?.customer_retention?.returning_count}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-slate-100 border border-slate-300"></div>
                <span className="font-bold text-slate-700">New Acquisitions</span>
              </div>
              <span className="font-black text-slate-900">{data?.customer_retention?.new_count}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Service Performance Distribution */}
      <div className="bg-white border border-slate-200 rounded-2xl p-8 md:p-10 shadow-sm mb-12 relative overflow-hidden">
        {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
        <h3 className="text-xl font-black tracking-tight mb-8 text-slate-900">Service Category Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {data?.service_distribution?.map((cat: any, i: number) => {
            const colors = ['bg-blue-600', 'bg-blue-400', 'bg-blue-300', 'bg-slate-300']
            const color = colors[i % colors.length]
            return (
              <div key={i} className="flex flex-col gap-4">
                <div className="flex justify-between text-sm font-bold text-slate-800">
                  <span>{cat.name}</span>
                  <span>{cat.percentage}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className={`h-full ${color} rounded-full transition-all duration-1000 delay-300`} style={{ width: `${cat.percentage}%` }}></div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Technical Footer */}
      <footer className="mt-auto pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs">
        <div className="flex gap-8">
          <div className="flex flex-col gap-1">
            <span className="text-[0.625rem] uppercase font-bold text-slate-400 tracking-widest">Version</span>
            <span className="font-mono text-slate-700 font-medium">WM-2.4.0-STABLE</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[0.625rem] uppercase font-bold text-slate-400 tracking-widest">Server Status</span>
            <span className="font-bold text-emerald-600 flex items-center gap-1.5 uppercase tracking-wide">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Operational
            </span>
          </div>
        </div>
        <div className="flex gap-3">
          <button className="p-2 border border-slate-200 text-slate-500 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors">
            <Printer className="w-4 h-4" />
          </button>
          <button className="p-2 border border-slate-200 text-slate-500 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors">
            <Download className="w-4 h-4" />
          </button>
        </div>
      </footer>
    </div>
  )
}
