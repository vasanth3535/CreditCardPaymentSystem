# Credit Card Payment System

## Project Overview
A credit card payment management application built with Django, Django REST Framework, FastAPI, and MySQL. It supports user authentication, card management, payment processing, transaction history, and administrative reporting.

## Features
- User registration, login, and logout using Django authentication.
- Password hashing through Django's built-in user system.
- Card creation and management with masked card numbers.
- No full card number or CVV fields in the card database model.
- FastAPI payment processing with JWT authentication.
- Payment statuses: PENDING, SUCCESS, and FAILED.
- User-specific transaction history, details, and filters.
- Django Admin management for users, cards, and transactions.
- Daily payment summary and admin-only CSV export.
- Admin activity logging.
- Django REST Framework API documentation and FastAPI Swagger.

## Technology Stack
- Python
- Django
- Django REST Framework
- FastAPI
- MySQL
- SQLAlchemy
- Simple JWT and PyJWT
- pytest and Coverage.py

## Prerequisites
- Python and pip
- MySQL Server
- A MySQL database named credit_cards_db, or the database name configured in the environment.

## Configuration
Create a `.env` file in the project root. Set these values for your local environment:

SECRET_KEY=replace_with_a_secure_secret
DB_NAME=credit_cards_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

Do not commit `.env` or share secret keys and database credentials.

## Installation
Activate the project's virtual environment, then run:

pip install -r requirements.txt

Apply database migrations:

python manage.py migrate

Create an administrator account if required:

python manage.py createsuperuser

## Running the Application
Start the Django application in one terminal:

python manage.py runserver

Start FastAPI in another terminal from the project root:

uvicorn payment_api.main:app --reload --port 8001

## Main URLs
- Django application: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/
- Daily payment summary: http://127.0.0.1:8000/admin/daily-payment-summary/
- CSV transaction export: http://127.0.0.1:8000/admin/transactions/export-csv/
- Admin activity logs: http://127.0.0.1:8000/admin/activity-logs/
- Django API documentation: http://127.0.0.1:8000/api/docs/
- FastAPI Swagger: http://127.0.0.1:8001/docs

Admin pages require an authorized staff or superuser account.

## Testing
Run Django tests:

python manage.py test users cards transactions_app -v 2

Run Django test coverage:

python -m coverage run manage.py test users cards transactions_app
python -m coverage report -m
python -m coverage html

Open `htmlcov/index.html` to view the HTML coverage report.

Run FastAPI payment tests:

python -m pytest payment_api/tests/test_payment.py -v

Run FastAPI coverage:

python -m pytest --cov=payment_api --cov-report=term-missing --cov-report=html

## Security Notes
- Django's authentication system hashes passwords.
- Protected payment API requests require a Bearer access token.
- Card and transaction access is restricted by user ownership checks.
- The card model stores masked card numbers and last four digits, not the full number or CVV.
- Use test card data only. Do not store sensitive payment authentication data.
- Keep `.env`, credentials, and production secrets out of Git.

## Day 3 Verification
The recorded Django test run passed 10 tests with 76% Django coverage. The FastAPI payment test run previously passed 6 tests with 96% coverage for the payment API module. Rerun the commands above to reproduce the results after code changes.

## Git
The project repository is initialized locally. Review `git status` and commit the verified source files with a meaningful commit message.

## Database Schema

The application uses MySQL for persistent storage.

Main tables:

- auth_user: stores user accounts and Django-hashed passwords.
- cards_card: stores the card owner, cardholder name, card type,
  masked card number, last four digits, and expiry date.
- transactions_app_transaction: stores the user, saved card, amount,
  transaction status, unique transaction reference, and creation time.

Relationships:

- One user can own multiple saved cards.
- One user can have multiple transactions.
- One saved card can be associated with multiple transactions.
- Each transaction belongs to one user and one saved card.

Payment processing:

FastAPI validates the access token and verifies that the selected
card belongs to the authenticated user. It creates a transaction
with PENDING status and then records the simulated final status as
SUCCESS or FAILED.

The Django transaction API allows authenticated users to view their
own transactions, retrieve individual transaction details, and filter
history by status, amount, or creation date.

Security:

The application stores masked card numbers rather than full card
numbers and does not store CVV values. Keep database credentials and
secret keys in the local .env file, and never commit that file.
