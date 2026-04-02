# User Authentication System

## Overview

The authentication system handles user registration, login, and session management across the application. It consists of three main parts:

1. **AuthContext** - React Context for global auth state management
2. **Login Component** - User login page
3. **Signup Component** - User registration page

**Locations:**
- AuthContext: `src/src/frontend/src/AuthContext.tsx`
- Login: `src/src/frontend/src/pages/login.tsx`
- Signup: `src/src/frontend/src/pages/signup.tsx`

---

## 1. Authentication Flow Architecture

### 1.1 High-Level Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│           User Authentication Flow                   │
└──────────────────────────────────────────────────────┘

┌─────────────────┐
│  App Component  │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│         AuthProvider (Context)                        │
│  - Manages global auth state                          │
│  - Stores token, user, userId, userData              │
│  - Provides login/logout functions                   │
└──────────────────────────────────────────────────────┘
         │
    ┌────┴─────┬──────────────┐
    │           │              │
    ▼           ▼              ▼
┌────────┐ ┌────────┐   ┌──────────┐
│ Login  │ │ Signup │   │ Protected│
│Component│ │Component│   │Components│
└────┬───┘ └───┬────┘   └──────────┘
     │         │
     └────┬────┘
          ▼
     (Auth State)
     ├─ isAuthenticated
     ├─ user (name)
     ├─ userId
     ├─ userData
     └─ loading

          │
    ┌─────▼──────────────────┐
    │   /api/auth/login      │
    │   /api/auth/signup     │
    │   /api/auth/checktoken │
    └────────────────────────┘
          │
         ▼
   ┌──────────────┐
   │ localStorage │
   │(authToken)   │
   └──────────────┘
          │
         ▼
   ┌────────────────────┐
   │ axios default      │
   │ headers.auth       │
   └────────────────────┘
```

### 1.2 Authentication States

```
┌─────────────────────────────────────────────────────┐
│              Authentication States                   │
└─────────────────────────────────────────────────────┘

1. LOADING (Initial State)
   - App just mounted
   - Checking localStorage for token
   - Verifying token with backend
   - UI shows loading indicator

2. UNAUTHENTICATED
   - No token in localStorage
   - User not logged in
   - Redirect to /login or /signup
   - Routes protected

3. AUTHENTICATED
   - Valid token in localStorage
   - User data loaded from backend
   - Can access protected routes
   - Token in axios headers
   - Can make API calls

4. TOKEN EXPIRED
   - Token still in localStorage
   - Backend rejects with 401
   - User logged out
   - Redirect to /login
```

---

## 2. AuthContext (Context Provider)

### 2.1 Context Shape

```typescript
type User = {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  // Add other user fields as needed
};

type AuthContextType = {
  isAuthenticated: boolean;   // Boolean flag
  user: string | null;        // User display name (for backward compat)
  userId: string | null;      // User ID (UUID)
  userData: User | null;      // Full user object
  loading: boolean;           // Still checking auth
  login: (token: string, user: string) => void;  // Set auth state
  logout: () => void;         // Clear auth state
};
```

### 2.2 State Variables

```typescript
const [isAuthenticated, setIsAuthenticated] = useState(false);
// Whether user has valid token

const [user, setUser] = useState<string | null>(null);
// Display name (firstName + lastName or email)

const [userId, setUserId] = useState<string | null>(null);
// Unique user ID from database

const [userData, setUserData] = useState<User | null>(null);
// Complete user object with all fields

