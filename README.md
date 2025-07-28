# PyQt5 Supabase Application

This project is a PyQt5 application that integrates with a Supabase PostgreSQL database using a session pooler for efficient database connection management.

## Project Structure

```
pyqt5-supabase-app
├── src
│   ├── main.py                # Entry point of the application
│   ├── db
│   │   ├── __init__.py        # Marks the db directory as a package
│   │   └── session_pool.py     # Implements the session pooler for database connections
│   ├── ui
│   │   └── main_window.py      # Defines the main window and UI components
│   └── config
│       └── __init__.py        # Marks the config directory as a package
├── .env                        # Environment variables for the application
├── requirements.txt            # Project dependencies
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd pyqt5-supabase-app
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory and add your Supabase database connection details and any other necessary API keys.

5. **Run the application:**
   ```
   python src/main.py
   ```

## Usage Guidelines

- The application initializes a PyQt5 GUI that interacts with the Supabase PostgreSQL database.
- Use the `session_pool.py` module to manage database connections efficiently.
- Modify the `main_window.py` file to customize the user interface as needed.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.