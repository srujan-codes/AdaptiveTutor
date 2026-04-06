/**
 * App.jsx — Root component with React Router configuration.
 * Implementation: TICKET-016, TICKET-017, TICKET-018, TICKET-019
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import Layout from './components/Layout.jsx'

// Pages
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Lesson from './pages/Lesson.jsx'
import Quiz from './pages/Quiz.jsx'
import Performance from './pages/Performance.jsx'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/lesson/:id" element={<Lesson />} />
            <Route path="/quiz/:lessonId" element={<Quiz />} />
            <Route path="/performance" element={<Performance />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
