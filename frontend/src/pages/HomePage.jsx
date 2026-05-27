import { Link } from 'react-router-dom'
import { useLanguage } from '../contexts/LanguageContext'
import { 
  GraduationCap, 
  Users, 
  Calendar, 
  BookOpen, 
  MessageSquare, 
  BarChart3,
  Globe,
  Shield,
  Smartphone,
  Zap,
  Languages
} from 'lucide-react'

function HomePage() {
  const { language, changeLanguage, t } = useLanguage()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <GraduationCap className="w-10 h-10 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{t('appName')}</h1>
                <p className="text-sm text-gray-600">{t('tagline')}</p>
              </div>
            </div>
            <nav className="flex items-center space-x-4">
              <Link to="/" className="text-gray-700 hover:text-blue-600 font-medium">{t('home')}</Link>
              <Link to="/login" className="text-gray-700 hover:text-blue-600 font-medium">{t('login')}</Link>
              <Link 
                to="/register" 
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition duration-300"
              >
                {t('register')}
              </Link>
              <div className="relative group">
                <button className="flex items-center space-x-2 text-gray-700 hover:text-blue-600">
                  <Languages className="w-5 h-5" />
                  <span className="uppercase">{language}</span>
                </button>
                <div className="absolute right-0 mt-2 w-32 bg-white rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                  <button
                    onClick={() => changeLanguage('en')}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    English
                  </button>
                  <button
                    onClick={() => changeLanguage('fr')}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    Français
                  </button>
                  <button
                    onClick={() => changeLanguage('rw')}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    Kinyarwanda
                  </button>
                </div>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-800 mb-6">
            {t('heroTitle')}
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            {t('heroDescription')}
          </p>
          <div className="flex justify-center space-x-4">
            <Link 
              to="/login" 
              className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition duration-300 text-lg font-semibold"
            >
              {t('loginToAccount')}
            </Link>
            <Link 
              to="/register" 
              className="bg-white text-blue-600 border-2 border-blue-600 px-8 py-3 rounded-lg hover:bg-blue-50 transition duration-300 text-lg font-semibold"
            >
              {t('createAccount')}
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold text-center text-gray-800 mb-12">
          {t('featuresTitle')}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Users className="w-8 h-8" />}
            title={t('multiRoleSupport')}
            description={t('multiRoleDesc')}
          />
          <FeatureCard
            icon={<BookOpen className="w-8 h-8" />}
            title={t('academicManagement')}
            description={t('academicDesc')}
          />
          <FeatureCard
            icon={<Calendar className="w-8 h-8" />}
            title={t('timetableEvents')}
            description={t('timetableDesc')}
          />
          <FeatureCard
            icon={<MessageSquare className="w-8 h-8" />}
            title={t('communicationHub')}
            description={t('communicationDesc')}
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title={t('analyticsReports')}
            description={t('analyticsDesc')}
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8" />}
            title={t('secureCompliant')}
            description={t('secureDesc')}
          />
        </div>
      </section>

      {/* Innovative Features */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">
            {t('whyChooseUs')}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <InnovativeFeature icon={<Globe />} text={t('multiLanguage')} />
            <InnovativeFeature icon={<Smartphone />} text={t('mobileFriendly')} />
            <InnovativeFeature icon={<BarChart3 />} text={t('smartAnalytics')} />
            <InnovativeFeature icon={<Zap />} text={t('instantNotifications')} />
            <InnovativeFeature icon={<Shield />} text={t('gdprReady')} />
            <InnovativeFeature icon={<Users />} text={t('parentAlumni')} />
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center max-w-3xl mx-auto bg-white rounded-2xl shadow-xl p-12">
          <h3 className="text-3xl font-bold text-gray-800 mb-4">
            {t('ctaTitle')}
          </h3>
          <p className="text-gray-600 mb-8">
            {t('ctaDescription')}
          </p>
          <div className="flex justify-center space-x-4">
            <Link 
              to="/register" 
              className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition duration-300 text-lg font-semibold"
            >
              {t('getStarted')}
            </Link>
            <Link 
              to="/login" 
              className="bg-gray-200 text-gray-800 px-8 py-3 rounded-lg hover:bg-gray-300 transition duration-300 text-lg font-semibold"
            >
              {t('login')}
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <GraduationCap className="w-8 h-8" />
                <h4 className="text-xl font-bold">{t('appName')}</h4>
              </div>
              <p className="text-gray-400">
                {t('footerDescription')}
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">{t('quickLinks')}</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/" className="hover:text-white">{t('home')}</Link></li>
                <li><Link to="/login" className="hover:text-white">{t('login')}</Link></li>
                <li><Link to="/register" className="hover:text-white">{t('register')}</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">{t('contactSupport')}</h4>
              <p className="text-gray-400 mb-2">{t('needHelp')}</p>
              <p className="text-gray-400">support@schooldata.com</p>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>{t('copyright')}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition duration-300">
      <div className="text-blue-600 mb-4">{icon}</div>
      <h4 className="text-xl font-semibold text-gray-800 mb-2">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function InnovativeFeature({ icon, text }) {
  return (
    <div className="flex items-center space-x-3">
      <div className="bg-white/20 p-2 rounded-lg">{icon}</div>
      <p className="font-medium">{text}</p>
    </div>
  )
}

export default HomePage
