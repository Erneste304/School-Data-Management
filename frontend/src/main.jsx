import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { LanguageProvider } from './contexts/LanguageContext'
import { ThemeProvider } from './contexts/ThemeContext'
import './index.css'

// Ensure session cookies are sent on every fetch request (Django session auth).
// Also auto-unwrap DRF paginated responses so components get plain arrays.
const _origFetch = window.fetch;
window.fetch = function (url, opts = {}) {
  opts.credentials = opts.credentials || 'include';
  return _origFetch.call(this, url, opts).then(response => {
    // Intercept .json() on GET requests to /api/ so paginated {results:[]} is unwrapped
    if (typeof url === 'string' && url.startsWith('/api/') && response.ok) {
      const origJson = response.json.bind(response);
      response.json = () =>
        origJson().then(data => {
          // If DRF paginated: { count, next, previous, results }
          if (data && Array.isArray(data.results) && 'count' in data) {
            return data.results;
          }
          return data;
        });
    }
    return response;
  });
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <LanguageProvider>
          <App />
        </LanguageProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
