import sqlite3
import csv
import bcrypt
from fpdf import FPDF

connect = sqlite3.connect('Capstone.db')
cursor = connect.cursor()

class Login():

    def login():
        user = input('Email: ')
        passw = input('Password: ').encode('utf-8')
        active = cursor.execute('SELECT active FROM Users WHERE email = ?', (user, )).fetchone()
        if active == 0:
            return "I'm sorry, your account is not active at this time" 
        elif active == None:
            return "Email and/or Password Incorrect"
        else:
            user_id = cursor.execute('SELECT user_id FROM Users WHERE email = ?', (user, )).fetchone()
            user_id = str(user_id).strip('(),')
            hashpw = cursor.execute('SELECT password FROM Users WHERE user_id = ?', (user_id,)).fetchone()
            hashpw = str(hashpw).strip("(),'").encode('utf-8')
            check = bcrypt.checkpw(password=passw, hashed_password=hashpw)
            if check == True:
                global token
                token = user_id
                print("Welcome!")
            else:
                print("Email and/or Password Incorrect")
        return

class View:
    def print_format_one(results, query):
        query_list = query.split()
        field_names = []
        for word in query_list:
            if word == 'SELECT':
                continue
            elif word == 'FROM':
                break
            else:
                word = word.strip(',')
                field_names.append(word)
        for row in results:
            for field in field_names:
                if field == 'password':
                    print(f'{field:<15}: **********')
                else:
                    print(f'{field:<15}: {row[field_names.index(field)]:<20}')
        return

    def print_format_all(results, query):
        query_list = query.split()
        field_names = []
        for word in query_list:
            if word == 'SELECT':
                continue
            elif word == 'FROM':
                break
            else:
                word = word.strip(',')
                word = (f'{word}'.replace('u.', ''))
                word = (f'{word}'.replace('r.', ''))
                word = (f'{word}'.replace('a.', ''))
                field_names.append(word)
        print(" | ".join(f'{str(field_name):<25}' for field_name in field_names))
        print("-" * 100)
        for row in results:
            formatted_row = " | ".join(f'{str(value):<25}' for value in row)
            print(formatted_row)
        return 

    def view_all():
        query = 'SELECT user_id, first_name, last_name, email FROM Users ORDER BY last_name, first_name'
        results = cursor.execute(query).fetchall()
        View.print_format_all(results, query)
        while True:
            print('''Users
--------
(S)earch for a user
(V)iew a user
(<)Back''')
            new_input = input('What would you like to do?')
            if new_input.lower() == 's':
                View.search()
            elif new_input.lower() == 'v':
                View.view_one()
            elif new_input == '<':
                break
            else:
                print('Unknown Syntax, please try again.')
            return

    def search():
        insert = input('Search Term: ')
        insert = f'%{insert}%'
        query = 'SELECT user_id, first_name, last_name, email FROM Users WHERE first_name LIKE ? or last_name LIKE ? ORDER BY last_name, first_name'
        results = cursor.execute(query, (insert, insert)).fetchall()
        View.print_format_all(results, query)
        return 

    def view_one(user='manager'):
        if user=='manager':
            insert = input('Insert User ID of the user you want to see: ')
            try:
                query = 'SELECT user_id, first_name, last_name, phone, email, password, active, date_created, hire_date, user_type FROM Users WHERE user_id = ? ORDER BY last_name, first_name'
                results = cursor.execute(query, (insert,)).fetchall()
                View.print_format_one(results, query)
            except:
                print('Please enter a valid ID.')
        else:
            insert = token
        try:
            query = 'SELECT user_id, first_name, last_name, phone, email, password FROM Users WHERE user_id = ? ORDER BY last_name, first_name'
            results = cursor.execute(query, (insert,)).fetchall()
            View.print_format_one(results, query)
        except:
            print('Please enter a valid ID.')
        return insert

    def view_competency_all():
        insert = input('Insert the Competency ID of the competency you want to view: ')
        try:
            query = 'SELECT u.user_id, u.first_name, u.last_name, r.score, r.date_taken FROM Users u JOIN Assessment_Results r ON u.user_id = r.user_id JOIN Assessments a ON a.assess_id = r.assess_id WHERE a.comp_id = ? ORDER BY u.last_name, u.first_name, r.date_taken'
            results = cursor.execute(query, (insert, )).fetchall()
            View.print_format_all(results, query)
        except:
            print('Please enter a valid ID.')
        return
    
    def view_competency_one(user_type = 'manager'):
        if user_type == 'manager':
            user = input('Insert the User ID of the user you want to view: ')
            insert = input('Insert the Competency ID of the competency you want to view: ')
        else:
            user = token
            insert = '*'
        try:
            query = 'SELECT u.user_id, u.first_name, u.last_name, r.score, r.date_taken FROM Users u JOIN Assessment_Results r ON u.user_id = r.user_id JOIN Assessments a ON a.assess_id = r.assess_id WHERE a.comp_id = ? AND u.user_id = ? ORDER BY u.last_name, u.first_name, r.date_taken'
            results = cursor.execute(query, (insert, user, )).fetchall()
            View.print_format_all(results, query)
        except:
            print('Please enter a valid ID.')
        return 

    def view_assessments(user_type = 'manager'):
        if user_type == 'manager':
            insert = input('Insert the User ID of the user you want to view: ')
        else:
            insert = token
        try:
            query = 'SELECT a.assess_name, r.score, r.date_taken FROM Assessments a JOIN Assessment_Results r ON a.assess_id = r.assess_id WHERE r.user_id = ? ORDER BY a.assess_name, r.date_taken'
            results = cursor.execute(query, (insert, )).fetchall()
            View.print_format_all(results, query)
        except:
            print('Please enter a valid ID.')
        return

