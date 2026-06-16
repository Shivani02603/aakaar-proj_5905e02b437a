'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { removeToken } from '@/lib/auth'

export default function Navbar() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/me', {
          credentials: 'include',
        })
        setIsAuthenticated(response.ok)
      } catch (error) {
        setIsAuthenticated(false)
      } finally {
        setIsLoading(false)
      }
    }
    checkAuth()
  }, [])

  const handleLogout = async () => {
    removeToken()
    setIsAuthenticated(false)
    router.push('/login')
    router.refresh()
  }

  return (
    <nav className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="text-xl font-bold text-blue-600">
            Aakaar Project
          </Link>
          <div className="hidden md:flex space-x-6">
            <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">
              Dashboard
            </Link>
            <Link href="/session%20management" className="text-gray-700 hover:text-blue-600 transition-colors">
              Sessions
            </Link>
            <Link href="/deployment" className="text-gray-700 hover:text-blue-600 transition-colors">
              Deployments
            </Link>
            <Link href="/backend" className="text-gray-700 hover:text-blue-600 transition-colors">
              Backends
            </Link>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {isLoading ? (
            <div className="w-20 h-8 bg-gray-200 animate-pulse rounded"></div>
          ) : isAuthenticated ? (
            <>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-50 text-red-600 hover:bg-red-100 rounded-md transition-colors font-medium"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors font-medium"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md transition-colors font-medium"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}