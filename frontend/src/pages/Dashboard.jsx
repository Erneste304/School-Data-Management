import { useState } from 'react'
import { Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import {
  Navbar, Sidebar, Avatar, Dropdown,
  DarkThemeToggle, Badge
} from 'flowbite-react'
import {
  HiHome, HiUsers, HiAcademicCap, HiCurrencyDollar,
  HiClipboardList, HiChat, HiVideoCamera, HiShieldCheck,
  HiCalendar, HiLogout, HiBookOpen, HiChartBar
} from 'react-icons/hi'
import { StudentDashboard, TeacherDashboard, ParentDashboard, AdminDashboard } from '../components/RoleBasedDashboard'
import StudentManagement from '../components/StudentManagement'
import AttendanceTracking from '../components/AttendanceTracking'
import ScheduleView from '../components/ScheduleView'

const NAV_ITEMS = {
  admin: [
    { to: '/dashboard', label: 'Overview', icon: HiHome, exact: true },
    { to: '/dashboard/students', label: 'Students', icon: HiAcademicCap },
    { to: '/dashboard/staff', label: 'Staff', icon: HiUsers },
    { to: '/dashboard/finance', label: 'Finance', icon: HiCurrencyDollar },
    { to: '/dashboard/discipline', label: 'Discipline', icon: HiClipboardList },
    { to: '/dashboard/activities', label: 'Activities', icon: HiCalendar },
    { to: '/dashboard/chat', label: 'Chat', icon: HiChat },
    { to: '/dashboard/livestream', label: 'Live Stream', icon: HiVideoCamera },
    { to: '/dashboard/audit', label: 'Audit Logs', icon: HiShieldCheck },
  ],
  teacher: [
    { to: '/dashboard', label: 'Overview', icon: HiHome, exact: true },
    { to: '/dashboard/classes', label: 'My Classes', icon: HiAcademicCap },
    { to: '/dashboard/assignments', label: 'Assignments', icon: HiBookOpen },
    { to: '/dashboard/grades', label: 'Grades', icon: HiChartBar },
    { to: '/dashboard/attendance', label: 'Attendance', icon: HiClipboardList },
    { to: '/dashboard/chat', label: 'Chat', icon: HiChat },
  ],
  student: [
    { to: '/dashboard', label: 'Overview', icon: HiHome, exact: true },
    { to: '/dashboard/schedule', label: 'Schedule', icon: HiCalendar },
    { to: '/dashboard/grades', label: 'Grades', icon: HiChartBar },
    { to: '/dashboard/assignments', label: 'Assignments', icon: HiBookOpen },
    { to: '/dashboard/chat', label: 'Chat', icon: HiChat },
  ],
  parent: [
    { to: '/dashboard', label: 'Overview', icon: HiHome, exact: true },
    { to: '/dashboard/children', label: 'My Children', icon: HiAcademicCap },
    { to: '/dashboard/grades', label: 'Grades', icon: HiChartBar },
    { to: '/dashboard/fees', label: 'Fees', icon: HiCurrencyDollar },
    { to: '/dashboard/chat', label: 'Chat', icon: HiChat },
  ],
}

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const navigate = useNavigate()
  
  // Get user role from localStorage (in production, this would come from API)
  const userRole = localStorage.getItem('userRole') || 'admin'
  const navItems = NAV_ITEMS[userRole] || NAV_ITEMS.admin

  function handleLogout() {
    localStorage.removeItem('auth')
    localStorage.removeItem('userRole')
    navigate('/login')
  }

  function getDashboardComponent() {
    switch (userRole) {
      case 'student':
        return <StudentDashboard />
      case 'teacher':
        return <TeacherDashboard />
      case 'parent':
        return <ParentDashboard />
      case 'admin':
      default:
        return <AdminDashboard />
    }
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
              {navItems.map(({ to, label, icon: Icon, exact }) => (
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
              label={<Avatar placeholderInitials={userRole.charAt(0).toUpperCase()} rounded size="sm" />}
            >
              <Dropdown.Header>
                <span className="block text-sm font-semibold capitalize">{userRole}</span>
                <span className="block text-xs text-gray-500">{userRole}@rutabo.rw</span>
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
            <Route index element={getDashboardComponent()} />
            <Route path="students" element={<StudentManagement />} />
            <Route path="attendance" element={<AttendanceTracking />} />
            <Route path="schedule" element={<ScheduleView />} />
            <Route path="*" element={<ComingSoon />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function ComingSoon() {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="text-5xl mb-4">🚧</div>
      <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Under Development</h3>
      <p className="text-gray-500 text-sm mt-1">This module is being connected to the API</p>
      <Badge color="indigo" className="mt-3">Coming Soon</Badge>
    </div>
  )
}
