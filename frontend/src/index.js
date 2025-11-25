import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const rootElement = document.getElementById('root');

if (!rootElement) {
  console.error('ERROR: Root element not found!');
  document.body.innerHTML = '<h1 style="color:red;padding:50px;">ERROR: Root element not found!</h1>';
} else {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

