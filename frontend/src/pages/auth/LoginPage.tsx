import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, ArrowRight, Mail, Lock, User, Phone, CheckCircle2, ChevronLeft } from 'lucide-react'
import { useAuth } from '@/services/auth-context'

export function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    name: '', username: '', email: '', phone: '', password: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    try {
      if (isLogin) {
        const user = await login(formData.username, formData.password)
        // login returns void, user available from context — redirect based on role
        navigate('/app')
      } else {
        await register({
          username: formData.username,
          password: formData.password,
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
        })
        navigate('/app')
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-50">

      {/* ── Left: Hero ── */}
      <div className="hidden lg:flex w-[45%] relative bg-slate-900 overflow-hidden flex-col justify-between">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-40 mix-blend-luminosity"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1601362840469-51e4d8d58785?auto=format&fit=crop&q=80&w=1200')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/60 to-transparent" />

        <div className="relative z-10 p-12">
          <img src="/washmind_logo_ngang.png" alt="WashMind" className="h-10 w-auto brightness-0 invert opacity-90" />
        </div>

        <div className="relative z-10 p-12 pb-16 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-[10px] font-bold uppercase tracking-widest border border-blue-500/30 backdrop-blur-md">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Intelligence Protocol 4.2
          </div>
          <h1 className="text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight">
            The standard<br />for premium<br />car care.
          </h1>
          <p className="text-slate-400 font-medium text-sm max-w-sm leading-relaxed">
            Access the largest network of elite detailing centers. AI-powered scheduling, telemetry tracking, and perfection-driven results.
          </p>
          <div className="flex items-center gap-3 pt-6 border-t border-slate-800">
            <div className="flex -space-x-3">
              {[1, 2, 3].map(i => (
                <img key={i} className="w-8 h-8 rounded-full border-2 border-slate-900" src={`https://i.pravatar.cc/100?img=${i}`} alt="User" />
              ))}
            </div>
            <p className="text-xs font-bold text-slate-500">Join 12,500+ premium members</p>
          </div>
        </div>

        {/* Demo credentials hint */}
        <div className="relative z-10 px-12 pb-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-4 backdrop-blur-md">
            <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-2">Demo Login</p>
            <p className="text-xs font-mono text-white/70">customer_an / Customer@2026</p>
          </div>
        </div>
      </div>

      {/* ── Right: Form ── */}
      <div className="flex-1 flex flex-col justify-center px-6 sm:px-12 md:px-24">

        {/* Mobile logo */}
        <div className="w-full max-w-[440px] mx-auto lg:hidden mb-12">
          <img src="/washmind_logo_ngang.png" alt="WashMind" className="h-10 w-auto" />
        </div>

        <div className="w-full max-w-[440px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
          <button
            className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-blue-600 transition-colors uppercase tracking-widest mb-10 group"
            onClick={() => navigate('/app')}
          >
            <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to app
          </button>

          <div className="mb-10">
            <h2 className="text-3xl font-black text-slate-900 tracking-tight">
              {isLogin ? 'Welcome back.' : 'Create account.'}
            </h2>
            <p className="text-sm text-slate-500 font-medium mt-2">
              {isLogin
                ? 'Secure access strictly for WashMind members.'
                : 'Enter your details to generate your WashMind ID.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-4 bg-red-50 text-red-600 border border-red-100 rounded-2xl text-sm font-semibold flex items-center gap-3">
                <ShieldCheck className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}

            {!isLogin && (
              <div className="space-y-4">
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                  <input required name="name" value={formData.name} onChange={handleChange} type="text" placeholder="Full Name"
                    className="w-full pl-12 pr-4 py-4 bg-white border border-slate-200 text-slate-900 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 text-sm font-semibold transition-all shadow-sm" />
                </div>
                <div className="flex gap-4">
                  <div className="relative group flex-1">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                    <input required name="email" value={formData.email} onChange={handleChange} type="email" placeholder="Email"
                      className="w-full pl-12 pr-4 py-4 bg-white border border-slate-200 text-slate-900 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 text-sm font-semibold transition-all shadow-sm" />
                  </div>
                  <div className="relative group flex-1">
                    <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                    <input required name="phone" value={formData.phone} onChange={handleChange} type="tel" placeholder="Phone"
                      className="w-full pl-12 pr-4 py-4 bg-white border border-slate-200 text-slate-900 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 text-sm font-semibold transition-all shadow-sm" />
                  </div>
                </div>
              </div>
            )}

            <div className="relative group">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
              <input required name="username" value={formData.username} onChange={handleChange} type="text" placeholder="Username"
                className="w-full pl-12 pr-4 py-4 bg-white border border-slate-200 text-slate-900 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 text-sm font-semibold transition-all shadow-sm" />
            </div>

            <div className="relative group">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
              <input required name="password" value={formData.password} onChange={handleChange} type="password" placeholder="Password"
                className="w-full pl-12 pr-4 py-4 bg-white border border-slate-200 text-slate-900 rounded-2xl outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 text-sm font-semibold transition-all shadow-sm" />
            </div>

            <button
              disabled={isLoading}
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 active:scale-[0.98] disabled:opacity-60 text-white py-4 rounded-2xl font-bold tracking-wide transition-all shadow-lg shadow-blue-500/30 flex justify-center items-center gap-2 group mt-2"
            >
              {isLoading ? (
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isLogin ? 'AUTHENTICATE' : 'CREATE ACCOUNT'}
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-10 text-center">
            <p className="text-sm font-medium text-slate-500">
              {isLogin ? "Don't have a WashMind ID?" : 'Already have an account?'}
            </p>
            <button
              onClick={() => { setIsLogin(!isLogin); setError('') }}
              className="mt-2 text-sm font-bold text-slate-900 hover:text-blue-600 transition-colors uppercase tracking-widest border-b-2 border-slate-900 hover:border-blue-600 pb-0.5"
            >
              {isLogin ? 'Request Member Access' : 'Return to Login'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
