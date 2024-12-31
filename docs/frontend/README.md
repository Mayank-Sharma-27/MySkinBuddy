# Frontend Documentation

## Technology Stack

- **Framework**: Next.js 14.1.0
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Libraries**:
  - @headlessui/react - For accessible UI components
  - @heroicons/react - For icons
- **Authentication**: @react-oauth/google for Google OAuth
- **State Management**: React Context API
- **Markdown Rendering**: react-markdown

## Component Structure

### Core Components

1. **ChatWindow.tsx**

   - Main chat interface component
   - Features:
     - Real-time message handling
     - Message history management
     - Auto-scrolling to latest messages
     - Loading states
     - Authentication integration
   - Props:
     ```typescript
     interface ChatWindowProps {
       productId: string;
       chatData: ChatData;
       fullPage?: boolean;
     }
     ```

2. **ChatMessage.tsx**

   - Individual chat message component
   - Supports both user and AI messages
   - Markdown rendering for formatted responses
   - Timestamp display
   - Message metadata handling

3. **ProductAutocomplete.tsx**

   - Product search and suggestion component
   - Features:
     - Real-time search suggestions
     - Keyboard navigation
     - Product image previews
     - Brand and category filtering
   - Integration with backend search API

4. **LoginModal.tsx & LoginForm.tsx**
   - Authentication components
   - Features:
     - Email/password login
     - Google OAuth integration
     - Form validation
     - Error handling
     - Password recovery flow

### Navigation & Layout

1. **Navbar.tsx**

   - Responsive navigation component
   - Features:
     - Dynamic authentication state
     - Mobile menu
     - User profile dropdown
     - Search integration

2. **Footer.tsx**
   - Site footer component
   - Features:
     - Responsive layout
     - Social media links
     - Newsletter signup
     - Legal links

### Product Related

1. **ProductList.tsx**

   - Product display component
   - Features:
     - Grid/List view toggle
     - Pagination
     - Filtering system
     - Sort options
     - Product card display

2. **SearchBar.tsx**
   - Global search component
   - Features:
     - Instant search
     - Search history
     - Category filters
     - Recent searches

### Authentication & Protection

1. **ProtectedRoute.tsx**

   - Route protection HOC
   - Features:
     - Authentication verification
     - Role-based access
     - Redirect handling
     - Loading states

2. **RegisterForm.tsx**
   - User registration component
   - Features:
     - Form validation
     - Password requirements
     - Email verification
     - Terms acceptance

### Recent Activity

1. **RecentChats.tsx**
   - Chat history component
   - Features:
     - Chat preview
     - Timestamp sorting
     - Search/filter chats
     - Delete/archive options

## UI Components

The `ui/` directory contains atomic components:

### Button.tsx

```typescript
interface ButtonProps {
  variant?: "primary" | "secondary" | "outline" | "gradient";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
}
```

- Customizable variants
- Responsive sizing
- Loading states
- Accessibility features

### Container.tsx

- Responsive padding
- Max-width constraints
- Nested container support

### Divider.tsx

- Horizontal/vertical orientations
- Custom styling options
- Text alignment options

### Additional Components

- Input fields
- Select dropdowns
- Modal dialogs
- Toast notifications
- Loading spinners

## State Management

### Authentication Context

- User authentication state
- Login/logout methods
- Token management
- Session persistence

### Chat Context

- Active chat session
- Message history
- Loading states
- Error handling

### Product Context

- Search results
- Filters state
- Sort preferences
- View preferences

## API Integration

### Authentication Endpoints

- POST /api/auth/login
- POST /api/auth/register
- POST /api/auth/logout
- GET /api/auth/verify

### Chat Endpoints

- POST /api/chat/message
- GET /api/chat/history
- DELETE /api/chat/clear

### Product Endpoints

- GET /api/products/search
- GET /api/products/:id
- GET /api/products/suggestions

## Styling

### Tailwind Configuration

- Custom color palette
- Typography scale
- Spacing system
- Breakpoints

### Component Styles

- BEM methodology
- Utility-first approach
- Responsive design
- Dark mode support

### Theme Variables

- Color schemes
- Font families
- Border radius
- Shadow styles

## Development

### Scripts

