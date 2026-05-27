import { createContext, useContext, useState, useEffect } from 'react'

const translations = {
  en: {
    // Header
    appName: 'School Data Management',
    tagline: 'Empowering Education Through Technology',
    home: 'Home',
    login: 'Login',
    register: 'Register',
    
    // Hero Section
    heroTitle: 'Welcome to the Future of School Management',
    heroDescription: 'A comprehensive platform for students, teachers, parents, and administrators to collaborate, manage school operations, and track academic progress in real-time.',
    loginToAccount: 'Login to Your Account',
    createAccount: 'Create Account',
    
    // Features
    featuresTitle: 'Powerful Features for Everyone',
    multiRoleSupport: 'Multi-Role Support',
    multiRoleDesc: 'Separate interfaces for students, teachers, parents, and administrators with role-based access control',
    academicManagement: 'Academic Management',
    academicDesc: 'Track grades, attendance, assignments, and exam results with comprehensive analytics',
    timetableEvents: 'Timetable & Events',
    timetableDesc: 'Interactive class schedules, event calendars, and automated reminders',
    communicationHub: 'Communication Hub',
    communicationDesc: 'Real-time messaging, announcements, and parent-teacher communication',
    analyticsReports: 'Analytics & Reports',
    analyticsDesc: 'Data-driven insights, performance trends, and detailed report cards',
    secureCompliant: 'Secure & Compliant',
    secureDesc: 'GDPR-ready data protection with secure authentication and authorization',
    
    // Innovative Features
    whyChooseUs: 'Why Choose Our Platform?',
    multiLanguage: 'Available in 3 languages (EN/FR/Kinyarwanda)',
    mobileFriendly: 'Mobile-friendly access anywhere, anytime',
    smartAnalytics: 'Smart analytics with real-time insights',
    instantNotifications: 'Instant notifications via email, SMS, or in-app',
    gdprReady: 'Secure & GDPR-ready data protection',
    parentAlumni: 'Parent and Alumni portals included',
    
    // Call to Action
    ctaTitle: 'Ready to Transform Your School Management?',
    ctaDescription: 'Join thousands of schools already using our platform to streamline operations and improve educational outcomes.',
    getStarted: 'Get Started Free',
    
    // Footer
    footerDescription: 'Empowering education through innovative technology solutions for schools worldwide.',
    quickLinks: 'Quick Links',
    contactSupport: 'Contact & Support',
    needHelp: 'Need help? Contact our support team',
    copyright: '© 2026 School Data Management. All rights reserved.',
  },
  fr: {
    // Header
    appName: 'Gestion des Données Scolaires',
    tagline: 'Autonomiser l\'éducation par la technologie',
    home: 'Accueil',
    login: 'Connexion',
    register: 'S\'inscrire',
    
    // Hero Section
    heroTitle: 'Bienvenue dans l\'avenir de la gestion scolaire',
    heroDescription: 'Une plateforme complète pour les étudiants, enseignants, parents et administrateurs pour collaborer, gérer les opérations scolaires et suivre les progrès académiques en temps réel.',
    loginToAccount: 'Connectez-vous à votre compte',
    createAccount: 'Créer un compte',
    
    // Features
    featuresTitle: 'Fonctionnalités puissantes pour tous',
    multiRoleSupport: 'Support multi-rôles',
    multiRoleDesc: 'Interfaces séparées pour les étudiants, enseignants, parents et administrateurs avec contrôle d\'accès basé sur les rôles',
    academicManagement: 'Gestion académique',
    academicDesc: 'Suivez les notes, la présence, les devoirs et les résultats des examens avec des analyses complètes',
    timetableEvents: 'Emploi du temps et événements',
    timetableDesc: 'Horaires de classe interactifs, calendriers d\'événements et rappels automatisés',
    communicationHub: 'Centre de communication',
    communicationDesc: 'Messagerie en temps réel, annonces et communication parents-enseignants',
    analyticsReports: 'Analyses et rapports',
    analyticsDesc: 'Informations basées sur les données, tendances de performance et bulletins détaillés',
    secureCompliant: 'Sécurisé et conforme',
    secureDesc: 'Protection des données conforme au RGPD avec authentification et autorisation sécurisées',
    
    // Innovative Features
    whyChooseUs: 'Pourquoi choisir notre plateforme?',
    multiLanguage: 'Disponible en 3 langues (EN/FR/Kinyarwanda)',
    mobileFriendly: 'Accès mobile-friendly n\'importe où, n\'importe quand',
    smartAnalytics: 'Analyses intelligentes avec informations en temps réel',
    instantNotifications: 'Notifications instantanées par email, SMS ou dans l\'application',
    gdprReady: 'Sécurisé et conforme au RGPD',
    parentAlumni: 'Portails parents et anciens élèves inclus',
    
    // Call to Action
    ctaTitle: 'Prêt à transformer votre gestion scolaire?',
    ctaDescription: 'Rejoignez des milliers d\'écoles utilisant déjà notre plateforme pour rationaliser les opérations et améliorer les résultats éducatifs.',
    getStarted: 'Commencer gratuitement',
    
    // Footer
    footerDescription: 'Autonomiser l\'éducation par des solutions technologiques innovantes pour les écoles du monde entier.',
    quickLinks: 'Liens rapides',
    contactSupport: 'Contact et support',
    needHelp: 'Besoin d\'aide? Contactez notre équipe de support',
    copyright: '© 2026 Gestion des Données Scolaires. Tous droits réservés.',
  },
  rw: {
    // Header
    appName: 'Gukora Ibyo Shuri',
    tagline: 'Gushyira Umusaruro mu Burezi Binyuze mu Ikoranabuhanga',
    home: 'Ahabanza',
    login: 'Kwinjira',
    register: 'Kwiyandikisha',
    
    // Hero Section
    heroTitle: 'Murakaza neza ku Burezi bwa Shuri bwa Kinyamakuru',
    heroDescription: 'Urubuga rwo gufasha abanyeshuri, abarimu, ababyeyi n\'abayobozi gukorana, gucunga imikorere ya shuri, no gukurikana ibyigezweho mu buryo bwikora',
    loginToAccount: 'Winjira kuri Konti yawe',
    createAccount: 'Kora Konti',
    
    // Features
    featuresTitle: 'Ibikorwa byiza kuri bose',
    multiRoleSupport: 'Gushigikira Abandi Benshi',
    multiRoleDesc: 'Imbuga zihisemo kuri abanyeshuri, abarimu, ababyeyi n\'abayobozi n\'uburenganzira bwihuse',
    academicManagement: 'Gucunga Burezi',
    academicDesc: 'Kurikana amanota, ubuhamya, imyitwarire n\'ibisubizo by\'amezi n\'ibikorwa byose',
    timetableEvents: 'Gahunda y\'Igihe n\'Ibikorwa',
    timetableDesc: 'Gahunda z\'ishuri zihuse, kalendari y\'ibikorwa n\'ibujyanama bikoresha',
    communicationHub: 'Ahantu hwo gutumiza',
    communicationDesc: 'Ubutumwa bwikora, amakuru n\'itumanira rwa ababyeyi n\'abarimu',
    analyticsReports: 'Ibikorwa n\'Ibikorwa',
    analyticsDesc: 'Ibisobanuro binyuze ku data, imiterere y\'akazi n\'ibikorwa byose',
    secureCompliant: 'Biteguye kandi Bihuse',
    secureDesc: 'Kurema data ihuse n\'uburenganzira bwo kwinjira no gukurikirana',
    
    // Innovative Features
    whyChooseUs: 'Ikihe niyo Impamvu za Kugura Urubuga Twaribo?',
    multiLanguage: 'Bihari mu rurimi rwa 3 (EN/FR/Kinyarwanda)',
    mobileFriendly: 'Bikora kuri telefone n\'ibindi bikoresha aho ari hose',
    smartAnalytics: 'Ibikorwa byihuse n\'ibisobanuro byikora',
    instantNotifications: 'Amakuru yihuse binyuze mu email, SMS cyangwa muri application',
    gdprReady: 'Biteguye kandi Bihuse',
    parentAlumni: 'Imbuga z\'ababyeyi n\'abasohuye zirimo',
    
    // Call to Action
    ctaTitle: 'Witeguye guhindura uburyo bwo gucunga shuri?',
    ctaDescription: 'Jya mu mashuri magana akoresha urubuga rwacu kugira ngo bakore neza imikorire yabo n\'ibyigezweho.',
    getStarted: 'Tangira Ushobora Kora',
    
    // Footer
    footerDescription: 'Gushyira umusaruro mu burezi binyuze mu ikoranabuhanga kuri mashuri yose isi',
    quickLinks: 'Amafunga Agera',
    contactSupport: 'Contact na Support',
    needHelp: 'Ugira ingorane? Twandikira',
    copyright: '© 2026 Gukora Ibyo Shuri. Uburenganzira bwose burabitswe.',
  },
}

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('en')

  useEffect(() => {
    // Load saved language preference from localStorage
    const savedLanguage = localStorage.getItem('language')
    if (savedLanguage && translations[savedLanguage]) {
      setLanguage(savedLanguage)
    }
  }, [])

  const changeLanguage = (lang) => {
    if (translations[lang]) {
      setLanguage(lang)
      localStorage.setItem('language', lang)
    }
  }

  const t = (key) => {
    return translations[language][key] || key
  }

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