class Add:
    def add_user():
        while True:
            first = input('First Name: ')
            last = input('Last Name: ')
            phone = input('Phone: ')
            email = input('Email: ')
            while True:
                password = input('Password: ')
                confirm = input('Confirm Password: ')
                if password == confirm:
                    password = password.encode('utf-8')
                    salt = bcrypt.gensalt(rounds = 12)
                    hashed = bcrypt.hashpw(password, salt)
                    hashed = hashed.decode('utf-8')
                    break
                else:
                    print('Passwords must match')
            user = input('User Type: ("user" or "manager") ')
            try:
                cursor.execute('INSERT INTO Users (first_name, last_name, phone, email, password, user_type) VALUES (?, ?, ?, ?, ?, ?)', (first, last, phone, email, hashed, user))
                connect.commit()
                print('User successfully added')
                break
            except:
                print('An error occurred, please try again.')
            
        

    def add_competency():
        while True:
            name = input('Name: ')
            try:
                cursor.execute('INSERT INTO Competencies (comp_name) VALUES (?)', (name, ))
                connect.commit()
                print('Competency successfully added')
                break
            except:
                print('An error occurred, please try again.')

    def add_assessment():
        while True:
            name = input('Name: ')
            try:
                cursor.execute('INSERT INTO Assessments (assess_name) VALUES (?)', (name, ))
                connect.commit()
                print('Assessment successfully added')
                break
            except:
                print('An error occurred, please try again.')

    def add_result():
        while True:
            user = input('User ID: ')
            assessment = input('Assessment ID: ')
            score = input('Score: ')
            manager = input('Manager ID: ')
            try:
                cursor.execute('INSERT INTO Assessment_Results (user_id, assess_id, score, manager_id) VALUES (?, ?, ?, ?)', (user, assessment, score, manager, ))
                connect.commit()
                print('Assessment successfully added')
                break
            except:
                print('An error occurred, please try again.')

