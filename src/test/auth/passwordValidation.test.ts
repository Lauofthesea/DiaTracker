import { describe, it, expect } from 'vitest';
import { validatePasswordStrength, validateEmail } from '@/lib/auth';

describe('Password Validation', () => {
  describe('validatePasswordStrength', () => {
    it('should accept a valid strong password', () => {
      const result = validatePasswordStrength('StrongP@ss123');
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject password shorter than 8 characters', () => {
      const result = validatePasswordStrength('Short1!');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters long');
    });

    it('should reject password without uppercase letter', () => {
      const result = validatePasswordStrength('lowercase123!');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one uppercase letter');
    });

    it('should reject password without lowercase letter', () => {
      const result = validatePasswordStrength('UPPERCASE123!');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one lowercase letter');
    });

    it('should reject password without digit', () => {
      const result = validatePasswordStrength('NoDigits!Pass');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one digit');
    });

    it('should reject password without special character', () => {
      const result = validatePasswordStrength('NoSpecial123');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one special character');
    });

    it('should return multiple errors for password with multiple issues', () => {
      const result = validatePasswordStrength('weak');
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(1);
    });

    it('should accept password with all special characters', () => {
      const specialChars = '!@#$%^&*(),.?":{}|<>';
      for (const char of specialChars) {
        const result = validatePasswordStrength(`Pass123${char}`);
        expect(result.valid).toBe(true);
      }
    });

    it('should handle empty password', () => {
      const result = validatePasswordStrength('');
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should accept password with exactly 8 characters meeting all requirements', () => {
      const result = validatePasswordStrength('Pass123!');
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('validateEmail', () => {
    it('should accept valid email addresses', () => {
      const validEmails = [
        'user@example.com',
        'test.user@example.com',
        'user+tag@example.co.uk',
        'user123@test-domain.com',
      ];

      validEmails.forEach((email) => {
        expect(validateEmail(email)).toBe(true);
      });
    });

    it('should reject invalid email addresses', () => {
      const invalidEmails = [
        'invalid',
        'invalid@',
        '@example.com',
        'user@',
        'user @example.com',
        'user@example',
        '',
      ];

      invalidEmails.forEach((email) => {
        expect(validateEmail(email)).toBe(false);
      });
    });
  });
});