const [loading, setLoading] = useState(true);
// True while checking auth on mount/route change
```

### 2.3 Initialization Effect

```typescript
useEffect(() => {
  const token = localStorage.getItem('authToken');
  if (token) {
    // Token exists, set it in axios headers
    axios.defaults.headers.common['authorization'] = token;
    // Verify token with backend
    checkAuthToken();
  } else {
    // No token, user is not authenticated
    setIsAuthenticated(false);
    setUser(null);
    setUserId(null);
    setUserData(null);
    delete axios.defaults.headers.common['authorization'];
    setLoading(false);
  }
}, []);
// Runs once on component mount
```

**Flow:**
1. App starts, AuthProvider mounts
2. Check localStorage for 'authToken'
3. If token exists:
   - Set it in axios default headers (for all future requests)
   - Call checkAuthToken() to verify it's valid
4. If no token:
   - Set authenticated to false
   - Clear axios headers
   - Set loading to false (skip verification)

### 2.4 Route Change Effect

```typescript
useEffect(() => {
  if (isAuthenticated) {
    checkAuthToken();
  }
}, [location.pathname]);
// Runs whenever user navigates to new page
```

**Purpose:** Re-verify auth token on each route change

**Why:** Catch if token expired while user was on current page

**Condition:** Only check if already authenticated (skip unnecessary checks)

### 2.5 checkAuthToken Function

```typescript
const checkAuthToken = async () => {
  try {
    // GET /api/auth/checktoken
    // Backend validates token and returns user data
    const response = await axios.get('/api/auth/checktoken') as { 
      data: { 
        name: string, 
        user: User 
      } 
    };
    
    const name = response.data.name;
    const userData = response.data.user;
    
    // Update state with user data
    setUser(name);
    setUserId(userData.id);
    setUserData(userData);
    setIsAuthenticated(true);
  } catch (error: any) {
    console.error(
      'Authentication failed:',
      error.response?.data?.message || error.message
    );
    // Token invalid or expired, logout user
    logout();
  } finally {
    setLoading(false);
  }
};
```

**Responsibility:**
1. Call backend to verify token is valid
2. Retrieve full user data (id, firstName, lastName, email)
3. Update all auth state variables
4. If fails: logout user (token expired/invalid)
5. Always set loading to false

**Response Expected:**
```typescript
{
  name: "John Doe",  // Display name
  user: {
    id: "uuid-12345",
    firstName: "John",
    lastName: "Doe",
    email: "john@example.com"
  }
}
```

**Error Cases:**
- 401 Unauthorized - Token expired or invalid
- 403 Forbidden - Token valid but user revoked
- 500 Server Error - Backend issue

### 2.6 login Function

```typescript
const login = (token: string, user: string) => {
  // Save token to localStorage (persists across browser restarts)
  localStorage.setItem('authToken', token);
  
  // Add token to axios default headers (all future requests have auth)
  axios.defaults.headers.common['authorization'] = token;
  
  // Update auth state immediately
  setIsAuthenticated(true);
  setUser(user);
  
  // Note: userId and userData will be set by checkAuthToken() 
  // when it's called on next route change or manually
};
```

**Called From:** Login/Signup components after successful backend auth

**Payload:**
- `token`: JWT or session token from `/api/auth/login` or `/api/auth/signup`
- `user`: Display name (e.g., "John Doe")

**What It Does:**
1. Persist token to localStorage
2. Add token to axios headers (for all API requests)
3. Set isAuthenticated and user immediately
4. userId/userData filled later by checkAuthToken()

**Flow:**
```
Login Form Submission
    ↓
POST /api/auth/login
    ↓
Success: { accessToken, name }
    ↓
login(accessToken, name)
    ↓
localStorage.setItem('authToken', token)
axios.defaults.headers['authorization'] = token
setIsAuthenticated(true)
setUser(name)
    ↓
Navigate to /dashboard
    ↓
Route change triggers second useEffect
    ↓
checkAuthToken() called
    ↓
userId and userData populated
```

### 2.7 logout Function

```typescript
const logout = () => {
  // Remove token from localStorage
  localStorage.removeItem('authToken');
  
  // Remove token from axios headers
  delete axios.defaults.headers.common['authorization'];
  
  // Clear all auth state
  setIsAuthenticated(false);
  setUser(null);
  setUserId(null);
  setUserData(null);
};
```

**Called From:**
- Dashboard component (logout button)
- checkAuthToken() on 401 error
- Anywhere app needs to force logout

**Effect:**
- Token removed from all future API requests
- All auth state cleared
- User not authenticated

### 2.8 useAuth Hook

```typescript
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
```

**Purpose:** Custom hook to access auth context

**Usage:** Any component that needs auth state

**Error Handling:** Throws if used outside AuthProvider

**Example:**
```typescript
const { isAuthenticated, user, userId, login, logout } = useAuth();
```

---

## 3. Login Component

### 3.1 Component Purpose

- Allow users to enter email and password
- Authenticate against backend
- Obtain and store auth token
- Redirect to dashboard on success

### 3.2 Component State

```typescript
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');

