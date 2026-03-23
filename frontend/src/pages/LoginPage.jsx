import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Card, Label, TextInput, Spinner, Alert } from 'flowbite-react'
import axios from 'axios'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleLogin(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await axios.post(
        '/api/accounts/login/',
        { username, password },
        { withCredentials: true }
      )
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-indigo-900 to-purple-900 flex items-center justify-center px-4">
      {/* Background glow effects */}
      <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full bg-blue-600/20 blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple-600/20 blur-3xl pointer-events-none" />

      <div className="relative w-full max-w-md z-10">
        {/* Logo / Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/30 mb-4">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 14l9-5-9-5-9 5 9 5zm0 0v6m0-6L3 9m9 5l9-5" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Rutabo School</h1>
          <p className="text-indigo-300 mt-1 text-sm">Management System</p>
        </div>

        {/* Card */}
        <Card className="!bg-white/5 !border-white/10 backdrop-blur-xl shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <Label htmlFor="username" value="Username" className="!text-indigo-200 font-medium" />
              <TextInput
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="mt-1"
                sizing="md"
              />
            </div>
            <div>
              <Label htmlFor="password" value="Password" className="!text-indigo-200 font-medium" />
              <TextInput
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1"
                sizing="md"
              />
            </div>

            {error && (
              <Alert color="failure" className="text-sm">
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              gradientDuoTone="purpleToBlue"
              className="w-full font-semibold"
              size="md"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Spinner size="sm" />
                  Signing in...
                </span>
              ) : 'Sign In'}
            </Button>
          </form>
        </Card>

        <p className="text-center text-indigo-400 text-xs mt-6">
          © {new Date().getFullYear()} Rutabo Secondary School · All rights reserved
        </p>
      </div>
    </div>
  )
}
