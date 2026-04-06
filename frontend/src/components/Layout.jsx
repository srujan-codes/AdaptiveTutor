/**
 * Layout — Wrapper for authenticated pages with Navbar.
 * Implementation: TICKET-016
 */

import { Outlet } from 'react-router-dom'
import Navbar from './Navbar.jsx'

export default function Layout() {
  // TODO: [TICKET-016] Add protected route logic
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
