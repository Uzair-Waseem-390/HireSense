# HireSense Frontend

A fully functional React.js frontend for the HireSense AI-powered Resume Analyzer & Job Match Engine.

## Features

### For Normal Users:
- **Login/Register**: Secure authentication
- **Upload Resume**: Upload PDF resume with real-time processing status via WebSocket
- **Match Job**: Submit job descriptions for AI-powered matching
- **View All Resumes**: See all uploaded resumes with toggle to set active resume
- **Match History**: View all job matches with detailed results

### For Admin Users:
- **Admin Dashboard**: Direct access to admin panel after login
- **Statistics**: Platform-wide statistics and calculations
- **User Management**: View all users
- **Resume Management**: View all resumes
- **Match Management**: View all job matches

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   cd frontend/vite-project
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000 (make sure your FastAPI server is running)

## Environment Variables

Create a `.env` file in the `frontend/vite-project` directory (optional):

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/          # Reusable components (Layout, ProtectedRoute)
├── contexts/           # React contexts (AuthContext)
├── pages/              # Page components
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Dashboard.jsx
│   ├── UploadResume.jsx
│   ├── MatchJob.jsx
│   ├── MyResumes.jsx
│   ├── MatchHistory.jsx
│   └── AdminDashboard.jsx
├── services/           # API service layers
│   ├── authService.js
│   ├── resumeService.js
│   ├── jobService.js
│   ├── adminService.js
│   └── websocketService.js
└── utils/              # Utility functions
    └── api.js          # Axios configuration
```

## API Routes Connected

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Users
- `POST /users/register/` - User registration
- `GET /users/profile` - Get user profile

### Resumes
- `POST /resumes/upload` - Upload resume
- `GET /resumes/my-resume` - Get active resume
- `GET /resumes/my-resume/analysis` - Get resume analysis
- `GET /resumes/me/` - Get all user resumes
- `GET /resumes/{id}/` - Get resume by ID
- `PUT /resumes/{id}/{is_active}` - Set resume active status
- `DELETE /resumes/{id}/` - Delete resume

### Jobs
- `POST /jobs/match` - Match job description
- `POST /jobs/quick-match` - Quick match (no save)
- `GET /jobs/matches` - Get all matches
- `GET /jobs/matches/{id}` - Get match detail
- `DELETE /jobs/matches/{id}` - Delete match
- `GET /jobs/stats` - Get user stats

### Admin
- `GET /admin/stats` - Get platform statistics
- `GET /admin/users` - Get all users
- `GET /admin/resumes` - Get all resumes
- `GET /admin/matches` - Get all matches

### WebSocket
- `ws://localhost:8000/ws/updates?token={token}` - Real-time updates

## Technologies Used

- React 19
- React Router DOM
- Axios
- Tailwind CSS
- Vite

## Notes

- The frontend automatically connects to WebSocket for real-time updates during resume processing and job matching
- Admin users are automatically redirected to the admin dashboard after login
- Normal users are redirected to the dashboard where they can upload resumes and match jobs
