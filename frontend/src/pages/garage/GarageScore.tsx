import { useState, useEffect } from 'react'
import { TrendingUp, CheckCircle2, Lightbulb, GaugeCircle } from 'lucide-react'
import { garageApi } from '@/services/api'

export function GarageScore() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    garageApi.score().then(res => {
      setData(res)
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }, [])

  if (!data && loading) {
    return (
      <div className="p-8 md:p-12 max-w-7xl mx-auto flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    )
  }

  // Calculate gauge dash offset based on aggregate_score
  // circumference = 2 * PI * 45 = 282.7
  // dashoffset = 282.7 - (282.7 * score / 100)
  const score = data?.aggregate_score || 0
  const circumference = 282.7
  const dashoffset = circumference - (circumference * score) / 100

  // Helper to format requirements
  const reqs = data?.progression?.requirements_for_next || {}
  const reqKeys = Object.keys(reqs)

  return (
    <div className="p-8 md:p-12 max-w-7xl mx-auto space-y-16">
      {/* Top Section: Radial Gauge */}
      <section className="flex flex-col md:flex-row items-center md:items-stretch gap-12 pt-8 relative">
        {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
        <div className="relative w-80 h-80 flex items-center justify-center shrink-0">
          {/* SVG Gauge */}
          <svg className="w-full h-full -rotate-90 transform drop-shadow-md" viewBox="0 0 100 100">
            <circle className="text-slate-100" cx="50" cy="50" fill="transparent" r="45" stroke="currentColor" strokeWidth="8"></circle>
            <circle 
              className="text-blue-500 transition-all duration-1000 ease-out" 
              cx="50" cy="50" fill="transparent" r="45" stroke="currentColor" 
              strokeDasharray={Object.is(NaN, dashoffset) ? 0 : circumference} 
              strokeDashoffset={Object.is(NaN, dashoffset) ? circumference : dashoffset} 
              strokeLinecap="round" strokeWidth="8">
            </circle>
          </svg>
          {/* Center Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-[0.6875rem] font-bold uppercase tracking-[0.2em] text-slate-400 mb-1">Efficiency Index</span>
            <div className="flex items-baseline">
              <span className="text-[5rem] font-black leading-none text-blue-600 tracking-tighter">{score}</span>
              <span className="text-2xl font-bold text-slate-300 ml-1">/100</span>
            </div>
            <div className="mt-4 px-4 py-1.5 bg-blue-50 rounded-full border border-blue-200">
              <span className="text-xs font-black text-blue-700 tracking-wider">STATUS: {data?.status_text}</span>
            </div>
          </div>
          {/* Blueprint Accents */}
          <div className="absolute top-0 right-0 p-2 border-r-2 border-t-2 border-slate-200 w-16 h-16 rounded-tr-3xl"></div>
          <div className="absolute bottom-0 left-0 p-2 border-l-2 border-b-2 border-slate-200 w-16 h-16 rounded-bl-3xl"></div>
        </div>

        <div className="flex-1 flex flex-col justify-center space-y-6">
          <div>
            <span className="text-[0.6875rem] font-bold uppercase tracking-[0.2em] text-blue-600 mb-2 block">Technical Overview</span>
            <h2 className="text-4xl md:text-[2.5rem] font-black text-slate-900 leading-tight tracking-tight italic pr-2">
              Aggregate Efficiency Score
            </h2>
            <p className="text-slate-500 max-w-xl text-lg mt-4 font-medium leading-relaxed">
              Your garage is currently operating at <span className="font-bold text-blue-600">{data?.technical_overview?.comparison_text}</span>. To reach "{data?.progression?.next_tier}" status, an aggregate score of 85+ is required across all primary schematic nodes.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-6 mt-4">
            <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-blue-200 transition-colors">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Bays</p>
              <p className="text-3xl font-black text-slate-900 mt-2">{String(data?.technical_overview?.active_bays).padStart(2,'0')} <span className="text-sm font-bold text-slate-400">/ {data?.technical_overview?.total_bays}</span></p>
            </div>
            <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-blue-200 transition-colors">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Throughput</p>
              <p className="text-3xl font-black text-slate-900 mt-2">{data?.technical_overview?.throughput_vph} <span className="text-sm font-bold text-slate-400">vph</span></p>
            </div>
          </div>
        </div>
      </section>

      {/* Middle Section: Component Breakdown */}
      <section className="space-y-8 bg-white border border-slate-200 rounded-[2.5rem] p-8 md:p-12 shadow-sm relative">
        {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
        <div className="flex flex-col md:flex-row justify-between md:items-end gap-6 border-b border-slate-200 pb-8">
          <div>
            <span className="text-[0.6875rem] font-bold uppercase tracking-[0.2em] text-slate-400 block mb-1">Diagnostic Breakdown</span>
            <h3 className="text-2xl font-black text-slate-900">Scoring Components</h3>
          </div>
          <button className="px-8 py-3 bg-slate-50 border border-slate-200 text-blue-700 rounded-full font-bold text-xs uppercase tracking-widest hover:bg-blue-50 hover:border-blue-200 hover:text-blue-800 transition-all shadow-sm">
            Download Full Report
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-6 md:gap-8 pt-4">
          {data?.score_components && Object.entries(data.score_components).map(([key, item]: [string, any]) => (
            <div key={key} className="group flex flex-col h-full">
              <div className="h-48 md:h-64 bg-slate-50 border border-slate-200 rounded-2xl relative overflow-hidden flex items-end p-1.5 hover:border-blue-300 transition-colors">
                <div 
                  className={`w-full rounded-xl transition-all duration-1000 ease-out hover:opacity-90 ${item.score >= 80 ? 'bg-blue-600' : item.score >= 60 ? 'bg-blue-400' : 'bg-rose-400'}`} 
                  style={{ height: `${item.score}%` }}
                ></div>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className={`text-4xl md:text-5xl font-black transition-colors ${item.score > 50 ? 'mix-blend-overlay text-white' : 'text-slate-900/10'}`}>{item.score}</span>
                </div>
              </div>
              <div className="mt-6 flex-grow">
                <h4 className="text-sm font-black uppercase tracking-tight text-slate-900">{key}</h4>
                <p className="text-xs text-slate-500 mt-2 font-medium leading-relaxed">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom Section: Roadmap */}
      <section className="bg-white border border-slate-200 rounded-[2.5rem] p-10 md:p-14 relative overflow-hidden shadow-sm">
        {loading && <div className="absolute inset-0 bg-white/50 backdrop-blur-[1px] z-20" />}
        <div className="absolute -right-20 -top-20 opacity-[0.02] text-slate-900 pointer-events-none">
          <GaugeCircle className="w-[400px] h-[400px]" />
        </div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-6 mb-12">
            <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center rotate-12 group-hover:rotate-0 transition-transform">
              <TrendingUp className="w-8 h-8" />
            </div>
            <div>
              <span className="text-[0.6875rem] font-bold uppercase tracking-[0.2em] text-blue-600 mb-1 block">Progression Path</span>
              <h3 className="text-3xl md:text-4xl font-black text-slate-900 tracking-tight italic">Roadmap to Elite Tier</h3>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 relative pt-8">
            {/* Connector Lines */}
            <div className="hidden md:block absolute top-[4.5rem] left-0 w-full h-1 bg-slate-100 -translate-y-1/2 z-0 rounded-full"></div>
            
            {/* Step 1: Standard */}
            <div className="relative z-10 bg-white p-8 border-2 border-blue-500 rounded-3xl shadow-md">
              <div className="absolute -top-4 left-8 px-4 py-1.5 bg-blue-600 rounded-full text-xs font-black text-white uppercase tracking-widest shadow-sm">{data?.progression?.current_tier === 'Standard' ? 'Active' : 'Completed'}</div>
              <h4 className="text-2xl font-black text-slate-900 mb-3 mt-2">Standard</h4>
              <p className="text-sm font-medium text-slate-500 mb-8 leading-relaxed">Current performance level. Solid foundations but inconsistent throughput in peak hours.</p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3 text-sm font-bold text-slate-700">
                  <CheckCircle2 className="w-5 h-5 text-blue-500" /> Registered Facility
                </li>
                <li className="flex items-center gap-3 text-sm font-bold text-slate-700">
                  <CheckCircle2 className="w-5 h-5 text-blue-500" /> Basic Telemetry
                </li>
              </ul>
            </div>

            {/* Step 2: Pro */}
            <div className="relative z-10 bg-slate-50 p-8 border border-slate-200 rounded-3xl opacity-90 hover:opacity-100 hover:bg-white hover:border-blue-300 transition-all cursor-pointer group mt-4 md:mt-0">
              {data?.progression?.current_tier === 'Pro' && (
                <div className="absolute -top-4 left-8 px-4 py-1.5 bg-blue-600 rounded-full text-xs font-black text-white uppercase tracking-widest shadow-sm">Active</div>
              )}
              <h4 className="text-2xl font-black text-slate-900 mb-3 mt-2">Pro</h4>
              <p className="text-sm font-medium text-slate-500 mb-8 leading-relaxed">Unlock priority search listing and lower platform transaction fees (12%).</p>
              <div className="space-y-6">
                {reqKeys.length > 0 && reqKeys.map(k => (
                  <div key={k} className="space-y-2">
                    <div className="flex justify-between text-xs font-black uppercase text-slate-700">
                      <span>{k.replace('_', ' ')}</span>
                      <span className="text-blue-600">{reqs[k].current}/{reqs[k].target}</span>
                    </div>
                    <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full group-hover:bg-blue-600 transition-colors" style={{ width: `${Math.min(100, (reqs[k].current / reqs[k].target) * 100)}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Step 3: Elite */}
            <div className="relative z-10 bg-slate-50 p-8 border border-slate-200 rounded-3xl opacity-70 hover:opacity-100 hover:bg-white hover:border-blue-300 transition-all cursor-pointer group mt-4 md:mt-0">
              {data?.progression?.current_tier === 'Elite' && (
                <div className="absolute -top-4 left-8 px-4 py-1.5 bg-blue-600 rounded-full text-xs font-black text-white uppercase tracking-widest shadow-sm">Active</div>
              )}
              <h4 className="text-2xl font-black text-slate-900 mb-3 mt-2">Elite</h4>
              <p className="text-sm font-medium text-slate-500 mb-8 leading-relaxed">Top 1% placement, dedicated account manager, and zero-fee maintenance leads.</p>
              <div className="mt-8 flex flex-wrap gap-2">
                <span className="px-3 py-1.5 border-2 border-slate-200 text-[10px] font-black uppercase rounded-lg text-slate-500 group-hover:border-blue-200 group-hover:text-blue-700 transition-colors">95+ Score</span>
                <span className="px-3 py-1.5 border-2 border-slate-200 text-[10px] font-black uppercase rounded-lg text-slate-500 group-hover:border-blue-200 group-hover:text-blue-700 transition-colors">ISO Certified</span>
                <span className="px-3 py-1.5 border-2 border-slate-200 text-[10px] font-black uppercase rounded-lg text-slate-500 group-hover:border-blue-200 group-hover:text-blue-700 transition-colors">0 Reclaims</span>
              </div>
            </div>
          </div>

          {data?.ai_recommendation && (
            <div className="mt-12 flex flex-col items-center text-center gap-4 p-8 border-2 border-dashed border-rose-200 rounded-3xl bg-rose-50 max-w-2xl mx-auto">
              <Lightbulb className="w-10 h-10 text-rose-500 shrink-0" />
              <div>
                <p className="text-base font-black text-rose-900 uppercase tracking-wide">{data.ai_recommendation.title}</p>
                <div className="text-sm font-medium text-rose-800 mt-2 leading-relaxed" 
                     dangerouslySetInnerHTML={{ __html: data.ai_recommendation.description.replace(/(Staff score \(45\))/g, '<strong>$1</strong>') }} />
              </div>
              <button className="mt-4 px-8 py-3 bg-rose-600 text-white rounded-full font-black text-xs uppercase tracking-widest hover:bg-rose-700 hover:scale-105 active:scale-95 transition-all shadow-md">
                Begin Assessment
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
