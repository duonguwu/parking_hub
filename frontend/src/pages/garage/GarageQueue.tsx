import { useState, useEffect } from 'react'
import { Car, Zap, Truck, AlertTriangle, Filter, Check, X, Info } from 'lucide-react'
import { garageApi } from '@/services/api'
import { BOOKING_STATUS_MAP } from '@/services/api'

export function GarageQueue() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, today, pending
  const [page, setPage] = useState(1)

  const fetchQueue = async () => {
    try {
      setLoading(true)
      const res = await garageApi.queue(filter, page, 10)
      setData(res)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQueue()
  }, [filter, page])

  const handleStatusUpdate = async (id: string, newStatus: string) => {
    try {
      await garageApi.updateBookingStatus(id, newStatus)
      // Optimistic upate or refetch
      fetchQueue()
    } catch (err) {
      alert('Action failed')
    }
  }

  const getVehicleIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'electric': return <Zap className="w-5 h-5 text-amber-500" />
      case 'suv':
      case 'truck': return <Truck className="w-5 h-5 text-emerald-600" />
      default: return <Car className="w-5 h-5 text-blue-600" />
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
    <div className="p-8 md:p-12 max-w-7xl mx-auto space-y-8">
      {/* Hero Stats Row */}
      {data?.hero_stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-4">
          <div className="bg-white border border-slate-200 p-8 rounded-2xl relative overflow-hidden shadow-sm">
            <div className="flex flex-col gap-1">
              <span className="text-[0.6875rem] font-bold text-slate-400 uppercase tracking-[0.1em]">Today's Capacity</span>
              <span className="text-5xl font-black text-slate-900 tracking-tighter">
                {data.hero_stats.capacity_percent}<span className="text-lg text-slate-400 font-normal ml-1">%</span>
              </span>
            </div>
            <div className="absolute bottom-0 left-0 h-1.5 bg-emerald-400" style={{ width: `${data.hero_stats.capacity_percent}%` }}></div>
          </div>
          <div className="bg-white border border-slate-200 p-8 rounded-2xl shadow-sm">
            <div className="flex flex-col gap-1">
              <span className="text-[0.6875rem] font-bold text-slate-400 uppercase tracking-[0.1em]">Active Bookings</span>
              <span className="text-5xl font-black text-blue-600 tracking-tighter leading-none">{data.hero_stats.active_bookings}</span>
            </div>
          </div>
          <div className="bg-white border border-slate-200 p-8 rounded-2xl shadow-sm">
            <div className="flex flex-col gap-1">
              <span className="text-[0.6875rem] font-bold text-slate-400 uppercase tracking-[0.1em]">Pending Approval</span>
              <span className="text-5xl font-black text-slate-900 tracking-tighter">{data.hero_stats.pending_approval}</span>
            </div>
          </div>
        </div>
      )}

      {/* Header & Filters */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-slate-200">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-900">Booking Queue</h2>
          <p className="text-slate-500 mt-2 font-medium">Quản lý danh sách lượt đã đặt và lượt đang chờ.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex bg-white border border-slate-200 rounded-full p-1 h-fit shadow-sm">
            {['all', 'today', 'pending'].map(f => (
              <button 
                key={f}
                onClick={() => { setFilter(f); setPage(1) }}
                className={`px-6 py-2 text-xs font-bold uppercase tracking-wider rounded-full ${
                  filter === f ? 'bg-blue-100 text-blue-800' : 'text-slate-500 hover:bg-slate-50'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
          <button className="h-10 w-10 flex items-center justify-center border border-slate-200 rounded-full bg-white hover:bg-slate-50 shadow-sm text-slate-600">
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm relative min-h-[400px]">
        {loading && (
          <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="px-8 py-5 text-[0.6875rem] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">Appointment Time</th>
                <th className="px-8 py-5 text-[0.6875rem] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">Customer & Vehicle</th>
                <th className="px-8 py-5 text-[0.6875rem] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">Service Details</th>
                <th className="px-8 py-5 text-[0.6875rem] font-bold text-slate-500 uppercase tracking-widest text-center whitespace-nowrap">Status</th>
                <th className="px-8 py-5 text-[0.6875rem] font-bold text-slate-500 uppercase tracking-widest text-right whitespace-nowrap">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500 font-bold uppercase tracking-widest">
                    No bookings found
                  </td>
                </tr>
              ) : data?.items?.map((item: any) => {
                const isPending = item.status === 'pending'
                const isCompleted = item.status === 'completed'
                const isInProgress = item.status === 'in_service' || item.status === 'in_progress'

                return (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors group">
                    <td className="px-8 py-6">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-900">
                          {new Date(item.appointment_time || item.requested_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span className="text-[0.6875rem] text-slate-500 uppercase font-bold tracking-tighter">
                          {new Date(item.appointment_time || item.requested_time).toLocaleDateString()}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
                          isPending ? 'bg-amber-50 text-amber-600 border-amber-200' : 'bg-slate-50 text-slate-500 border-slate-200'
                        }`}>
                          {isPending ? <AlertTriangle className="w-5 h-5" /> : getVehicleIcon(item.vehicle?.type)}
                        </div>
                        <div className="flex flex-col">
                          <span className="text-sm font-bold text-slate-900">{item.customer_name}</span>
                          <span className="text-[0.6875rem] font-medium text-slate-500 mt-0.5">
                            {item.vehicle?.name || 'Vehicle'} • <span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 font-bold ml-1">{item.vehicle?.plate || 'N/A'}</span>
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-900">{item.service?.name || item.service_type_code}</span>
                        <span className="text-[0.6875rem] text-slate-500 uppercase font-bold tracking-tighter mt-0.5">{item.service?.description || 'Standard Package'}</span>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-center">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[0.6875rem] font-black uppercase tracking-wider border ${
                        isInProgress ? 'bg-blue-100 text-blue-700 border-blue-200' :
                        isPending ? 'bg-amber-100 text-amber-800 border-amber-200' :
                        isCompleted ? 'bg-emerald-100 text-emerald-800 border-emerald-200' :
                        'bg-slate-100 text-slate-600 border-slate-200'
                      }`}>
                        {isInProgress && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>}
                        {isCompleted && <Check className="w-3 h-3" />}
                        {BOOKING_STATUS_MAP[item.status]?.label || item.status}
                      </span>
                    </td>
                    <td className="px-8 py-6 text-right">
                      {!isCompleted && item.status !== 'cancelled_by_garage' && item.status !== 'cancelled_by_customer' ? (
                        <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          {isPending && (
                            <>
                              <button onClick={() => handleStatusUpdate(item.id, 'confirmed')} className="h-8 w-8 flex items-center justify-center rounded-full bg-emerald-100 text-emerald-700 hover:bg-emerald-200 transition-colors" title="Confirm Booking">
                                <Check className="w-4 h-4" />
                              </button>
                              <button onClick={() => handleStatusUpdate(item.id, 'cancelled_by_garage')} className="h-8 w-8 flex items-center justify-center rounded-full bg-rose-100 text-rose-600 hover:bg-rose-200 transition-colors" title="Decline/Cancel Booking">
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          {!isPending && (
                            <button onClick={() => handleStatusUpdate(item.id, 'completed')} className="h-8 w-8 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors" title="Mark as Completed">
                              <Check className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      ) : (
                        <div className="text-xs font-bold text-slate-400 mr-2">DONE</div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Footer */}
        {data?.pagination && (
          <div className="px-8 py-6 flex items-center justify-between bg-slate-50 border-t border-slate-200">
            <span className="text-[0.6875rem] font-bold text-slate-500 uppercase tracking-widest hidden sm:block">
              Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, data.pagination.total_items)} of {data.pagination.total_items} entries
            </span>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="h-8 px-4 flex items-center border border-slate-200 rounded-full text-xs font-bold text-slate-600 hover:bg-white disabled:opacity-50"
              >Prev</button>
              
              <div className="flex items-center gap-1">
                {[...Array(data.pagination.total_pages)].map((_, i) => (
                  <button 
                    key={i} 
                    onClick={() => setPage(i + 1)}
                    className={`h-8 w-8 flex items-center justify-center border rounded-full text-xs font-bold shadow-sm ${
                      page === i + 1 ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-200 bg-transparent text-slate-600 hover:bg-white'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>

              <button 
                onClick={() => setPage(p => Math.min(data.pagination.total_pages, p + 1))}
                disabled={page >= data.pagination.total_pages}
                className="h-8 px-4 flex items-center border border-slate-200 rounded-full text-xs font-bold text-slate-600 hover:bg-white disabled:opacity-50"
              >Next</button>
            </div>
          </div>
        )}
      </div>

      {/* Insight Alert */}
      {data?.ai_insight && (
        <div className="mt-8 p-6 md:p-8 border-2 border-dashed border-blue-200 rounded-2xl bg-blue-50 flex items-start gap-4">
          <Info className="w-6 h-6 text-blue-600 shrink-0" />
          <div>
            <h4 className="text-sm font-black text-blue-900 uppercase tracking-tight">{data.ai_insight.title || 'Coordination Insight'}</h4>
            <p className="text-sm text-blue-800 mt-1.5 leading-relaxed max-w-3xl font-medium">
              {data.ai_insight.message}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
