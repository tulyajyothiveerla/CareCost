from flask import Flask, render_template, jsonify, request
import sys
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

# Add scripts to path for Excel storage
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from storage_excel import read_sheet, add_row, update_row, delete_row, add_column, get_sheet_data

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/savings')
def savings():
    return render_template('savings.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/insurance')
def insurance():
    return render_template('insurance.html')

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# API Endpoints for dynamic data
@app.route('/api/expenses')
def api_expenses():
    """Get all expenses from Excel."""
    try:
        df = read_sheet('expenses')
        if df.empty:
            return jsonify([])
        
        expenses = []
        for _, row in df.iterrows():
            expenses.append({
                'date': str(row['date']),
                'amount': float(row['amount']),
                'category': row['category'],
                'notes': row['notes']
            })
        return jsonify(expenses)
    except Exception as e:
        print(f"Error reading expenses: {e}")
        return jsonify([])

@app.route('/api/dashboard')
def api_dashboard():
    """Get dashboard summary data (totals, stats)."""
    try:
        expenses_df = read_sheet('expenses')
        insurance_df = read_sheet('insurance')
        savings_df = read_sheet('savings')
        contributions_df = read_sheet('contributions')
        
        # Calculate totals
        total_expenses = 0
        month_expenses = 0
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        expenses_by_category = {}
        expenses_by_month = {}
        
        if not expenses_df.empty:
            for _, row in expenses_df.iterrows():
                amount = float(row['amount'])
                category = row['category']
                total_expenses += amount
                
                # Count by category
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0
                expenses_by_category[category] += amount
                
                # Count by month
                try:
                    exp_date = pd.to_datetime(row['date'])
                    if exp_date.month == current_month and exp_date.year == current_year:
                        month_expenses += amount
                    
                    month_key = exp_date.strftime('%Y-%m')
                    if month_key not in expenses_by_month:
                        expenses_by_month[month_key] = 0
                    expenses_by_month[month_key] += amount
                except:
                    pass
        
        # Get insurance count
        insurance_count = len(insurance_df) if not insurance_df.empty else 0
        
        # Get savings
        total_saved = 0
        if not contributions_df.empty:
            total_saved = contributions_df['amount'].sum()
        
        return jsonify({
            'totalExpenses': int(total_expenses),
            'monthExpenses': int(month_expenses),
            'totalSaved': int(total_saved),
            'insuranceCount': insurance_count,
            'expensesByCategory': {k: int(v) for k, v in expenses_by_category.items()},
            'expensesByMonth': {k: int(v) for k, v in sorted(expenses_by_month.items())}
        })
    except Exception as e:
        print(f"Error reading dashboard: {e}")
        return jsonify({
            'totalExpenses': 0,
            'monthExpenses': 0,
            'totalSaved': 0,
            'insuranceCount': 0,
            'expensesByCategory': {},
            'expensesByMonth': {}
        })

