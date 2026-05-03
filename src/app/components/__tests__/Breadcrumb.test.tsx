import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Breadcrumb from '../Breadcrumb';

describe('Breadcrumb', () => {
  it('renders all breadcrumb items', () => {
    const items = [
      { label: 'Home' },
      { label: 'Health Check' },
      { label: 'Results' },
    ];

    render(<Breadcrumb items={items} />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Health Check')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
  });

  it('renders clickable links for non-last items with onClick', () => {
    const mockOnClick = vi.fn();
    const items = [
      { label: 'Home', onClick: mockOnClick },
      { label: 'Health Check', onClick: mockOnClick },
      { label: 'Results' },
    ];

    render(<Breadcrumb items={items} />);

    const homeLink = screen.getByText('Home');
    expect(homeLink.tagName).toBe('BUTTON');

    fireEvent.click(homeLink);
    expect(mockOnClick).toHaveBeenCalled();
  });

  it('renders last item as non-clickable text', () => {
    const mockOnClick = vi.fn();
    const items = [
      { label: 'Home', onClick: mockOnClick },
      { label: 'Results', onClick: mockOnClick },
    ];

    render(<Breadcrumb items={items} />);

    const resultsText = screen.getByText('Results');
    expect(resultsText.tagName).toBe('SPAN');

    // Last item should not be clickable even if onClick is provided
    fireEvent.click(resultsText);
    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it('renders separators between items', () => {
    const items = [
      { label: 'Home' },
      { label: 'Health Check' },
      { label: 'Results' },
    ];

    const { container } = render(<Breadcrumb items={items} />);

    // Should have 2 separators for 3 items
    const separators = container.querySelectorAll('svg');
    expect(separators.length).toBe(2);
  });

  it('renders single item without separator', () => {
    const items = [{ label: 'Home' }];

    const { container } = render(<Breadcrumb items={items} />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    
    // Should have no separators for single item
    const separators = container.querySelectorAll('svg');
    expect(separators.length).toBe(0);
  });

  it('handles items without onClick as non-clickable', () => {
    const items = [
      { label: 'Home' },
      { label: 'Results' },
    ];

    render(<Breadcrumb items={items} />);

    const homeText = screen.getByText('Home');
    expect(homeText.tagName).toBe('SPAN');
  });
});
