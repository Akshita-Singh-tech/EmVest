import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { NewsPage } from './pages/NewsPage'
import { WatchlistPage } from './pages/WatchlistPage'
import { ChatbotPage } from './pages/ChatbotPage'
import { ProfilePage } from './pages/ProfilePage'
import { SettingsPage } from './pages/SettingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/news/:id" element={<NewsPage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route path="/chat" element={<ChatbotPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
