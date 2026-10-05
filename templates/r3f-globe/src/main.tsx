import { createRoot } from 'react-dom/client';
import '@fontsource/cormorant-garamond/400.css';
import '@fontsource/cormorant-garamond/500.css';
import '@fontsource-variable/inter';
import './styles.css';
import { App } from './App';

createRoot(document.getElementById('root')!).render(<App />);
