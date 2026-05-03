import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { useAuth } from '@/app/contexts/AuthContext';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Progress } from '@/app/components/ui/progress';
import { Loader2, Check, X } from 'lucide-react';

interface PasswordStrength {
  score: number; // 0-100
  label: string;
  color: string;
  requirements: {
    minLength: boolean;
    hasUppercase: boolean;
    hasLowercase: boolean;
    hasDigit: boolean;
    hasSpecial: boolean;
  };
}

export default function SignupPage() {
  const navigate = useNavigate();
  const { signup } = useAuth();

  const [firstName, setFirstName] = useState('');
  const [middleName, setMiddleName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const calculatePasswordStrength = (pwd: string): PasswordStrength => {
    const requirements = {
      minLength: pwd.length >= 8,
      hasUppercase: /[A-Z]/.test(pwd),
      hasLowercase: /[a-z]/.test(pwd),
      hasDigit: /\d/.test(pwd),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
    };

    const metRequirements = Object.values(requirements).filter(Boolean).length;
    const score = (metRequirements / 5) * 100;

    let label = 'Weak';
    let color = 'bg-red-500';

    if (score >= 80) {
      label = 'Strong';
      color = 'bg-green-500';
    } else if (score >= 60) {
      label = 'Good';
      color = 'bg-yellow-500';
    } else if (score >= 40) {
      label = 'Fair';
      color = 'bg-orange-500';
    }

    return { score, label, color, requirements };
  };

  const passwordStrength = calculatePasswordStrength(password);

  const validateForm = (): boolean => {
    if (!firstName.trim()) {
      setError('First name is required');
      return false;
    }

    if (!surname.trim()) {
      setError('Surname is required');
      return false;
    }

    if (!email.trim()) {
      setError('Email is required');
      return false;
    }

    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return false;
    }

    if (!password) {
      setError('Password is required');
      return false;
    }

    // Check all password requirements
    if (!passwordStrength.requirements.minLength) {
      setError('Password must be at least 8 characters long');
      return false;
    }

    if (!passwordStrength.requirements.hasUppercase) {
      setError('Password must contain at least one uppercase letter');
      return false;
    }

    if (!passwordStrength.requirements.hasLowercase) {
      setError('Password must contain at least one lowercase letter');
      return false;
    }

    if (!passwordStrength.requirements.hasDigit) {
      setError('Password must contain at least one digit');
      return false;
    }

    if (!passwordStrength.requirements.hasSpecial) {
      setError('Password must contain at least one special character');
      return false;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Combine name fields into full name
      const fullName = middleName.trim() 
        ? `${firstName.trim()} ${middleName.trim()} ${surname.trim()}`
        : `${firstName.trim()} ${surname.trim()}`;
      
      await signup(fullName, email, password);
      // Navigate to home after successful signup
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const RequirementIndicator = ({ met, text }: { met: boolean; text: string }) => (
    <div className="flex items-center gap-2 text-sm">
      {met ? (
        <Check className="h-4 w-4 text-green-500" />
      ) : (
        <X className="h-4 w-4 text-gray-400" />
      )}
      <span className={met ? 'text-green-700' : 'text-gray-600'}>{text}</span>
    </div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Create an Account</CardTitle>
          <CardDescription className="text-center">
            Enter your information to get started
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input
                id="firstName"
                type="text"
                placeholder="John"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                disabled={isLoading}
                autoComplete="given-name"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="middleName">
                Middle Name <span className="text-gray-500 text-sm font-normal">(Optional)</span>
              </Label>
              <Input
                id="middleName"
                type="text"
                placeholder="Michael"
                value={middleName}
                onChange={(e) => setMiddleName(e.target.value)}
                disabled={isLoading}
                autoComplete="additional-name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="surname">Surname</Label>
              <Input
                id="surname"
                type="text"
                placeholder="Doe"
                value={surname}
                onChange={(e) => setSurname(e.target.value)}
                disabled={isLoading}
                autoComplete="family-name"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                autoComplete="email"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                autoComplete="new-password"
                required
              />

              {password && (
                <div className="space-y-2 mt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Password strength:</span>
                    <span className={`font-medium ${
                      passwordStrength.score >= 80 ? 'text-green-600' :
                      passwordStrength.score >= 60 ? 'text-yellow-600' :
                      passwordStrength.score >= 40 ? 'text-orange-600' :
                      'text-red-600'
                    }`}>
                      {passwordStrength.label}
                    </span>
                  </div>
                  <Progress value={passwordStrength.score} className="h-2" />

                  <div className="space-y-1 pt-2">
                    <RequirementIndicator
                      met={passwordStrength.requirements.minLength}
                      text="At least 8 characters"
                    />
                    <RequirementIndicator
                      met={passwordStrength.requirements.hasUppercase}
                      text="One uppercase letter"
                    />
                    <RequirementIndicator
                      met={passwordStrength.requirements.hasLowercase}
                      text="One lowercase letter"
                    />
                    <RequirementIndicator
                      met={passwordStrength.requirements.hasDigit}
                      text="One digit"
                    />
                    <RequirementIndicator
                      met={passwordStrength.requirements.hasSpecial}
                      text="One special character (!@#$%^&*...)"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                autoComplete="new-password"
                required
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Sign Up'
              )}
            </Button>

            <div className="text-sm text-center text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:underline font-medium">
                Log in
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
