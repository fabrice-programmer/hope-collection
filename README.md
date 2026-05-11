# Flask Login System with SQLite & Bootstrap

A complete Flask authentication system with user registration, login/logout functionality, and a SQLite database, styled with Bootstrap 5.

## Features

✅ User Registration with email validation  
✅ Secure Login/Logout system  
✅ Password hashing with Bcrypt  
✅ SQLite database  
✅ Bootstrap 5 responsive UI  
✅ Session management with Flask-Login  
✅ Form validation with WTForms  
✅ Protected routes (login required)  

## Project Structure

```
.
├── market/
│   ├── __init__.py          # App initialization
│   ├── models.py            # User and Item models
│   ├── forms.py             # Registration and Login forms
│   ├── routes.py            # Application routes
│   └── templates/
│       ├── base.html        # Base template with navbar
│       ├── home.html        # Home page
│       ├── login.html       # Login form
│       ├── register.html    # Registration form
│       ├── market.html      # Market page
│       └── ...
├── run.py                   # Entry point
├── create_db.py             # Database initialization
└── requirements.txt         # Dependencies
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create the Database
```bash
python create_db.py
```

### 3. Run the Application
```bash
python run.py
```

The app will be available at `http://localhost:5000`

## User Registration & Login

### Register
1. Click "Register" in the navbar
2. Enter username, email, and password
3. Account is automatically logged in after creation

### Login
1. Click "Login" in the navbar
2. Enter your username and password
3. You'll be redirected to the market page

### Logout
- Click "Logout" in the navbar (only visible when logged in)

## Database Models

### User Model
- `id` - Primary key
- `username` - Unique username
- `email_address` - Unique email
- `password_hash` - Encrypted password
- `budget` - User's budget (default: 1000)
- `items` - Relationship to items owned

### Item Model
- `id` - Primary key
- `name` - Item name
- `price` - Item price
- `barcode` - Item barcode
- `description` - Item description
- `owner` - Foreign key to User

## Routes

| Route | Method | Authentication | Purpose |
|-------|--------|---|---------|
| `/` | GET | No | Home page |
| `/register` | GET, POST | No | User registration |
| `/login` | GET, POST | No | User login |
| `/logout` | GET | Yes | User logout |
| `/market` | GET | Yes | Market page |
| `/users` | GET | No | View all users |

## Configuration

Edit `market/__init__.py` to customize:
- `SQLALCHEMY_DATABASE_URI` - Database connection string
- `SECRET_KEY` - Session encryption key (change this in production!)
- Login manager messages

## Security Notes

⚠️ **For Production:**
1. Change `SECRET_KEY` to a random secure string
2. Set `SQLALCHEMY_ECHO = False`
3. Set `DEBUG = False`
4. Use environment variables for sensitive config
5. Add CSRF protection tokens
6. Use HTTPS

## Technologies Used

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - User session management
- **Flask-Bcrypt** - Password hashing
- **WTForms** - Form handling & validation
- **Bootstrap 5** - Responsive UI
- **SQLite** - Lightweight database

## Customization

### Modify Login Manager Behavior
Edit `market/__init__.py`:
```python
login_manager.login_view = 'login_page'  # Redirect to login page
login_manager.login_message = 'Please log in first'
login_manager.login_message_category = 'info'
```

### Add More Fields to User Registration
1. Add field to `market/models.py` User model
2. Add field to `market/forms.py` RegisterForm
3. Update `market/templates/register.html`
4. Re-create database with `python create_db.py`

### Style Customization
Edit templates in `market/templates/` to modify Bootstrap classes and styling.

## Troubleshooting

### Database Issues
```bash
# Reset database
rm instance/database.db
python create_db.py
```

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Template Not Found
Check that template files are in `market/templates/` directory.

## License

MIT License - Feel free to use this project as a starting point!
