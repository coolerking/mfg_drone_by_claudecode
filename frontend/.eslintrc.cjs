module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:jsx-a11y/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh', 'jsx-a11y'],
  rules: {
    // React Refresh
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    
    // TypeScript rules
    '@typescript-eslint/no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_' 
    }],
    'react/prop-types': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
    
    // Code Quality Rules (based on quality-gates.ts)
    'complexity': ['error', { max: 10 }],
    'max-depth': ['error', { max: 4 }],
    'max-lines': ['error', { max: 300 }],
    'max-lines-per-function': ['error', { max: 50 }],
    'max-params': ['error', { max: 5 }],
    
    // Security Rules (based on quality-gates.ts SECURITY_REQUIREMENTS)
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-debugger': 'error',
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-script-url': 'error',
    
    // Accessibility Rules (Critical - based on quality-gates.ts ACCESSIBILITY_REQUIREMENTS)
    'jsx-a11y/aria-required-attr': 'error',
    'jsx-a11y/aria-valid-attr-value': 'error',
    'jsx-a11y/button-name': 'error',
    'jsx-a11y/heading-order': 'error',
    'jsx-a11y/img-alt': 'error',
    'jsx-a11y/label-has-associated-control': 'error',
    'jsx-a11y/anchor-has-content': 'error',
    'jsx-a11y/aria-role': 'error',
    'jsx-a11y/role-has-required-aria-props': 'error',
    'jsx-a11y/role-supports-aria-props': 'error',
    'jsx-a11y/tabindex-no-positive': 'error',
    
    // Accessibility Rules (Important - warnings)
    'jsx-a11y/color-contrast': 'warn',
    'jsx-a11y/landmark-one-main': 'warn',
    'jsx-a11y/page-has-heading-one': 'warn',
    'jsx-a11y/no-redundant-roles': 'warn',
    'jsx-a11y/click-events-have-key-events': 'warn',
    'jsx-a11y/mouse-events-have-key-events': 'warn',
    'jsx-a11y/no-static-element-interactions': 'warn',
    
    // Accessibility Rules (Monitor - info level)
    'jsx-a11y/html-has-lang': 'off', // Handled by index.html
    'jsx-a11y/landmark-unique': 'off', // Monitor only
    'jsx-a11y/no-duplicate-id': 'off', // Monitor only
    'jsx-a11y/meta-viewport': 'off', // Monitor only
    
    // Additional React/JSX best practices
    'react/jsx-no-target-blank': ['error', { allowReferrer: false }],
    'react/jsx-no-script-url': 'error',
    'react/no-danger': 'error',
    'react/no-danger-with-children': 'error',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  // Quality gate integration
  overrides: [
    {
      files: ['src/components/common/**/*.tsx'],
      rules: {
        'complexity': ['error', { max: 8 }],
        'max-lines-per-function': ['error', { max: 40 }],
      }
    },
    {
      files: ['src/hooks/**/*.ts'],
      rules: {
        'complexity': ['error', { max: 8 }],
        'max-lines-per-function': ['error', { max: 40 }],
      }
    },
    {
      files: ['src/utils/**/*.ts'],
      rules: {
        'complexity': ['error', { max: 12 }],
        'max-lines-per-function': ['error', { max: 60 }],
      }
    },
    {
      files: ['src/test/**/*.{ts,tsx}', '**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
      rules: {
        'max-lines-per-function': ['error', { max: 100 }],
        'no-console': 'off',
        '@typescript-eslint/no-explicit-any': 'off',
      }
    }
  ]
}