// From hooks/context
const { login } = useAuth();
const dispatch = useAppDispatch();
```

**State:**
- `email`: User's email input
- `password`: User's password input
- `login`: Function to update AuthContext
- `dispatch`: Redux dispatcher for alerts

**No Loading Flag:** Component doesn't track submission state (could hang on slow network)

### 3.3 API Integration

```typescript
type PostData = {
  email: string;
  password: string;
};

const postRequest = async (url: string, payload: PostData) => {
  try {
    const response = await axios.post(url, payload);
    return response.data;
  } catch (error: any) {
    console.error('Error making POST request:', error);
    throw new Error(
      error.response?.data?.message || 'Failed to make POST request'
    );
  }
};
```

**Utility Function:** Generic POST request handler

**Error Extraction:** Prefers backend error message, fallback to generic

**Response Expected:**
```typescript
{
  accessToken: "eyJhbGc...",
  name: "John Doe"
}
```

### 3.4 Form Submission Handler

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  const url = '/api/auth/login';
  const payload: PostData = { email, password };
  
  try {
    // Call backend to authenticate
    const { accessToken, name } = await postRequest(url, payload) as {
      accessToken: string;
      name: string;
    };
    
    // Update auth context with token
    login(accessToken, name);
    
    // Navigation happens automatically by useNavigate() or routing guard
  } catch (error) {
    if (error instanceof Error) {
      console.error('Login failed:', error.message);
      dispatch(showAlertWithTimeout(
        'error', 
        error.message || 'Incorrect email or password. Please try again.'
      ));
    } else {
      console.error('Login failed: An unknown error occurred.');
      dispatch(showAlertWithTimeout(
        'error', 
        'An unknown error occurred. Please try again.'
      ));
    }
  }
};
```

**Flow:**
1. Prevent default form submission
2. Prepare email and password payload
3. POST to `/api/auth/login`
4. Type-assert response (has accessToken and name)
5. Call `login()` to update AuthContext
6. On error: dispatch alert to show user
7. On success: app routing should redirect to dashboard

**Error Handling:**
- Catches specific Error instances
- Shows backend error message to user
- Fallback message if unknown error
- Logs to console for debugging

**Missing Feature:**
- No redirect to /dashboard (maybe handled by routing guard?)
- Could improve UX with loading button during submission

### 3.5 UI Layout

```jsx
<div className='container d-flex justify-content-center align-items-center vh-100'>
  <div className='card p-4 shadow' style={{ width: '400px' }}>
    <h1 className='text-center mb-4'>Login</h1>
    
    <form onSubmit={handleSubmit}>
      
      {/* Email Input */}
      <div className='mb-3'>
        <label htmlFor='email' className='form-label'>Email</label>
        <input
          type='email'
          id='email'
          className='form-control'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder='Enter your email'
          required
        />
      </div>
      
      {/* Password Input */}
      <div className='mb-3'>
        <label htmlFor='password' className='form-label'>Password</label>
        <input
          type='password'
          id='password'
          className='form-control'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder='Enter your password'
          required
        />
      </div>
      
      {/* Submit Button */}
      <button type='submit' className='btn btn-primary w-100'>
        Login
      </button>
      
    </form>
    
    {/* Link to Signup */}
    <div className='mt-3 text-center'>
      <span>Don't have an account? </span>
      <Link to='/signup'>Sign Up</Link>
    </div>
  </div>
</div>
```

**Layout:**
- Centered card (vh-100 = full viewport height)
- 400px width (mobile-friendly)
- Shadow for depth
- Responsive Bootstrap grid

