---
name: frontend
description: "Frontend development specialist for React + TypeScript + Vite + Tailwind CSS. Use when implementing UI components, pages, forms, data fetching, or any frontend TypeScript code. Enforces Suspense-first data fetching, feature-based architecture, and accessible UI design."
---

# Frontend Development Skill

You are a frontend development expert specializing in React, TypeScript, Vite, and Tailwind CSS.

## When to use this skill

- Implementing React components or pages
- Adding or updating UI data fetching (React Query, SWR)
- Setting up routing or navigation
- Writing frontend tests (Vitest, Testing Library)
- Working with forms, validation, or user input
- Working in the `frontend/` directory

## Do not use this skill when

- The task is purely backend (Python/FastAPI) — use the `backend` skill instead
- The task is infrastructure/deployment — use the `terraform` skill instead

## Core Stack

- **Language**: TypeScript (strict mode)
- **Framework**: React 18+
- **Build tool**: Vite
- **Styling**: Tailwind CSS
- **Data fetching**: React Query or SWR with Suspense
- **Testing**: Vitest + @testing-library/react
- **Target directory**: `frontend/`

## Instructions

### 1. Project Structure (Feature-Based)

```
frontend/src/
├── features/           # Feature-based modules
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── types.ts
│   └── users/
│       ├── components/
│       ├── hooks/
│       └── types.ts
├── shared/             # Shared utilities
│   ├── components/     # Reusable UI components
│   ├── hooks/
│   └── utils/
├── app/                # App-level setup (routing, providers)
└── main.tsx
```

### 2. Suspense-First Data Fetching

Always wrap data-fetching components in Suspense boundaries:

```tsx
// ✅ Correct: Suspense-first
function UsersPage() {
  return (
    <Suspense fallback={<UserListSkeleton />}>
      <ErrorBoundary fallback={<ErrorMessage />}>
        <UserList />
      </ErrorBoundary>
    </Suspense>
  );
}

function UserList() {
  const { data: users } = useSuspenseQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  return <ul>{users.map(u => <UserItem key={u.id} user={u} />)}</ul>;
}

// ❌ Incorrect: Manual loading states
function UserList() {
  const { data, isLoading, error } = useQuery(...);
  if (isLoading) return <Spinner />;
  if (error) return <Error />;
  return ...;
}
```

### 3. TypeScript Rules

- **No `any` types** — use proper generics or `unknown`
- All component props must have explicit interfaces
- Use `type` for object shapes, `interface` for extensible types
- Strict null checks: handle `undefined` and `null` explicitly

```tsx
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

interface UserCardProps {
  user: User;
  onSelect?: (userId: string) => void;
  className?: string;
}

function UserCard({ user, onSelect, className }: UserCardProps) {
  return (
    <div
      className={`rounded-lg p-4 ${className ?? ''}`}
      onClick={() => onSelect?.(user.id)}
    >
      <h3 className="font-semibold">{user.name}</h3>
      <p className="text-gray-500">{user.email}</p>
    </div>
  );
}
```

### 4. Design System

- **Dark mode**: Default with light mode support (`dark:` prefix)
- **Icons**: SVG icons only — use Heroicons or Lucide. **Never use emojis as icons.**
- **Touch targets**: Minimum 44×44px for interactive elements
- **Cursor**: `cursor-pointer` on all clickable elements
- **Transitions**: Use `transition-colors duration-200` for hover states
- **Focus states**: Always visible (never `outline-none` without alternative)

### 5. Accessibility Requirements

- All images must have meaningful `alt` text
- Form inputs must have associated `<label>` elements
- Icon-only buttons need `aria-label`
- Color is never the only indicator of state
- Tab order matches visual order
- Minimum 4.5:1 color contrast ratio for text

### 6. Component Guidelines

```tsx
// Loading state
function Skeleton() {
  return <div className="animate-pulse bg-gray-200 rounded h-4 w-full" />;
}

// Error state
function ErrorMessage({ message }: { message: string }) {
  return (
    <div role="alert" className="text-red-600 p-4 border border-red-200 rounded">
      {message}
    </div>
  );
}

// Empty state
function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-12 text-gray-500">
      <p>{message}</p>
    </div>
  );
}
```

### 7. API Client Pattern

```ts
// features/users/api/index.ts
import { apiClient } from '@/shared/api/client';

export interface UsersResponse {
  users: User[];
  total: number;
}

export async function fetchUsers(): Promise<UsersResponse> {
  const response = await apiClient.get<UsersResponse>('/api/v1/users');
  return response.data;
}
```

### 8. Testing

```tsx
import { render, screen, userEvent } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  const mockUser: User = {
    id: '1',
    name: 'Alice',
    email: 'alice@example.com',
    createdAt: new Date(),
  };

  it('renders user name and email', () => {
    // Given: a user object
    // When: UserCard is rendered
    render(<UserCard user={mockUser} />);

    // Then: name and email are displayed
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
  });
});
```

### 9. Commands

```bash
npm run dev           # development server
npm run build         # production build
npm run test          # run tests
npm run test:coverage # with coverage
npm run lint          # ESLint
npm run type-check    # TypeScript check
```

## Pre-Delivery Checklist

- [ ] No `any` types
- [ ] All Suspense boundaries in place  
- [ ] Loading, error, and empty states handled
- [ ] Accessible (alt text, labels, aria labels)
- [ ] Dark mode tested
- [ ] No emojis used as icons
- [ ] All clickable elements have `cursor-pointer`
- [ ] Tests written for new components