class Edit:
    def edit_info():
        if user_type == 'manager':
            user = View.view_one()
        else:
            user = View.view_one('user')
        while True:
            field = input('Enter the name of the field you would like to update: ')
            if field == 'password':
                while True:
                    hashpw = cursor.execute('SELECT password FROM Users WHERE user_id = ?', (token,)).fetchone()
                    hashpw = str(hashpw).strip("(),'").encode('utf-8')
                    old = input('Old Password: ').encode('utf-8')
                    check = bcrypt.checkpw(password=old, hashed_password=hashpw)
                    if check == True:
                        password = input('New Password: ')
                        confirm = input('Confirm New Password: ')
                        if password == confirm:
                            password = password.encode('utf-8')
                            salt = bcrypt.gensalt(rounds = 12)
                            info = bcrypt.hashpw(password, salt)
                            info = info.decode('utf-8')
                            break
                        else:
                            print('Passwords must match')
            else:
                info = input('What would you like to change the info to? ')
            try:
                cursor.execute(f'UPDATE Users SET {field} = ? WHERE user_id = ?', (info, user,))
                connect.commit()
                print('Update Successful')
                break
            except:
                print('An error occured, please try again.')

    def edit_competency():
        while True:
            comp_id = input('Enter the ID of the competency you wish to update: ')
            try:
                query = 'SELECT comp_id, comp_name, date_created FROM Competencies WHERE comp_id = ?'
                comp_info = cursor.execute(query, (comp_id,)).fetchall()
                View.print_format_one(comp_info, query)
            except:
                print('Please enter a valid ID.')
                continue
            field = input('Enter the name of the field you would like to update: ')
            info = input('What would you like to change the info to? ')
            try:
                cursor.execute(f'UPDATE Competencies SET {field} = ? WHERE comp_id = ?', (info, comp_id,))
                connect.commit()
                print('Update Successful')
                break
            except:
                print('An error occured, please try again.')
                continue

    def edit_assessment():
        while True:
            assess_id = input('Enter the ID of the assessment you wish to update: ')
            try:
                query = 'SELECT assess_id, comp_id, assess_name, date_created FROM Assessments WHERE assess_id = ?'
                results = cursor.execute(query, (assess_id,)).fetchall()
                View.print_format_one(results, query)
            except:
                print('Please enter a valid ID.')
                continue
            field = input('Enter the name of the field you would like to update: ')
            info = input('What would you like to change the info to? ')
            try:
                cursor.execute(f'UPDATE Assessments SET {field} = ? WHERE assess_id = ?', (info, assess_id,))
                connect.commit()
                print('Update Successful')
                break
            except:
                print('An error occured, please try again.')
                continue
            
    def edit_result():
        while True:
            result_id = input('Enter the ID of the result you wish to update: ')
            try:
                query = 'SELECT result_id, user_id, assess_id, score, date_taken FROM Assessment_Results WHERE result_id = ?'
                results = cursor.execute(query, (result_id,)).fetchall()
                View.print_format_one(results, query)
            except:
                print('Please enter a valid ID.')
                continue
            field = input('Enter the name of the field you would like to update: ')
            info = input('What would you like to change the info to? ')
            try:
                cursor.execute(f'UPDATE Assessment_Results SET {field} = ? WHERE result_id = ?', (info, result_id,))
                connect.commit()
                print('Update Successful')
                break
            except:
                print('An error occured, please try again.')
                continue
            
class Delete:
    def delete_result():
        while True:
            result_id = input('Enter the ID of the result you wish to delete: ')
            try:
                cursor.execute('DELETE FROM Assessment_Results WHERE result_id = ?', (result_id,))
                connect.commit()
                print('Deletion Successful')
                break
            except:
                print('An error occured, please try again.')
                continue

class Import:
    def import_from_csv():
        path = input('Please ensure the file is in the "import" folder and input the name of the file here: ')
        try:
            with open(f'import/{path}', 'r', newline='') as file:
                csvreader = csv.reader(file)
                header = next(csvreader)
                print (header)
                for row in csvreader:
                    query = f'INSERT INTO Assessment_Results ({', '.join(header)}) VALUES {tuple(row)}'
                    print(query)
                    cursor.execute(query)
                    connect.commit()
                    print('Import complete.')
        except:
            print('An error occurred, please try again.')

class Export:
    def export():

        try:
            table = input(f'Which table would you like to export?\nUsers, Competencies, Assessments, Assessment_Results\n')
            query = f'SELECT * FROM {table}'
            cursor.execute(f'{query} LIMIT 0')
            column_names = [description[0] for description in cursor.description]
            rows = cursor.execute(query).fetchall()
            i = 0
            while True:
                try:
                    with open(f'export/export_{table.lower()}{i}.csv', 'x') as file:
                        file.close()
                        break
                except FileExistsError:
                    i += 1
                    continue
            with open(f'export/export_{table.lower()}{i}.csv', 'w', newline='') as file:
                csvwriter = csv.DictWriter(file, fieldnames=column_names)
                csvwriter.writeheader()
                for row in rows:
                    dictionary = {}
                    for i in column_names:
                        dictionary[i] = row[column_names.index(i)]
                    csvwriter.writerow(dictionary)
            print('Export Complete!')
        except:
            print('An error has occured, please try again.')

    def export_to_pdf():
        try:
            table = input('Which table would you like to export to PDF?\nUsers, Competencies, Assessments, Assessment_Results\n')
            query = f'SELECT * FROM {table}'
            cursor.execute(query)
            
            # Get column names and data
            column_names = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            
            # Add title
            pdf.cell(200, 10, txt=f"{table} Report", ln=1, align='C')
            pdf.ln(10)
            
            # Calculate column widths
            col_width = 190 / len(column_names)
            
            # Add headers
            for col in column_names:
                pdf.cell(col_width, 10, txt=col, border=1)
            pdf.ln()
            
            # Add data rows
            for row in rows:
                for item in row:
                    pdf.cell(col_width, 10, txt=str(item), border=1)
                pdf.ln()
            
            # Save the PDF
            i = 0
            while True:
                try:
                    filename = f'export/export_{table.lower()}{i}.pdf'
                    pdf.output(filename)
                    print(f'PDF exported successfully to {filename}')
                    break
                except:
                    i += 1
                    continue
                    
        except:
            print(f'An error occurred, please try again.')

