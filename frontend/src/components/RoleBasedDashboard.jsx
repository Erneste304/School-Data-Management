import { useState, useEffect } from 'react'
import {
  HiAcademicCap, HiUsers, HiCurrencyDollar, HiClipboardList,
  HiCalendar, HiBookOpen, HiChat, HiChartBar, HiClock
} from 'react-icons/hi'

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

// Student Dashboard
export function StudentDashboard() {
  const [profile, setProfile] = useState(null)
  const [schedule, setSchedule] = useState([])
  const [grades, setGrades] = useState([])
  const [assignmentsCount, setAssignmentsCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const opts = { credentials: 'include' };

        const profRes = await fetch('/api/academics/my-profile/', opts);
        if (profRes.ok) {
          const profData = await profRes.json();
          setProfile(profData);
        }

        const schedRes = await fetch('/api/academics/my-schedule/', opts);
        if (schedRes.ok) {
          const schedData = await schedRes.json();
          setSchedule(schedData);
        }

        const gradesRes = await fetch('/api/academics/grades/', opts);
        if (gradesRes.ok) {
          const gradesData = await gradesRes.json();
          setGrades(gradesData);
        }

        const assignRes = await fetch('/api/academics/assignments/', opts);
        const subRes = await fetch('/api/academics/submissions/', opts);
        if (assignRes.ok && subRes.ok) {
          const assignData = await assignRes.json();
          const subData = await subRes.json();
          const submittedIds = new Set(subData.map(s => s.assignment));
          const pending = assignData.filter(a => !submittedIds.has(a.id)).length;
          setAssignmentsCount(pending);
        }
      } catch (error) {
        console.error('Error fetching student dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="flex justify-center py-10"><span className="loader-blue"></span></div>;
  }

  const sInfo = profile?.student || {};

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
          Welcome back, {profile?.full_name || 'Student'}! 👋
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
          Track your academic progress and stay updated • {sInfo.current_class || 'Not assigned to a class'}
        </p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="GPA" value={sInfo.gpa !== undefined && sInfo.gpa !== null ? sInfo.gpa : 'N/A'} color="from-blue-500 to-blue-700" icon={HiAcademicCap} />
        <StatCard title="Attendance" value={sInfo.attendance_rate !== undefined && sInfo.attendance_rate !== null ? `${sInfo.attendance_rate}%` : 'N/A'} color="from-emerald-500 to-emerald-700" icon={HiClipboardList} />
        <StatCard title="Assignments" value={`${assignmentsCount} Pending`} color="from-violet-500 to-violet-700" icon={HiBookOpen} />
        <StatCard title="Upcoming Classes" value={`${schedule.length} Total`} color="from-rose-500 to-rose-700" icon={HiCalendar} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Today's Schedule</h3>
          <div className="space-y-3">
            {schedule.length > 0 ? (
              schedule.map((item, index) => (
                <ScheduleItem 
                  key={index}
                  time={`${item.start_time.substring(0, 5)} - ${item.end_time.substring(0, 5)}`}
                  subject={item.subject_name} 
                  room={item.room || 'TBD'} 
                  students={item.students}
                />
              ))
            ) : (
              <p className="text-gray-500 text-sm py-4">No classes scheduled for today.</p>
            )}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Recent Grades</h3>
          <div className="space-y-3">
            {grades.length > 0 ? (
              grades.slice(0, 5).map((item, index) => {
                const getLetter = (score) => {
                  const val = parseFloat(score);
                  if (val >= 90) return 'A';
                  if (val >= 80) return 'B';
                  if (val >= 70) return 'C';
                  if (val >= 60) return 'D';
                  return 'F';
                };
                return (
                  <GradeItem 
                    key={index}
                    subject={item.assignment_name} 
                    grade={getLetter(item.score)} 
                    score={`${item.score}%`} 
                  />
                );
              })
            ) : (
              <p className="text-gray-500 text-sm py-4">No grades recorded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Teacher Dashboard
export function TeacherDashboard() {
  const [profile, setProfile] = useState(null)
  const [schedule, setSchedule] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const opts = { credentials: 'include' };

        const profRes = await fetch('/api/academics/my-profile/', opts);
        if (profRes.ok) {
          const profData = await profRes.json();
          setProfile(profData);
        }

        const schedRes = await fetch('/api/academics/my-schedule/', opts);
        if (schedRes.ok) {
          const schedData = await schedRes.json();
          setSchedule(schedData);
        }

        const statsRes = await fetch('/api/academics/dashboard-stats/', opts);
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
      } catch (error) {
        console.error('Error fetching teacher dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="flex justify-center py-10"><span className="loader-blue"></span></div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
          Welcome back, {profile?.full_name || 'Teacher'}! 👋
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
          Manage your classes and track student progress • {profile?.role_display}
        </p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Total Students" value={stats?.total_students || 120} color="from-blue-500 to-blue-700" icon={HiUsers} />
        <StatCard title="Classes Today" value={schedule.length} color="from-emerald-500 to-emerald-700" icon={HiCalendar} />
        <StatCard title="Assignments to Grade" value="12" color="from-violet-500 to-violet-700" icon={HiBookOpen} />
        <StatCard title="Average Class Score" value="84%" color="from-rose-500 to-rose-700" icon={HiChartBar} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Today's Classes</h3>
          <div className="space-y-3">
            {schedule.length > 0 ? (
              schedule.map((item, index) => (
                <ScheduleItem 
                  key={index}
                  time={`${item.start_time.substring(0, 5)} - ${item.end_time.substring(0, 5)}`}
                  subject={`${item.subject_name} (${item.class_name})`} 
                  room={item.room || 'TBD'} 
                />
              ))
            ) : (
              <p className="text-gray-500 text-sm py-4">No active classes today.</p>
            )}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Pending Actions</h3>
          <div className="space-y-3">
            <ActionItem title="Grade Physics Quiz" priority="High" />
            <ActionItem title="Submit Lesson Plan" priority="Medium" />
            <ActionItem title="Parent Meeting" priority="Low" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Parent Dashboard
export function ParentDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Welcome back, Parent! 👋</h2>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Monitor your child's academic progress</p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Child's GPA" value="3.8" color="from-blue-500 to-blue-700" icon={HiAcademicCap} />
        <StatCard title="Attendance" value="95%" color="from-emerald-500 to-emerald-700" icon={HiClipboardList} />
        <StatCard title="Fees Due" value="RWF 150,000" color="from-violet-500 to-violet-700" icon={HiCurrencyDollar} />
        <StatCard title="Upcoming Events" value="2" color="from-rose-500 to-rose-700" icon={HiCalendar} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Child's Performance</h3>
          <div className="space-y-3">
            <GradeItem subject="Mathematics" grade="A" score="92%" />
            <GradeItem subject="Physics" grade="B+" score="88%" />
            <GradeItem subject="English" grade="A-" score="90%" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Recent Communications</h3>
          <div className="space-y-3">
            <MessageItem from="Math Teacher" message="Parent meeting scheduled for Friday" time="2 hours ago" />
            <MessageItem from="School Admin" message="Fee payment reminder" time="1 day ago" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Admin Dashboard
export function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/academics/dashboard-stats/', { credentials: 'include' });
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <div className="flex justify-center py-10"><span className="loader-blue"></span></div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Welcome back, Admin! 👋</h2>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Overview of school operations and statistics</p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Total Students" value={stats?.total_students || 0} color="from-blue-500 to-blue-700" icon={HiUsers} />
        <StatCard title="Staff Members" value={stats?.total_staff || 0} color="from-emerald-500 to-emerald-700" icon={HiUsers} />
        <StatCard title="Total Classes" value={stats?.total_classes || 0} color="from-violet-500 to-violet-700" icon={HiCurrencyDollar} />
        <StatCard title="Total Subjects" value={stats?.total_subjects || 0} color="from-rose-500 to-rose-700" icon={HiClipboardList} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Recent Activities</h3>
          <div className="space-y-3">
            <ActivityItem action="New student enrolled" user="Admin" time="10 min ago" />
            <ActivityItem action="Fee payment received" user="Finance" time="1 hour ago" />
            <ActivityItem action="Staff meeting scheduled" user="HR" time="2 hours ago" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Department Overview</h3>
          <div className="space-y-3">
            <DepartmentItem name="Academics" status="Active" />
            <DepartmentItem name="Finance" status="Active" />
            <DepartmentItem name="Discipline" status="Review" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">System Status</h3>
          <div className="space-y-3">
            <SystemStatusItem name="Database" status="Online" />
            <SystemStatusItem name="API Server" status="Online" />
            <SystemStatusItem name="Backup" status="Scheduled" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper Components
function ScheduleItem({ time, subject, room, students }) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <div className="flex items-center gap-3">
        <HiClock className="text-blue-500" />
        <div>
          <p className="font-medium text-gray-800 dark:text-white">{subject}</p>
          <p className="text-sm text-gray-500">{room} {students && `• ${students} students`}</p>
        </div>
      </div>
      <span className="text-sm text-gray-500">{time}</span>
    </div>
  )
}

function GradeItem({ subject, grade, score }) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p className="font-medium text-gray-800 dark:text-white">{subject}</p>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-500">{score}</span>
        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">{grade}</span>
      </div>
    </div>
  )
}

function ActionItem({ title, priority }) {
  const colors = {
    High: 'bg-red-100 text-red-700',
    Medium: 'bg-yellow-100 text-yellow-700',
    Low: 'bg-green-100 text-green-700'
  }
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p className="font-medium text-gray-800 dark:text-white">{title}</p>
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors[priority]}`}>{priority}</span>
    </div>
  )
}

// Extra loader style helper (defined in css)
const style = document.createElement('style');
style.textContent = `
.loader-blue {
    width: 32px;
    height: 32px;
    border: 3px solid #3b82f6;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
}
`;
document.head.appendChild(style);

function MessageItem({ from, message, time }) {
  return (
    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <p className="font-medium text-gray-800 dark:text-white">{from}</p>
        <span className="text-xs text-gray-500">{time}</span>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  )
}

function ActivityItem({ action, user, time }) {
  return (
    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p className="font-medium text-gray-800 dark:text-white">{action}</p>
      <div className="flex items-center justify-between mt-1">
        <span className="text-sm text-gray-500">by {user}</span>
        <span className="text-xs text-gray-500">{time}</span>
      </div>
    </div>
  )
}

function DepartmentItem({ name, status }) {
  const colors = {
    Active: 'bg-green-100 text-green-700',
    Review: 'bg-yellow-100 text-yellow-700'
  }
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p className="font-medium text-gray-800 dark:text-white">{name}</p>
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors[status]}`}>{status}</span>
    </div>
  )
}

function SystemStatusItem({ name, status }) {
  const colors = {
    Online: 'bg-green-100 text-green-700',
    Scheduled: 'bg-blue-100 text-blue-700'
  }
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <p className="font-medium text-gray-800 dark:text-white">{name}</p>
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${colors[status]}`}>{status}</span>
    </div>
  )
}
