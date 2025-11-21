import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #F9FAFB;
    color: #111827;
    line-height: 1.6;
  }

  code {
    font-family: 'Fira Code', 'Courier New', monospace;
  }

  a {
    color: #002970;
    text-decoration: none;
    transition: color 0.2s ease;
  }

  a:hover {
    color: #003d99;
  }

  button {
    font-family: inherit;
    cursor: pointer;
    border: none;
    outline: none;
    transition: all 0.2s ease;
  }

  button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  input, textarea {
    font-family: inherit;
    outline: none;
  }
`;

export default GlobalStyles;