**Inputs:**
- Email: type='email' for browser validation
- Password: type='password' for masking
- Both required fields

**Navigation:**
- "Sign Up" link for new users

---

## 4. Signup Component

### 4.1 Component Purpose

- Allow users to register with email and password
- Capture first and last name
- Create account on backend
- Redirect to login page on success

### 4.2 Component State

```typescript
const [firstName, setFirstName] = useState<string>('');
const [lastName, setLastName] = useState<string>('');
const [email, setEmail] = useState<string>('');
const [password, setPassword] = useState<string>('');

// From hooks
const navigate = useNavigate();
const dispatch = useAppDispatch();
```

**State:**
- `firstName`, `lastName`: User's name
- `email`, `password`: Login credentials
- `navigate`: React Router navigation
- `dispatch`: Redux dispatcher for alerts

### 4.3 API Integration

```typescript
type PostData = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
};

type ResponseData = {
  message: string;
  user: object;
};

const postRequest = async (
  url: string,
  payload: PostData
): Promise<ResponseData> => {
  try {
    const response = await axios.post<ResponseData>(url, payload);
    return response.data;
  } catch (error: any) {
    console.error('Error making POST request:', error);
    throw new Error(
      error.response?.data?.message || 'Failed to make POST request'
    );
  }
};
```

**Differences from Login:**
- Includes firstName and lastName
- Response has `message` and `user` (not `accessToken`)
- No auto-login after signup (user must login manually)

**Response Expected:**
```typescript
{
  message: "User created successfully",
  user: {
    id: "uuid-12345",
    firstName: "John",
    lastName: "Doe",
    email: "john@example.com"
  }
}
```

### 4.4 Form Submission Handler

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  const url = '/api/auth/signup';
  const payload: PostData = {
    email: email,
    password: password,
    firstName: firstName,
    lastName: lastName,
  };
  
  try {
    // Create account
    await postRequest(url, payload);
    
    // Redirect to login (user must login manually)
    navigate('/login');
  } catch (error) {
    if (error instanceof Error) {
      console.error('Signup failed:', error.message);
      dispatch(showAlertWithTimeout(
        'error', 
        error.message || 'Error with signup, please try again'
      ));
    } else {
      console.error('Signup failed: An unknown error occurred.');
      dispatch(showAlertWithTimeout(
        'error', 
        'An unknown error occurred. Please try again.'
      ));
    }
  }
};
```

**Flow:**
1. Prevent default form submission
2. Prepare payload with all user info
3. POST to `/api/auth/signup`
4. On success: navigate to `/login`
5. On error: show alert (don't navigate)

**Key Difference from Login:**
- No auto-login after signup
- User must manually login on next screen
- Allows email verification flow (if implemented)

### 4.5 UI Layout

```jsx
<div className='container d-flex justify-content-center align-items-center vh-100'>
  <div className='card p-4 shadow' style={{ width: '400px' }}>
    <h1 className='text-center mb-4'>Sign Up</h1>
    
    <form onSubmit={handleSubmit}>
      
      {/* First Name */}
      <div className='mb-3'>
        <label htmlFor='firstName' className='form-label'>First Name</label>
        <input
          type='text'
          id='firstName'
          className='form-control'
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          placeholder='Enter your first name'
          required
        />
      </div>
      
      {/* Last Name */}
      <div className='mb-3'>
        <label htmlFor='lastName' className='form-label'>Last Name</label>
        <input
          type='text'
          id='lastName'
          className='form-control'
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          placeholder='Enter your last name'
          required
        />
      </div>
      
      {/* Email */}
      <div className='mb-3'>
        <label htmlFor='email' className='form-label'>Email</label>
        <input
          type='email'
          id='email'
          className='form-control'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder='Enter your email'
          required
        />
      </div>
      
      {/* Password */}
      <div className='mb-3'>
        <label htmlFor='password' className='form-label'>Password</label>
        <input
          type='password'
          id='password'
          className='form-control'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder='Enter your password'
          required
        />
      </div>
      
      {/* Submit Button */}
      <button type='submit' className='btn btn-primary w-100'>
        Sign Up
      </button>
      
    </form>
    
    {/* Link to Login */}
    <div className='mt-3 text-center'>
      <span>Already have an account? </span>
      <Link to='/login'>Login</Link>
    </div>
  </div>