```json
{
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "next lint"
}
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_GOOGLE_CLIENT_ID=
NEXT_PUBLIC_ENVIRONMENT=
```

### Code Organization

```
client/
├── app/
│   ├── components/
│   ├── contexts/
│   ├── hooks/
│   ├── utils/
│   └── styles/
├── public/
└── types/
```

## Performance Optimization

### Code Splitting

- Dynamic imports
- Route-based splitting
- Component lazy loading

### Image Optimization

- Next.js Image component
- Responsive images
- WebP format
- Lazy loading

### Caching Strategy

- API response caching
- Static page generation
- Incremental Static Regeneration

## Accessibility

### ARIA Labels

- Semantic HTML
- Keyboard navigation
- Screen reader support
- Focus management

### Color Contrast

- WCAG compliance
- High contrast mode
- Color blind friendly

## Testing

### Unit Tests

- Component testing
- Hook testing
- Utility function testing

### Integration Tests

- User flows
- API integration
- Authentication flows

### E2E Tests

- Critical path testing
- Cross-browser testing
- Mobile responsiveness

## Common Errors and Solutions

### Import/Export Mismatches

#### Understanding Default vs Named Exports/Imports

JavaScript/TypeScript modules have two main ways of exporting and importing code: default exports and named exports. Here's a comprehensive explanation:

##### Default Exports

- A module can only have **one** default export
- Default exports are meant to be the main exported value of a module
- They're often used for components that are the main/only export of their file
- You can import them with any name you choose

```typescript
// Exporting
export default function Button() { ... }
// or
const Button = () => { ... };
export default Button;

// Importing
import Button from './Button';      // Standard way
import CustomButton from './Button'; // Can use any name - still imports the same component
import MyButton from './Button';    // All these import the same default export
```

##### Named Exports

- A module can have multiple named exports
- Each export has a specific name that must be used when importing
- They're good for exporting multiple related functions/components
- You must use the exact name when importing (or use an alias with 'as')

```typescript
// Exporting
export function Button() { ... }
export function IconButton() { ... }
export const ButtonGroup = () => { ... }

// Importing
import { Button, IconButton } from './Button';          // Import specific exports
import { Button as CustomButton } from './Button';      // Import with alias
import * as ButtonComponents from './Button';           // Import all exports as namespace
```

##### When to Use Each

- **Use Default Exports When:**

  - The module has a main component/function
  - You're creating a component that's the primary export
  - The file contains one main piece of functionality
  - Example: `Navbar.tsx`, `Footer.tsx`

- **Use Named Exports When:**
  - You have multiple related items to export
  - You want to ensure consistent naming across imports
  - You're creating a utility file with multiple functions
  - Example: `utils.ts`, `hooks.ts`

##### Common Patterns

```typescript
// Component file with both default and named exports
export interface ButtonProps { ... }
export const ButtonTypes = { ... }
export default function Button(props: ButtonProps) { ... }

// Importing both default and named exports
import Button, { ButtonProps, ButtonTypes } from './Button';
```

##### Best Practices

1. Be consistent with your export style within your project
2. Use default exports for main components
3. Use named exports for utilities and multiple exports
4. Document your export/import patterns in your project guidelines
5. Consider using named exports when you want to ensure consistent naming

#### Error Message

```
Error: Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: undefined.
```

#### Cause

This error typically occurs when there's a mismatch between how a component is exported and how it's imported. There are two main types of exports in JavaScript/TypeScript:

1. Default exports:

```typescript
// Component file
export default function MyComponent() { ... }

// How to import
import MyComponent from './MyComponent';
```

2. Named exports:

```typescript
// Component file
export function MyComponent() { ... }

// How to import
import { MyComponent } from './MyComponent';
```

#### Solution

- Check how the component is exported in its file
- Match the import style with the export style:
  - For default exports, use: `import Name from './path'`
  - For named exports, use: `import { Name } from './path'`
- If you need to change multiple files, make sure the export/import style is consistent

#### Example

In our case, the Navbar component was using a default export:

```typescript
// Navbar.tsx
export default function Navbar() { ... }
```

But we were trying to import it as a named export:

```typescript
// Wrong
import { Navbar } from "../components/Navbar";

// Correct
import Navbar from "../components/Navbar";
```
