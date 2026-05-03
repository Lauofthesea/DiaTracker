import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../app/App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('has the correct title', () => {
    render(<App />);
    // Add more specific tests based on your App component
    expect(document.title).toBeDefined();
  });
});