</div>
```

**Identical to Login layout except:**
- 4 form fields instead of 2
- Different button text and heading
- Different route link text

---

## 5. User Data Flow

### 5.1 Registration Flow (Signup → Login)

```
User at Signup Page
        │
        ▼
Enter: firstName, lastName, email, password
        │
        ▼
handleSubmit()
        │
        ▼
POST /api/auth/signup
  ├─ firstName
  ├─ lastName
  ├─ email
  └─ password
        │
        ▼
Backend Creates User
  ├─ Validates email not taken
  ├─ Hashes password
  ├─ Creates user record
  └─ Returns success
        │
        ▼
navigate('/login')
        │
        ▼
User at Login Page
        │
        ▼
Enter: email, password
        │
        ▼
(See Login Flow Below)
```

### 5.2 Login Flow (Authentication)

```
User at Login Page
        │
        ▼
Enter: email, password
        │
        ▼
handleSubmit()
        │
        ▼
POST /api/auth/login
  ├─ email
  └─ password
        │
        ▼
Backend Authenticates
  ├─ Find user by email
  ├─ Verify password hash
  ├─ Generate JWT/Session token
  └─ Return: { accessToken, name }
        │
        ▼
login(accessToken, name)
        │
        ├─ localStorage.setItem('authToken', token)
        │
        ├─ axios.defaults.headers['authorization'] = token
        │
        ├─ setIsAuthenticated(true)
        │
        └─ setUser(name)
        │
        ▼
App Router Redirects (or component navigates)
        │
        ▼
Route Change → /dashboard
        │
        ▼
Second useEffect Triggers
  └─ checkAuthToken()
        │
        ▼
GET /api/auth/checktoken (with token in header)
        │
        ▼
Backend Validates Token
  ├─ Decode JWT
  ├─ Verify signature
  ├─ Fetch full user data
  └─ Return: { name, user: { id, firstName, lastName, email } }
        │
        ▼
Update State:
  ├─ setUser(name)
  ├─ setUserId(userData.id)
  └─ setUserData(userData)
        │
        ▼
Dashboard Component Renders
  └─ Access: { user, userId, userData } from context
```

### 5.3 Token Persistence

```
Session Start (Page Reload)
        │
        ▼
AuthProvider mounts
        │
        ▼
First useEffect fires
        │
        ▼
const token = localStorage.getItem('authToken')
        │
        ├─ Token found
        │   ├─ axios.defaults.headers['authorization'] = token
        │   └─ checkAuthToken() → Verify token valid
        │
        └─ No token
            ├─ setIsAuthenticated(false)
            └─ setLoading(false)
```

---

## 6. Token Management

### 6.1 Token Storage

```typescript
// Login
localStorage.setItem('authToken', token);

// Logout
localStorage.removeItem('authToken');

// On app startup
const token = localStorage.getItem('authToken');
```

**Storage Location:** Browser localStorage
**Persistence:** Survives page reloads and browser restarts
**Security:** Accessible to XSS attacks (not HttpOnly like server-side would be)

### 6.2 Token in API Requests

```typescript
// Set in context
axios.defaults.headers.common['authorization'] = token;

// All subsequent requests include:
headers: {
  authorization: 'eyJhbGc...'
}
```

**Scope:** All axios requests (global default)
**Format:** Bearer token or JWT (backend-specific)
**Removed:** On logout via `delete axios.defaults.headers.common['authorization']`

### 6.3 Token Verification Flow

```
On Route Change
    │
    ├─ location.pathname changes
    │
    ├─ if isAuthenticated
    │   └─ checkAuthToken()
    │
    └─ GET /api/auth/checktoken
        ├─ Backend validates token
        ├─ If valid → Return user data
        ├─ If expired → 401 error
        │   └─ logout() called
        └─ User redirected to /login
