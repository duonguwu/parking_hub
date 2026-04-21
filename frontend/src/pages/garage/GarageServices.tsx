import { useState, useEffect } from 'react'
import { PlusCircle, Wrench, PackagePlus, Edit2, Timer, TrendingUp, Droplets, SprayCan, CheckCircle2 } from 'lucide-react'
import { garageApi } from '@/services/api'

export function GarageServices() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    garageApi.services().then(res => {
      setData(res)
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [])

  const getIcon = (type: string) => {
    switch(type) {
      case 'spraycan': return <SprayCan className="w-8 h-8" />
      case 'droplets': return <Droplets className="w-8 h-8" />
      default: return <CheckCircle2 className="w-8 h-8" />
    }
  }

  const getIconStyles = (type: string) => {
    switch(type) {
      case 'spraycan': return 'bg-purple-50 border-purple-100 text-purple-600'
      case 'droplets': return 'bg-blue-50 border-blue-100 text-blue-600'
      default: return 'bg-amber-50 border-amber-100 text-amber-600'
    }
  }

  if (!data && loading) {
    return (
      <div className="p-8 md:p-12 max-w-7xl mx-auto flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8 md:p-12 max-w-7xl mx-auto space-y-12">
      {/* Header Section */}
      <header className="flex flex-col md:flex-row justify-between md:items-end gap-6 mb-8">
        <div className="space-y-2">
          <span className="text-[0.6875rem] uppercase tracking-[0.1em] font-bold text-blue-500">Configuration Panel</span>
          <h2 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tighter italic pr-2">Services</h2>
        </div>
        <button className="flex items-center justify-center gap-2 bg-blue-100 text-blue-800 px-8 py-3.5 rounded-full font-bold hover:bg-blue-200 active:scale-95 transition-all">
          <PlusCircle className="w-5 h-5" />
          Add New Service
        </button>
      </header>

      {/* Stats Row */}
      {data?.stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-slate-200 p-8 flex flex-col justify-between rounded-2xl relative overflow-hidden group hover:border-blue-200 transition-all shadow-sm">
            <div className="relative z-10 space-y-2">
              <p className="text-[0.6875rem] uppercase tracking-widest font-bold text-slate-500">Total Active Services</p>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-black text-slate-900">{data.stats.active_services}</span>
              </div>
            </div>
            <div className="absolute -right-4 -bottom-4 opacity-[0.03] pointer-events-none group-hover:scale-110 transition-transform duration-500">
              <Wrench className="w-40 h-40" />
            </div>
          </div>

          <div className="bg-white border border-slate-200 p-8 flex flex-col justify-between rounded-2xl relative overflow-hidden group hover:border-blue-200 transition-all shadow-sm">
            <div className="relative z-10 space-y-2">
              <p className="text-[0.6875rem] uppercase tracking-widest font-bold text-slate-500">Avg. Completion Time</p>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-black text-slate-900">{data.stats.avg_completion_time_mins}</span>
                <span className="text-sm font-bold text-slate-500">mins</span>
              </div>
            </div>
            <div className="absolute -right-4 -bottom-4 opacity-[0.03] pointer-events-none group-hover:scale-110 transition-transform duration-500">
              <Timer className="w-40 h-40" />
            </div>
          </div>

          <div className="bg-white border border-slate-200 p-8 flex flex-col justify-between rounded-2xl relative overflow-hidden group hover:border-blue-200 transition-all shadow-sm">
            <div className="relative z-10 space-y-2">
              <p className="text-[0.6875rem] uppercase tracking-widest font-bold text-slate-500">Revenue Efficiency</p>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-black text-emerald-600">{data.stats.revenue_efficiency_percent}</span>
                <span className="text-sm font-bold text-slate-500">%</span>
              </div>
            </div>
            <div className="absolute -right-4 -bottom-4 opacity-[0.03] pointer-events-none group-hover:scale-110 transition-transform duration-500">
              <TrendingUp className="w-40 h-40" />
            </div>
          </div>
        </div>
      )}

      {/* Service Grid Bento */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 relative">
        {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
        
        {data?.services?.map((svc: any) => (
          <article key={svc.id} className="bg-white border border-slate-200 rounded-2xl p-8 flex flex-col h-full hover:border-blue-300 shadow-sm hover:shadow-md transition-all duration-300">
            <div className="flex justify-between items-start mb-6">
              <div className={`p-4 rounded-2xl border ${getIconStyles(svc.icon_type)}`}>
                {getIcon(svc.icon_type)}
              </div>
              {svc.tags?.includes('Popular') && (
                <span className="bg-emerald-100 text-emerald-800 text-[10px] font-black uppercase px-2 py-1 rounded shadow-sm border border-emerald-200">Popular</span>
              )}
            </div>
            <h3 className="text-2xl font-black text-slate-900 mb-2 tracking-tight">{svc.name}</h3>
            <p className="text-slate-500 font-medium text-sm leading-relaxed mb-8 flex-grow">
              {svc.description}
            </p>
            <div className="space-y-4 mb-8">
              <div className="flex justify-between items-center text-sm border-b border-slate-100 pb-3">
                <span className="text-slate-500 font-bold">Price</span>
                <span className="font-black text-slate-900">${(svc.price_usd || svc.price_vnd / 25000).toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center text-sm border-b border-slate-100 pb-3">
                <span className="text-slate-500 font-bold">Duration</span>
                <span className="font-bold text-slate-700 flex items-center gap-1.5"><Timer className="w-3.5 h-3.5" /> {svc.duration_minutes >= 1440 ? `${svc.duration_minutes / 1440} Days` : svc.duration_minutes >= 60 && svc.duration_minutes % 60 === 0 ? `${svc.duration_minutes / 60} Hours` : `${svc.duration_minutes} mins`}</span>
              </div>
            </div>
            <button className="w-full py-3 rounded-full border-2 border-slate-100 text-slate-600 font-bold text-sm hover:bg-blue-50 hover:border-blue-200 hover:text-blue-700 transition-all flex items-center justify-center gap-2">
              <Edit2 className="w-4 h-4" /> Edit Service
            </button>
          </article>
        ))}

        {/* Action Card: New Service */}
        <div className="border-2 border-dashed border-slate-300 rounded-2xl p-8 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-all min-h-[400px]">
          <div className="w-16 h-16 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center text-slate-400 group-hover:text-blue-600 group-hover:border-blue-400 mb-6 transition-all group-hover:scale-110 group-hover:bg-white shadow-[0_0_0_0_rgba(59,130,246,0)] group-hover:shadow-[0_0_20px_0_rgba(59,130,246,0.2)]">
            <PlusCircle className="w-8 h-8" />
          </div>
          <h4 className="text-lg font-black text-slate-700 group-hover:text-blue-700 transition-colors">Draft New Service</h4>
          <p className="text-sm font-medium text-slate-400 mt-3 max-w-[200px]">Define a new offering for your service catalog</p>
        </div>

        {/* Promo Card Layout */}
        {data?.upsell_recommendation && (
          <div className="bg-gradient-to-br from-blue-600 to-blue-800 text-white rounded-2xl p-8 lg:col-span-2 relative overflow-hidden flex flex-col justify-center shadow-lg hover:shadow-blue-900/20 transition-shadow">
            <div className="relative z-10 max-w-sm">
              <p className="text-[0.6875rem] uppercase tracking-widest font-black text-blue-200 mb-2">Upsell Opportunity</p>
              <h3 className="text-3xl font-black mb-4 leading-tight italic">{data.upsell_recommendation.title.replace(' ', '\n')}</h3>
              <p className="text-blue-100 font-medium text-sm mb-8 leading-relaxed">
                {data.upsell_recommendation.description}
              </p>
              <button className="bg-white text-blue-700 px-6 py-3 rounded-full font-black text-xs uppercase tracking-wider hover:scale-105 active:scale-95 transition-transform shadow-md">
                Configure Bundles
              </button>
            </div>
            <div className="absolute right-[-20px] bottom-[-40px] opacity-20 pointer-events-none">
              <PackagePlus className="w-64 h-64" />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
