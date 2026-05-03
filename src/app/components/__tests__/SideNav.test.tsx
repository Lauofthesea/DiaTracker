import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router';
import SideNav from '../SideNav';

// Mock useNavigate and useLocation
const mockNavigate = vi.fn();
vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/' }),
  };
});

describe('SideNav', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders all navigation items', () => {
    render(
      <BrowserRouter>
        <SideNav />
      </BrowserRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Health Check')).toBeInTheDocument();
    expect(screen.getByText('Log Meal')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('renders logo and title when not collapsed', () => {
    render(
      <BrowserRouter>
        <SideNav collapsed={false} />
      </BrowserRouter>
    );

    expect(screen.getByText('Diabetes Tracker')).toBeInTheDocument();
    expect(screen.getByText('ML-Powered Health')).toBeInTheDocument();
  });

  it('hides text labels when collapsed', () => {
    render(
      <BrowserRouter>
        <SideNav collapsed={true} />
      </BrowserRouter>
    );

    expect(screen.queryByText('Home')).not.toBeInTheDocument();
    expect(screen.queryByText('Health Check')).not.toBeInTheDocument();
  });

  it('navigates to correct route when item is clicked', () => {
    render(
      <BrowserRouter>
        <SideNav />
      </BrowserRouter>
    );

    const healthCheckButton = screen.getByText('Health Check');
    fireEvent.click(healthCheckButton);

    expect(mockNavigate).toHaveBeenCalledWith('/health-check');
  });

  it('shows collapse toggle button when onToggleCollapse is provided', () => {
    const mockToggle = vi.fn();
    render(
      <BrowserRouter>
        <SideNav onToggleCollapse={mockToggle} />
      </BrowserRouter>
    );

    const toggleButton = screen.getByLabelText('Collapse sidebar');
    expect(toggleButton).toBeInTheDocument();

    fireEvent.click(toggleButton);
    expect(mockToggle).toHaveBeenCalled();
  });

  it('does not show collapse toggle button when onToggleCollapse is not provided', () => {
    render(
      <BrowserRouter>
        <SideNav />
      </BrowserRouter>
    );

    expect(screen.queryByLabelText('Collapse sidebar')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Expand sidebar')).not.toBeInTheDocument();
  });

  it('applies correct width when collapsed', () => {
    const { container } = render(
      <BrowserRouter>
        <SideNav collapsed={true} />
      </BrowserRouter>
    );

    const sideNav = container.firstChild as HTMLElement;
    expect(sideNav).toHaveClass('w-[80px]');
  });

  it('applies correct width when expanded', () => {
    const { container } = render(
      <BrowserRouter>
        <SideNav collapsed={false} />
      </BrowserRouter>
    );

    const sideNav = container.firstChild as HTMLElement;
    expect(sideNav).toHaveClass('w-[240px]');
  });
});