# Menu
token = 'x'
while token == 'x':
    print('Log In')
    print(f'-'*15)
    Login.login()
user_type = cursor.execute('SELECT user_type FROM Users WHERE user_id = ?', (token,)).fetchone()
user_type = user_type[0]
if user_type == 'manager':
    while True:
        print(f'''Welcome to the Competency Tracking Tool!
Menu
------
(V)iew
(A)dd
(E)dit
(D)elete
(I)mport CSV
E(X)port Table
(Q)uit''')
        user_input = input('What would you like to do?\n')
        if user_input.lower() == 'v':
            while True:
                print('''View
-----
(U)sers
User (S)cores
(C)ompetency Scores
(A)ssessments
(<)Return to Menu''')
                new_input = input('What would you like to view?\n')
                if new_input.lower() == 'u':
                    View.view_all()
                elif new_input.lower() == 's':
                    View.view_competency_one()
                elif new_input.lower() == 'c':
                    View.view_competency_all()
                elif new_input.lower() == 'a':
                    View.view_assessments()
                elif new_input == '<':
                    break
                else:
                    print("Unknown Syntax, please try again.")

        elif user_input.lower() == 'a':
            while True:
                print('''Add
-----
(U)ser
(C)ompetency
(A)ssessment
(R)esult
(<)Return to Menu''')
                new_input = input('What would you like to add?\n')
                if new_input.lower() == 'u':
                    Add.add_user()
                elif new_input.lower() == 'c':
                    Add.add_competency()
                elif new_input.lower() == 'a':
                    Add.add_assessment()
                elif new_input.lower() == 'r':
                    Add.add_result()
                elif new_input == '<':
                    break
                else:
                    print("Unknown Syntax, please try again.")
        
        elif user_input.lower() == 'e':
            while True:
                print('''Edit
-----
(U)ser Info
(C)ompetency
(A)ssessment
(R)esult
(<)Return to Menu''')
                new_input = input('What would you like to add?\n')
                if new_input.lower() == 'u':
                    Edit.edit_info()
                elif new_input.lower() == 'c':
                    Edit.edit_competency()
                elif new_input.lower() == 'a':
                    Edit.edit_assessment()
                elif new_input.lower() == 'r':
                    Edit.edit_result()
                elif new_input == '<':
                    break
                else:
                    print("Unknown Syntax, please try again.")

        elif user_input.lower() == 'd':
            Delete.delete_result()

        elif user_input.lower() == 'i':
            Import.import_from_csv()

        elif user_input.lower() == 'x':
            print('''Export
-----
(C)SV Export
(P)DF Export
(<)Return to Menu''')
            export_choice = input('Choose export format: ')
            if export_choice.lower() == 'c':
                Export.export()
            elif export_choice.lower() == 'p':
                Export.export_to_pdf()
            elif export_choice == '<':
                continue
            else:
                print("Unknown Syntax, please try again.")

        elif user_input.lower() == 'q':
            break
        
        else:
            print("Unknown Syntax, please try again.")
else:
    while True:
        print(f'''Welcome to the Competency Tracking Tool!
Menu
------
(V)iew
(E)dit Info
(Q)uit''')
        user_input = input('What would you like to do?\n')
        if user_input.lower() == 'v':
            while True:
                print('''View
-----
(U)ser Info
(C)ompetency Scores
(A)ssessments
(<)Return to Menu''')
                new_input = input('What would you like to view?\n')
                if new_input.lower() == 'u':
                    View.view_one('user')
                elif new_input.lower() == 'c':
                    View.view_competency_one('user')
                elif new_input.lower() == 'a':
                    View.view_assessments('user')
                elif new_input == '<':
                    break
                else:
                    print("Unknown Syntax, please try again.")
        elif user_input.lower() == 'e':
            Edit.edit_info()
        elif user_input.lower() == 'q':
            break
        else:
            print("Unknown Syntax, please try again.")


