import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { X, Lock, Mail, User, ShieldCheck } from '../ui/Icons'
import { Button } from '../ui/Button'

export function AuthModal() {
  const { isAuthModalOpen, authModalTab, closeAuthModal, login, signup } = useAuth()
  const [tab, setTab] = useState<'login' | 'signup'>(authModalTab)

  // Form states
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    setTab(authModalTab)
    setError(null)
  }, [authModalTab, isAuthModalOpen])

  if (!isAuthModalOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (tab === 'signup') {
      if (!fullName.trim()) {
        setError('Please enter your full name.')
        return
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters long.')
        return
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.')
        return
      }
      setIsSubmitting(true)
      const res = await signup(fullName, email, password)
      setIsSubmitting(false)
      if (!res.success) {
        setError(res.error || 'Registration failed.')
      }
    } else {
      if (!email.trim() || !password) {
        setError('Please enter both your email and password.')
        return
      }
      setIsSubmitting(true)
      const res = await login(email, password)
      setIsSubmitting(false)
      if (!res.success) {
        setError(res.error || 'Incorrect email or password.')
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
              <Lock size={16} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                {tab === 'login' ? 'Welcome Back' : 'Create Your Account'}
              </h3>
              <p className="text-xs text-slate-400">
                {tab === 'login' ? 'Access your private portfolio & chat' : 'Secure, encrypted investor account'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={closeAuthModal}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition cursor-pointer"
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab Toggle */}
        <div className="flex rounded-lg bg-slate-950 p-1 border border-slate-800">
          <button
            type="button"
            onClick={() => { setTab('login'); setError(null) }}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition cursor-pointer ${
              tab === 'login'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setTab('signup'); setError(null) }}
            className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition cursor-pointer ${
              tab === 'signup'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800/60 text-xs text-rose-300">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {tab === 'signup' && (
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <User size={13} className="text-slate-400" />
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Alex Morgan"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>
          )}

          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
              <Mail size={13} className="text-slate-400" />
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@example.com"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
              <Lock size={13} className="text-slate-400" />
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
          </div>

          {tab === 'signup' && (
            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                <Lock size={13} className="text-slate-400" />
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>
          )}

          {/* Security Notice */}
          <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-400">
            <ShieldCheck size={14} className="text-emerald-400 shrink-0" />
            <span>Encrypted with salted Bcrypt & JWT tokens. Never shared.</span>
          </div>

          <div className="pt-2">
            <Button
              type="submit"
              className="w-full justify-center"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? 'Processing...'
                : tab === 'login'
                ? 'Sign In to Emvest'
                : 'Create Account & Start Research'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