```

**Timing:** Every navigation (could be optimized with longer cache TTL)

**Cost:** Extra backend call per page navigation

**Benefit:** Catches token expiration immediately

---

## 7. Error Handling

### 7.1 Login Errors

| Error | Cause | User Message |
|-------|-------|-------------|
| Email not found | User doesn't exist | "Incorrect email or password" |
| Password incorrect | Wrong password | "Incorrect email or password" |
| Account disabled | Admin action | Backend error message |
| Server error | Backend crash | "Failed to make POST request" |
| Network error | No internet | "Failed to make POST request" |

**Strategy:** Generic message for security (don't reveal if email exists)

### 7.2 Signup Errors

| Error | Cause | User Message |
|-------|-------|-------------|
| Email taken | User already exists | Backend error message |
| Invalid email | Bad format | Backend validation message |
| Weak password | Doesn't meet requirements | Backend validation message |
| Server error | Backend crash | "Error with signup, please try again" |
| Network error | No internet | "An unknown error occurred" |

**Strategy:** Show validation errors (helps user fix input)

### 7.3 Token Verification Errors

| Error | Cause | Handler |
|-------|-------|---------|
| 401 Unauthorized | Token expired | logout() |
| 403 Forbidden | User revoked | logout() |
| Network error | Connection lost | logout() |
| Server error | Backend down | logout() |

**Strategy:** Any error → logout and require re-login

---

## 8. Security Considerations

### 8.1 Token Security

**Current Implementation:**
- Tokens stored in localStorage (XSS vulnerable)
- Sent in Authorization header (CSRF safe with default axios)
- No HttpOnly flag (server-side cookies more secure)
- No Secure flag check (might be HTTP in dev)

**Improvements:**
```typescript
// Set HttpOnly, Secure, SameSite in backend
Set-Cookie: authToken=...; HttpOnly; Secure; SameSite=Strict

// Frontend uses credentials:
axios.defaults.withCredentials = true;
```

### 8.2 Password Handling

**Current Implementation:**
- Password sent over HTTPS (assumed by backend)
- Hashed on backend (assumed)
- No client-side validation shown

**Improvements:**
```typescript
// Add client-side validation
const validatePassword = (password: string) => {
  return password.length >= 8 &&
         /[A-Z]/.test(password) &&
         /[0-9]/.test(password) &&
         /[^A-Za-z0-9]/.test(password);
};
```

### 8.3 Email Validation

**Current Implementation:**
- HTML5 `type='email'` only (client-side)
- Backend should validate

**Improvements:**
```typescript
// Add confirmation email flow
// Only allow login after email verified
```

### 8.4 Token Expiration

**Current Implementation:**
- Checked on each route change
- No refresh token shown

**Improvements:**
```typescript
// Implement refresh token flow
// Issue short-lived access token + long-lived refresh token
// Use refresh token to get new access token when expired
```

---

## 9. Component Integration

### 9.1 Auth Flow in App

```typescript
// In App.tsx (or index.tsx)
<AuthProvider>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/signup" element={<Signup />} />
    
    {/* Protected routes */}
    <Route 
      path="/dashboard" 
      element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } 
    />
  </Routes>
