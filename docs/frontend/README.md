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