@app.route('/api/user')
def api_user():
    """Get current user profile data."""
    try:
        users_df = read_sheet('users')
        if users_df.empty:
            return jsonify({'name': 'User', 'email': 'user@email.com', 'phone': '', 'gender': 'female'})
        user = users_df.iloc[0]
        return jsonify({
            'name': user['name'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'gender': user.get('gender', 'female')
        })
    except:
        return jsonify({'name': 'User', 'email': 'user@email.com', 'phone': '', 'gender': 'female'})

@app.route('/api/insurance')
def api_insurance():
    """Get all insurance policies."""
    try:
        df = read_sheet('insurance')
        if df.empty:
            return jsonify([])
        policies = []
        for _, row in df.iterrows():
            policies.append({
                'provider': row['provider'],
                'policyNumber': row['policy_number'],
                'coverage': int(float(row['coverage'])),
                'expiry': str(row['expiry'])
            })
        return jsonify(policies)
    except Exception as e:
        print(f"Error reading insurance: {e}")
        return jsonify([])

@app.route('/api/savings')
def api_savings():
    """Get savings goal and progress."""
    try:
        savings_df = read_sheet('savings')
        contributions_df = read_sheet('contributions')
        
        goal = 0
        if not savings_df.empty:
            goal = int(float(savings_df.iloc[0]['goal']))
        
        total_saved = 0
        if not contributions_df.empty:
            total_saved = int(contributions_df['amount'].sum())
        
        return jsonify({
            'goal': goal,
            'saved': total_saved,
            'remaining': max(0, goal - total_saved),
            'percentage': int((total_saved / goal * 100) if goal > 0 else 0)
        })
    except Exception as e:
        print(f"Error reading savings: {e}")
        return jsonify({'goal': 0, 'saved': 0, 'remaining': 0, 'percentage': 0})

@app.route('/api/contributions')
def api_contributions():
    """Get all contributions."""
    try:
        df = read_sheet('contributions')
        if df.empty:
            return jsonify([])
        contributions = []
        for _, row in df.iterrows():
            contributions.append({
                'date': str(row['date']),
                'amount': int(float(row['amount']))
            })
        return jsonify(contributions)
    except:
        return jsonify([])

@app.route('/api/home')
def api_home():
    """Get home page summary data."""
    try:
        expenses_df = read_sheet('expenses')
        insurance_df = read_sheet('insurance')
        contributions_df = read_sheet('contributions')
        
        # Recent expenses
        recent_expenses = []
        if not expenses_df.empty:
            recent_df = expenses_df.sort_values('date', ascending=False).head(5)
            for _, row in recent_df.iterrows():
                recent_expenses.append({
                    'date': str(row['date']),
                    'category': row['category'],
                    'amount': int(float(row['amount'])),
                    'notes': row['notes']
                })
        
        # Summary stats
        total_expenses = int(expenses_df['amount'].sum()) if not expenses_df.empty else 0
        insurance_count = len(insurance_df)
        total_saved = int(contributions_df['amount'].sum()) if not contributions_df.empty else 0
        
        return jsonify({
            'totalExpenses': total_expenses,
            'insuranceCount': insurance_count,
            'totalSaved': total_saved,
            'recentExpenses': recent_expenses
        })
    except Exception as e:
        print(f"Error reading home: {e}")
        return jsonify({
            'totalExpenses': 0,
            'insuranceCount': 0,
            'totalSaved': 0,
            'recentExpenses': []
        })

# CRUD ENDPOINTS FOR EXPENSES
@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add a new expense."""
    try:
        data = request.json
        print(f"📩 Received expense data: {data}")
        
        required_fields = ['email', 'date', 'amount', 'category', 'notes']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            print(f"❌ Missing fields: {missing}")
            return jsonify({'error': 'Missing required fields: ' + str(missing)}), 400
        
        # Ensure amount is a number
        try:
            data['amount'] = float(data['amount'])
        except:
            print(f"❌ Invalid amount: {data['amount']}")
            return jsonify({'error': 'Amount must be a number'}), 400
        
        # Add created_at timestamp
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Ensure all fields are strings except amount
        data['email'] = str(data['email'])
        data['date'] = str(data['date'])
        data['category'] = str(data['category'])
        data['notes'] = str(data['notes'])
        
        print(f"✏️  Prepared data: {data}")
        print(f"📝 Calling add_row('expenses', ...)")
        
        add_row('expenses', data)
        
        print(f"✅ Expense saved successfully")
        return jsonify({'success': True, 'message': 'Expense added'}), 201
    except Exception as e:
        print(f"❌ Error adding expense: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:row_num>', methods=['PUT'])
def update_expense(row_num):
    """Update an expense (row_num is 1-indexed)."""
    try:
        data = request.json
        update_row('expenses', row_num, data)
        return jsonify({'success': True, 'message': 'Expense updated'})
    except Exception as e:
        print(f"Error updating expense: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:row_num>', methods=['DELETE'])
def delete_expense(row_num):
    """Delete an expense (row_num is 1-indexed)."""
    try:
        delete_row('expenses', row_num)
        return jsonify({'success': True, 'message': 'Expense deleted'})
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return jsonify({'error': str(e)}), 500

# CRUD ENDPOINTS FOR USERS
@app.route('/api/user', methods=['POST'])
def add_user():
    """Add a new user."""
    try:
        data = request.json
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        add_row('users', data)
        return jsonify({'success': True, 'message': 'User added'}), 201
    except Exception as e:
        print(f"Error adding user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:row_num>', methods=['PUT'])
def update_user(row_num):
    """Update user profile."""
    try:
        data = request.json
        update_row('users', row_num, data)
        return jsonify({'success': True, 'message': 'User updated'})
    except Exception as e:
        print(f"Error updating user: {e}")
        return jsonify({'error': str(e)}), 500

# CRUD ENDPOINTS FOR INSURANCE
@app.route('/api/insurance', methods=['POST'])
def add_insurance():
    """Add a new insurance policy."""
    try:
        data = request.json
        required_fields = ['email', 'provider', 'policy_number', 'coverage', 'expiry_date', 'status']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        add_row('insurance', data)
        return jsonify({'success': True, 'message': 'Policy added'}), 201
    except Exception as e:
        print(f"Error adding insurance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insurance/<int:row_num>', methods=['PUT'])
def update_insurance(row_num):
    """Update an insurance policy."""
    try:
        data = request.json
        update_row('insurance', row_num, data)
        return jsonify({'success': True, 'message': 'Policy updated'})
    except Exception as e:
        print(f"Error updating insurance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insurance/<int:row_num>', methods=['DELETE'])
def delete_insurance(row_num):
    """Delete an insurance policy."""
    try:
        delete_row('insurance', row_num)
        return jsonify({'success': True, 'message': 'Policy deleted'})
    except Exception as e:
        print(f"Error deleting insurance: {e}")
        return jsonify({'error': str(e)}), 500

# CRUD ENDPOINTS FOR SAVINGS
@app.route('/api/savings', methods=['POST'])
def add_savings():
    """Add/update savings goal."""
    try:
        data = request.json
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        add_row('savings', data)
        return jsonify({'success': True, 'message': 'Savings goal added'}), 201
    except Exception as e:
        print(f"Error adding savings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/savings/<int:row_num>', methods=['PUT'])
def update_savings(row_num):
    """Update savings goal."""
    try:
        data = request.json
        update_row('savings', row_num, data)
        return jsonify({'success': True, 'message': 'Savings goal updated'})
    except Exception as e:
        print(f"Error updating savings: {e}")
        return jsonify({'error': str(e)}), 500

# CRUD ENDPOINTS FOR CONTRIBUTIONS
@app.route('/api/contributions', methods=['POST'])
def add_contribution():
    """Add a new contribution to savings."""
    try:
        data = request.json
        required_fields = ['email', 'date', 'amount']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        add_row('contributions', data)
        return jsonify({'success': True, 'message': 'Contribution added'}), 201
    except Exception as e:
        print(f"Error adding contribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contributions/<int:row_num>', methods=['DELETE'])
def delete_contribution(row_num):
    """Delete a contribution."""
    try:
        delete_row('contributions', row_num)
        return jsonify({'success': True, 'message': 'Contribution deleted'})
    except Exception as e:
        print(f"Error deleting contribution: {e}")
        return jsonify({'error': str(e)}), 500

# CRUD ENDPOINTS FOR CONTACTS
@app.route('/api/contact', methods=['POST'])
def add_contact():
    """Add a new contact message."""
    try:
        data = request.json
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        add_row('contact', data)
        return jsonify({'success': True, 'message': 'Message sent'}), 201
    except Exception as e:
        print(f"Error adding contact: {e}")
        return jsonify({'error': str(e)}), 500

# UTILITY ENDPOINTS
@app.route('/api/add-column', methods=['POST'])
def api_add_column():
    """Add a new column to a sheet."""
    try:
        data = request.json
        sheet_name = data.get('sheet_name')
        column_name = data.get('column_name')
        
        if not sheet_name or not column_name:
            return jsonify({'error': 'Missing parameters'}), 400
        
        add_column(sheet_name, column_name)
        return jsonify({'success': True, 'message': f'Column {column_name} added'})
    except Exception as e:
        print(f"Error adding column: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sheet-data/<sheet_name>')
def api_sheet_data(sheet_name):
    """Get all data from a sheet."""
    try:
        data = get_sheet_data(sheet_name)
        return jsonify(data)
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
