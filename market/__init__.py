import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from flask_mail import Mail
from dotenv import load_dotenv
from flask_migrate import Migrate

# -------------------------
# BASE DIRECTORY FIX
# -------------------------
basedir = os.path.abspath(os.path.dirname(__file__))

# -------------------------
# APP INIT
# -------------------------
app = Flask(__name__)

# -------------------------
# LOAD ENV FILE
# -------------------------
project_root = os.path.abspath(os.path.join(basedir, '..'))
env_path = os.path.join(project_root, '.env')

load_dotenv(env_path)

# -------------------------
# DATABASE CONFIG
# -------------------------
database_path = os.path.join(
    basedir,
    '..',
    'instance',
    'database.db'
)

os.makedirs(os.path.dirname(database_path), exist_ok=True)

database_uri = f"sqlite:///{os.path.normpath(database_path).replace(os.path.sep, '/')}"

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------------
# SECRET KEY
# -------------------------
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    '6bbfe0ca18dacabb4c4f3b66'
)

# -------------------------
# SESSION CONFIG
# -------------------------
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# -------------------------
# EMAIL CONFIG
# -------------------------
app.config['MAIL_SERVER'] = (
    os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
).strip()

app.config['MAIL_PORT'] = int(
    os.environ.get('MAIL_PORT') or 587
)

app.config['MAIL_USERNAME'] = (
    os.environ.get('MAIL_USERNAME') or ''
).strip()

app.config['MAIL_PASSWORD'] = (
    os.environ.get('MAIL_PASSWORD') or ''
).strip()

app.config['MAIL_USE_TLS'] = os.environ.get(
    'MAIL_USE_TLS',
    'True'
).lower() in ('true', '1', 'yes')

app.config['MAIL_USE_SSL'] = os.environ.get(
    'MAIL_USE_SSL',
    'False'
).lower() in ('true', '1', 'yes')

app.config['MAIL_DEFAULT_SENDER'] = (
    os.environ.get('MAIL_DEFAULT_SENDER')
    or app.config['MAIL_USERNAME']
)

app.config['MAIL_TIMEOUT'] = int(
    os.environ.get('MAIL_TIMEOUT', 15)
)

app.config['SHOW_RESET_LINK_WHEN_EMAIL_FAIL'] = os.environ.get(
    'SHOW_RESET_LINK_WHEN_EMAIL_FAIL',
    'False'
).lower() in ('true', '1', 'yes')

# -------------------------
# DEBUG PRINTS
# -------------------------
print(f" * Loading .env from: {env_path}")
print(f" * .env Exists: {os.path.exists(env_path)}")
print(f" * Database Path: {database_path}")
print(f" * Email User: {app.config['MAIL_USERNAME']}")
print(f" * Password Loaded: {bool(app.config['MAIL_PASSWORD'])}")

# -------------------------
# EXTENSIONS
# -------------------------
db = SQLAlchemy(app)

# FIXED:
# migrate must come AFTER db initialization
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message = 'Please log in first to access this page.'
login_manager.login_message_category = 'info'

Session(app)

# -------------------------
# CONTEXT PROCESSOR
# -------------------------
@app.context_processor
def inject_site_settings():

    from market.models import SiteSettings
    from sqlalchemy import select

    try:
        settings = db.session.execute(
            select(SiteSettings)
        ).scalar_one_or_none()

        # Create default settings if none exist
        if not settings:
            settings = SiteSettings(
                id=1,
                business_name='Hope Collection',
                whatsapp_number='250791641207',
                contact_email='niyonsabafabrice03@gmail.com',
                currency_code='RWF',
                delivery_fee=0
            )

            db.session.add(settings)
            db.session.commit()

    except Exception as e:

        print(f"Site settings error: {e}")

        # Fallback object prevents template crash
        class DefaultSettings:
            business_name = 'Hope Collection'
            whatsapp_number = '250791641207'
            contact_email = 'niyonsabafabrice03@gmail.com'
            currency_code = 'RWF'
            delivery_fee = 0
            facebook_url = ''
            instagram_url = ''

        settings = DefaultSettings()

    return dict(site_settings=settings)

# -------------------------
# IMPORT ROUTES
# -------------------------
from market import routes