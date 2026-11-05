import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { User } from '../components/ui/Icons'

const allSectors = [
  'Banking & Financial Services',
  'Information Technology',
  'Automobile & Auto Ancillary',
  'Pharmaceuticals & Healthcare',
  'Energy, Oil & Gas',
  'Fast Moving Consumer Goods (FMCG)',
  'Metals & Mining',
  'Real Estate & Infrastructure',
]

export function ProfilePage() {
  const [name, setName] = useState('Akshita Singh')
  const [email, setEmail] = useState('akshita.pb.singh@gmail.com')
  const [riskTolerance, setRiskTolerance] = useState<'Conservative' | 'Moderate' | 'Aggressive'>('Moderate')
  const [selectedSectors, setSelectedSectors] = useState<string[]>([
    'Banking & Financial Services',
    'Information Technology',
    'Automobile & Auto Ancillary',
  ])
  const [savedSuccess, setSavedSuccess] = useState(false)

  const toggleSector = (sector: string) => {
    setSelectedSectors((prev) =>
      prev.includes(sector) ? prev.filter((s) => s !== sector) : [...prev, sector]
    )
  }

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    setSavedSuccess(true)
    setTimeout(() => setSavedSuccess(false), 3000)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="pb-2 border-b border-slate-800">
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
          Investor Profile & Preferences
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Tailor your market intelligence feed, watchlist priorities, and AI risk parameters.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Account Details Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User size={18} className="text-indigo-400" />
              <CardTitle>Personal Details</CardTitle>
            </div>
            <CardDescription>Basic account and contact details.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Investment Risk Profile */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Tolerance Strategy</CardTitle>
            <CardDescription>
              Directs how the AI agent calculates risk factors and weights negative sentiment events.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {(['Conservative', 'Moderate', 'Aggressive'] as const).map((level) => (
                <div
                  key={level}
                  onClick={() => setRiskTolerance(level)}
                  className={`p-4 rounded-xl border cursor-pointer transition ${
                    riskTolerance === level
                      ? 'bg-indigo-600/15 border-indigo-500 text-white shadow-sm'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="font-bold text-sm text-white mb-1">{level}</div>
                  <p className="text-xs text-slate-400 leading-normal">
                    {level === 'Conservative' && 'Focus on high-cap dividend payers and risk minimization.'}
                    {level === 'Moderate' && 'Balanced exposure across growth leaders and value defensives.'}
                    {level === 'Aggressive' && 'Emphasis on high-beta growth momentum and early trend detection.'}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Preferred Sectors Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Sector Interests</CardTitle>
            <CardDescription>
              Select key industry sectors to prioritize in your news intelligence stream.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {allSectors.map((sector) => {
                const isSelected = selectedSectors.includes(sector)
                return (
                  <button
                    key={sector}
                    type="button"
                    onClick={() => toggleSector(sector)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition cursor-pointer ${
                      isSelected
                        ? 'bg-indigo-600 text-white border-indigo-500'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {isSelected && '✓ '}
                    {sector}
                  </button>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-2">
          {savedSuccess ? (
            <Badge variant="success" size="md">
              ✓ Preferences saved successfully! (Ready for Phase 5 persistence)
            </Badge>
          ) : (
            <span className="text-xs text-slate-400">
              Settings structured for backend persistence in Phase 5 & 6.
            </span>
          )}
          <Button type="submit">Save Preferences</Button>
        </div>
      </form>
    </div>
  )
}
