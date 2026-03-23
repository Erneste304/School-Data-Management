import { useState } from 'react'
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import {
  Navbar, Sidebar, Avatar, Dropdown,
  DarkThemeToggle, Badge
} from 'flowbite-react'
import {
  HiHome, HiUsers, HiAcademicCap, HiCurrencyDollar,
  HiClipboardList, HiChat, HiVideoCamera, HiShieldCheck,
  HiCalendar, HiLogout
} from 'react-icons/hi'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Overview', icon: HiHome, exact: true },
  { to: '/dashboard/students', label: 'Students', icon: HiAcademicCap },
  { to: '/dashboard/staff', label: 'Staff', icon: HiUsers },
  { to: '/dashboard/finance', label: 'Finance', icon: HiCurrencyDollar },
  { to: '/dashboard/discipline', label: 'Discipline', icon: HiClipboardList },
  { to: '/dashboard/activities', label: 'Activities', icon: HiCalendar },
  { to: '/dashboard/chat', label: 'Chat', icon: HiChat },
  { to: '/dashboard/livestream', label: 'Live Stream', icon: HiVideoCamera },
  { to: '/dashboard/audit', label: 'Audit Logs', icon: HiShieldCheck },
]

function StatCard({ title, value, color, icon: Icon }) {
  return (
    <div className={`rounded-2xl p-5 bg-gradient-to-br ${color} shadow-lg flex items-center gap-4`}>
      <div className="p-3 rounded-xl bg-white/20">
        <Icon className="text-white w-6 h-6" />
      </div>
      <div>
        <p className="text-white/70 text-sm">{title}</p>
        <p className="text-white text-2xl font-bold">{value}</p>
      </div>
    </div>
  )
}

function Overview() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Good morning 👋</h2>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Welcome back to Rutabo School Management</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Total Students" value="1,240" color="from-blue-500 to-blue-700" icon={HiAcademicCap} />
        <StatCard title="Staff Members" value="87" color="from-emerald-500 to-emerald-700" icon={HiUsers} />
        <StatCard title="Fees Collected" value="RWF 4.2M" color="from-violet-500 to-violet-700" icon={HiCurrencyDollar} />
        <StatCard title="Open Cases" value="12" color="from-rose-500 to-rose-700" icon={HiClipboardList} />
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const navigate = useNavigate()

  function handleLogout() {
    localStorage.removeItem('auth')
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 flex-shrink-0 hidden md:block`}>
        <Sidebar className="h-full border-r border-gray-200 dark:border-gray-700 !rounded-none" collapsed={!sidebarOpen}>
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            {sidebarOpen && (
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Rutabo SMS
              </span>
            )}
            <button
              onClick={() => setSidebarOpen(o => !o)}
              className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          <Sidebar.Items>
            <Sidebar.ItemGroup>
              {NAV_ITEMS.map(({ to, label, icon: Icon, exact }) => (
                <NavLink key={to} to={to} end={exact}>
                  {({ isActive }) => (
                    <Sidebar.Item
                      as="div"
                      icon={Icon}
                      className={isActive
                        ? 'bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-blue-600 dark:text-blue-400 font-semibold'
                        : ''}
                    >
                      {label}
                    </Sidebar.Item>
                  )}
                </NavLink>
              ))}
            </Sidebar.ItemGroup>
          </Sidebar.Items>
        </Sidebar>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top navbar */}
        <Navbar className="border-b border-gray-200 dark:border-gray-700 !rounded-none px-4">
          <div className="flex items-center gap-3 ml-auto">
            <DarkThemeToggle />
            <Dropdown
              arrowIcon={false}
              inline
              label={<Avatar placeholderInitials="HT" rounded size="sm" />}
            >
              <Dropdown.Header>
                <span className="block text-sm font-semibold">Head Teacher</span>
                <span className="block text-xs text-gray-500">headteacher@rutabo.rw</span>
              </Dropdown.Header>
              <Dropdown.Item icon={HiLogout} onClick={handleLogout}>
                Sign out
              </Dropdown.Item>
            </Dropdown>
          </div>
        </Navbar>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route index element={<Overview />} />
            <Route path="students" element={<ComingSoon title="Students" />} />
            <Route path="staff" element={<ComingSoon title="Staff" />} />
            <Route path="finance" element={<ComingSoon title="Finance" />} />
            <Route path="discipline" element={<ComingSoon title="Discipline" />} />
            <Route path="activities" element={<ComingSoon title="Activities" />} />
            <Route path="chat" element={<ComingSoon title="Chat" />} />
            <Route path="livestream" element={<ComingSoon title="Live Stream" />} />
            <Route path="audit" element={<ComingSoon title="Audit Logs" />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function ComingSoon({ title }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="text-5xl mb-4">🚧</div>
      <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
      <p className="text-gray-500 text-sm mt-1">This module is being connected to the API</p>
      <Badge color="indigo" className="mt-3">Coming Soon</Badge>
    </div>
  )
}
