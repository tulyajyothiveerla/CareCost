# CareCost  — Medical Expense Tracker

A modern web app for tracking healthcare expenses, insurance policies, savings goals, and visualizing medical costs.

## Features

- **Expense Calendar**: Track medical expenses by date with categories and notes.
- **Insurance Management**: Store and manage multiple insurance policies.
- **Savings Goals**: Plan and track medical emergency savings contributions.
- **Visualizations**: Dashboard with charts showing expense trends and summaries.
- **Profile Management**: Customize user profile with name and gender avatar.
- **Contact & Support**: Send messages to the support team.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Chart.js for visualizations)
- **Backend**: Flask (Python web framework)
- **Data Storage**: Excel workbook (`.xlsx`) with file-based persistence
- **Security**: Bcrypt for password hashing, portalocker for safe concurrent access

## Installation

### 1. Clone/navigate to project directory
```bash
cd c:\IM\ PROJECT\CareCost2.0
```

### 2. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Initialize the Excel workbook
```bash
python scripts/init_workbook.py
```

This creates `carecost_data.xlsx` with sheets for:
- `users` — user accounts
- `expenses` — medical expenses
- `insurance` — insurance policies
- `savings` — savings goal tracking
- `contributions` — savings contributions
- `contact` — contact form messages

### 4. Run the Flask app
```bash
python app.py
```

The app will start on `http://localhost:5000`. Open in your browser and log in (or sign up).

## Usage

### Data Import from Browser

If you have existing data in your browser's localStorage (from the original app), you can export and import it:

#### Export localStorage from browser:
1. Open the app in your browser
2. Press **F12** to open DevTools
3. Go to the **Console** tab
4. Run: `copy(JSON.stringify(localStorage))`
5. Paste into a text file and save as `localstorage.json`

#### Import into Excel:
```bash
python scripts/import_localstorage.py localstorage.json
```

This will:
- Create user accounts (with hashed passwords)
- Import all expenses, insurance policies, and savings data
- Create an automatic backup of the Excel file

### Data Export to JSON

Export all workbook data back to JSON format (useful for backups or syncing):

```bash
python scripts/export_localstorage.py export.json
```

## Excel Workbook Schema

### users
| Column | Type | Description |
|--------|------|-------------|
| name | text | User's full name |
| email | text | Unique email address |
| password_hash | text | Bcrypt-hashed password |
| gender | text | 'male' or 'female' (for avatar) |
| created_at | datetime | Account creation timestamp |

### expenses
| Column | Type | Description |
|--------|------|-------------|
| email | text | User's email (links to users) |
| date | date | Expense date (YYYY-MM-DD) |
| amount | number | Amount in ₹ (Indian Rupees) |
| category | text | e.g., 'Hospital', 'Medicine', 'Consultation', 'Insurance', 'Others' |
| notes | text | Additional details |
| created_at | datetime | Entry creation timestamp |

### insurance
| Column | Type | Description |
|--------|------|-------------|
| email | text | User's email |
| provider | text | Insurance company name |
| policy_number | text | Unique policy number |
| coverage | number | Coverage amount in ₹ |
| expiry_date | date | Policy expiry date (YYYY-MM-DD) |
| status | text | 'Pending', 'Approved', or 'Rejected' |
| created_at | datetime | Entry creation timestamp |

### savings
| Column | Type | Description |
|--------|------|-------------|
| email | text | User's email |
| goal_amount | number | Savings goal in ₹ |
| saved_amount | number | Current savings in ₹ |
| created_at | datetime | Record creation timestamp |

### contributions
| Column | Type | Description |
|--------|------|-------------|
| email | text | User's email |
| date | date | Contribution date (YYYY-MM-DD) |
| amount | number | Contribution amount in ₹ |
| created_at | datetime | Entry creation timestamp |

### contact
| Column | Type | Description |
|--------|------|-------------|
| name | text | Sender's name |
| email | text | Sender's email |
| message | text | Message content |
| created_at | datetime | Submission timestamp |

## File Locking & Backups

- The Excel import/export scripts use **portalocker** to prevent file corruption during concurrent access.
- A timestamped backup (e.g., `carecost_data_backup_20240219_120530.xlsx`) is created automatically before imports.
- Atomic writes ensure data integrity: changes are written to a temp file then swapped with the original.

## Current Limitations

1. **Single-threaded**: Excel is not optimized for heavy concurrent writes; works best for single or light multi-user scenarios.
2. **No real-time sync**: Data changes in the workbook require app restart or manual refresh.
3. **File-based**: Requires the workbook file to be accessible (local or shared network drive); not suitable for cloud deployments.
4. **No built-in versioning**: Keep backups for data recovery.

## Future Enhancements

- Migrate to a proper SQL database (PostgreSQL/SQLite) for scalability.
- Add server-side auth and secure session handling.
- Implement REST APIs for client-server sync.
- Add role-based access control (admin, user).
- Email notifications for insurance expiry and savings milestones.

## Troubleshooting

### "File is locked" error
- Ensure the Excel file is not open in Excel while running scripts.
- The file locking is automatic; wait a few seconds and retry.

### Import fails with "Invalid date"
- Ensure dates in the Excel file are in **YYYY-MM-DD** format.
- Example: `2024-02-19` (not `19/02/2024` or `Feb 19, 2024`).

### Script not found
- Ensure you're running from the project root directory.
- Example: `python scripts/init_workbook.py` (not `cd scripts && python init_workbook.py`).

## Development

### Running tests (if added in future)
```bash
pytest tests/
```

### Check dependencies
```bash
pip list
```

### Update requirements
```bash
pip freeze > requirements.txt
```

## License

This project is part of CareCost 2.0 and is for educational/internal use.

## Support

For issues, questions, or feature requests, use the in-app contact form or check the documentation above.

---

**Last Updated**: February 19, 2026  
**Version**: 2.0 (Excel Backend)
