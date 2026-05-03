import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router';
import ResponsiveLayout from '../ResponsiveLayout';

// Mock the navigation components
vi.mock('../BottomNav', () => ({
  default: () => <div data-testid="bottom-nav">BottomNav</div>,
}));

vi.mock('../SideNav', () => ({
  default: ({ collapsed }: { collapsed: boolean }) => (
    <div data-testid="side-nav" data-collapsed={collapsed}>
      SideNav
    </div>
  ),
}));

describe('ResponsiveLayout', () => {
  let originalInnerWidth: number;

  beforeEach(() => {
    originalInnerWidth = window.innerWidth;
  });

  afterEach(() => {
    // Restore original window width
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  const setWindowWidth = (width: number) => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: width,
    });
    window.dispatchEvent(new Event('resize'));
  };

  it('renders children content', () => {
    render(
      <BrowserRouter>
        <ResponsiveLayout>
          <div data-testid="test-content">Test Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('test-content')).toBeInTheDocument();
  });

  it('shows BottomNav on mobile viewport (767px or less)', () => {
    setWindowWidth(375); // Mobile width

    render(
      <BrowserRouter>
        <ResponsiveLayout>
          <div>Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('bottom-nav')).toBeInTheDocument();
    expect(screen.queryByTestId('side-nav')).not.toBeInTheDocument();
  });

  it('shows SideNav on tablet viewport (768px - 1023px)', () => {
    setWindowWidth(800); // Tablet width

    render(
      <BrowserRouter>
        <ResponsiveLayout>
          <div>Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('side-nav')).toBeInTheDocument();
    expect(screen.queryByTestId('bottom-nav')).not.toBeInTheDocument();
  });

  it('shows SideNav on desktop viewport (1024px or greater)', () => {
    setWindowWidth(1440); // Desktop width

    render(
      <BrowserRouter>
        <ResponsiveLayout>
          <div>Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('side-nav')).toBeInTheDocument();
    expect(screen.queryByTestId('bottom-nav')).not.toBeInTheDocument();
  });

  it('hides BottomNav when showBottomNav is false', () => {
    setWindowWidth(375); // Mobile width

    render(
      <BrowserRouter>
        <ResponsiveLayout showBottomNav={false}>
          <div>Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    expect(screen.queryByTestId('bottom-nav')).not.toBeInTheDocument();
  });

  it('applies correct padding for mobile with BottomNav', () => {
    setWindowWidth(375);

    const { container } = render(
      <BrowserRouter>
        <ResponsiveLayout>
          <div>Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    // The padding is applied to the inner div with transition-all
    const contentWrapper = container.querySelector('.transition-all');
    expect(contentWrapper).toHaveClass('pb-[80px]');
  });

  it('applies correct padding for desktop with SideNav', () => {
    setWindowWidth(1440);

    const { container } = render(
      <BrowserRouter>
        <ResponsiveLayout>
          <div>Content</div>
        </ResponsiveLayout>
      </BrowserRouter>
    );

    // The padding is applied to the inner div with transition-all
    const contentWrapper = container.querySelector('.transition-all');
    expect(contentWrapper).toHaveClass('pl-[240px]');
  });
});