</AuthProvider>
```

### 9.2 ProtectedRoute Component (Not Shown)

Expected to exist but not in provided files:

```typescript
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};
```

### 9.3 Using Auth in Components

```typescript
const Dashboard: React.FC = () => {
  const { user, userId, userData, logout } = useAuth();
  
  return (
    <div>
      <h1>Welcome, {user}!</h1>
      <p>Your ID: {userId}</p>
      <p>Email: {userData?.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
};
```

---

## 10. State Transitions

### 10.1 State Machine

```
┌─────────────┐
│   LOADING   │  (App starts)
└──────┬──────┘
       │
       ├─ Token in localStorage?
       │
       ├─ Yes → Verify token
       │   ├─ Valid → AUTHENTICATED
       │   └─ Invalid → UNAUTHENTICATED
       │
       └─ No → UNAUTHENTICATED
                   │
                   ▼
         ┌──────────────────────┐
         │  UNAUTHENTICATED     │
         │  (Show Login/Signup) │
         └──────────┬───────────┘
                    │
                    ├─ User clicks Login
                    │  └─ Enter credentials
                    │     └─ POST /login
                    │        ├─ Success → login() → AUTHENTICATED
                    │        └─ Fail → Show error, stay UNAUTHENTICATED
                    │
                    └─ User clicks Signup
                       └─ Enter credentials
                          └─ POST /signup
                             ├─ Success → Navigate to /login
                             └─ Fail → Show error, stay UNAUTHENTICATED
                                 │
                                 ▼
         ┌──────────────────────┐
         │  AUTHENTICATED       │
         │  (Show Dashboard)    │
         └──────────┬───────────┘
                    │
                    ├─ User navigates
                    │  └─ checkAuthToken()
                    │     ├─ Valid → Stay AUTHENTICATED
                    │     └─ Invalid → logout() → UNAUTHENTICATED
                    │
                    └─ User clicks Logout
                       └─ logout() → UNAUTHENTICATED
```

---

## 11. API Endpoints

### 11.1 Endpoint Details

| Method | Endpoint | Purpose | Request | Response | Status |
|--------|----------|---------|---------|----------|--------|
| POST | `/api/auth/signup` | Register new user | `{ firstName, lastName, email, password }` | `{ message, user }` | 201 or 400 |
| POST | `/api/auth/login` | Authenticate user | `{ email, password }` | `{ accessToken, name }` | 200 or 401 |
| GET | `/api/auth/checktoken` | Verify token valid | (Token in header) | `{ name, user }` | 200 or 401 |

### 11.2 Request/Response Examples

**Signup Request:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Signup Response (Success):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  }
}
```

**Login Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Login Response (Success):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "name": "John Doe"
}
```

**CheckToken Request:**
```
GET /api/auth/checktoken
Headers: {
  Authorization: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**CheckToken Response (Success):**
```json
{
  "name": "John Doe",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  }
}
```

---

## 12. localStorage Keys

| Key | Value | Type | Set By | Used By | Cleared By |
|-----|-------|------|--------|---------|-----------|
| `authToken` | JWT/Session token | string | `login()` | axios headers | `logout()` |

---

## 13. TypeScript Interfaces

```typescript
// User data type
interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
}

// Auth context type
interface AuthContextType {
  isAuthenticated: boolean;
  user: string | null;
  userId: string | null;
  userData: User | null;
  loading: boolean;
  login: (token: string, user: string) => void;
  logout: () => void;
}

// Login/Signup request
interface PostData {
  email: string;
  password: string;
  // Signup only:
  firstName?: string;
  lastName?: string;
}

// Auth responses
interface SignupResponse {
  message: string;
  user: User;
}

interface LoginResponse {
  accessToken: string;
  name: string;
}

interface CheckTokenResponse {
  name: string;
  user: User;
}
```

---

## 14. Testing Scenarios

### 14.1 Happy Path

```
1. User navigates to /signup
2. Fills form (firstName, lastName, email, password)
3. Clicks "Sign Up"
4. ✓ Account created
5. ✓ Redirected to /login
6. ✓ Fills email/password
7. ✓ Clicks "Login"
8. ✓ Token received and stored
9. ✓ Redirected to /dashboard
10. ✓ User data displayed
```

### 14.2 Edge Cases

**Duplicate Email:**
- Signup with existing email → Error shown
- Should not create duplicate account

**Wrong Password:**
- Login with correct email, wrong password → Generic error
- Should not reveal if email exists

**Token Expiration:**
- User logged in, token expires
- Navigate to new page → checkAuthToken fails
- User logged out, redirected to /login

**Lost Connection:**
- Network error during login → Error shown
- Page still functional, can retry

---

## 15. Common Issues and Debugging

### 15.1 Issue: "useAuth must be used within an AuthProvider"

**Cause:** Component using `useAuth()` but not wrapped in `<AuthProvider>`

**Solution:**
```typescript
// In App.tsx
<AuthProvider>
  <YourComponent /> {/* Can now use useAuth */}
</AuthProvider>
```

### 15.2 Issue: Token not persisting across page reload

**Cause:** localStorage not working (private browsing, storage disabled)

**Solution:** Check DevTools → Application → Storage

### 15.3 Issue: Infinite redirect loop

**Cause:** ProtectedRoute redirects to /login, but checkAuthToken keeps failing

**Solution:** Verify `/api/auth/checktoken` works and returns 401 on expired token

### 15.4 Issue: axios requests missing Authorization header

**Cause:** `login()` not called, or header deletion in logout failed

**Solution:**
```typescript
console.log(axios.defaults.headers.common['authorization']);
// Should show token after login
```

### 15.5 Issue: User data undefined in components

**Cause:** Accessing `userData` before `checkAuthToken()` completes

**Solution:** Check `loading` flag first
```typescript
if (loading) return <div>Loading...</div>;
if (!userData) return <div>No user data</div>;
return <div>{userData.firstName}</div>;
```

---

## 16. Performance Considerations

### 16.1 Token Verification Overhead

**Current:** Verify on every route change

**Cost:** 
- Extra HTTP request per navigation
- Typically less than 100 ms, but adds up

**Optimization Options:**

```typescript
// Option 1: Cache validation for X seconds
const [lastCheckTime, setLastCheckTime] = useState(0);
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

useEffect(() => {
  if (isAuthenticated && Date.now() - lastCheckTime > CACHE_TTL) {
    checkAuthToken();
    setLastCheckTime(Date.now());
  }
}, [location.pathname]);

// Option 2: Verify only if approaching expiration
const getTokenExpiration = (token: string) => {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return payload.exp * 1000; // Convert to milliseconds
};

const isTokenExpiringSoon = (token: string, buffer = 60000) => {
  return getTokenExpiration(token) < Date.now() + buffer;
};
```

### 16.2 Component Render Optimization

**Issue:** All components re-render when auth state changes

**Solution:** Use context selectors or Redux for fine-grained updates

```typescript
// Instead of useAuth() (returns whole context)
// Use selector
const user = useAuthSelector(state => state.user);
```

---

## 17. Related Files

| File | Relationship |
|------|---------|
| `App.tsx` | Should wrap routes in AuthProvider |
| `Dashboard.tsx` | Uses useAuth for user info and logout |
| `canvas.tsx` | May need userId for saving diagrams |
| `dataRoutes.ts` (backend) | Implements /api/auth/* endpoints |
| `authController.ts` (backend) | Business logic for signup/login |
| `ProtectedRoute.tsx` | Guards routes that require auth |

---

## 18. Authentication Checklist

### Frontend Implementation
- [x] AuthContext with login/logout
- [x] Login component with form
- [x] Signup component with form
- [x] Token storage in localStorage
- [x] Token in axios headers
- [x] Token verification on route change
- [ ] ProtectedRoute component (NOT SHOWN - should exist)
- [ ] Loading state in ProtectedRoute
- [ ] Redirect to login on 401
- [ ] Redirect to dashboard on login

### Backend Implementation (Assumed)
- [x] POST /api/auth/signup - Create user
- [x] POST /api/auth/login - Authenticate user
- [x] GET /api/auth/checktoken - Verify token
- [ ] Implement refresh token flow
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after N failed attempts
- [ ] Email verification flow
- [ ] Password reset flow

### Security
- [ ] Move token to HttpOnly cookie
- [ ] Add CSRF protection
- [ ] Add password strength validation
- [ ] Add rate limiting
- [ ] Add email verification
- [ ] Add 2FA support

---

## 19. Summary

The authentication system provides:

1. **Registration** via Signup component
2. **Authentication** via Login component
3. **Session Management** via AuthContext
4. **Token Persistence** via localStorage
5. **Automatic Token Verification** on route changes
6. **Global Auth State** accessible via useAuth hook

**Key Flow:**
User → Login/Signup → POST /api/auth → Token received → localStorage + axios headers → Dashboard accessible → checkAuthToken() on each navigation → logout() to clear state

