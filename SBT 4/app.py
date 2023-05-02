from crypt import methods
from flask import Flask, render_template, request, jsonify,redirect, url_for
from jsonresponse import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db_config = {
    'user': 'root',
    'password' : '1234asd!',
    'host': 'localhost',
    'port': 3306,
    'database': 'sbt'
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s' % db_config
db_string = 'mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s' % db_config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = db.create_engine(db_string, engine_opts={'pool_recycle': 3600})

# This function communicate from backnd to databse to calculates the adjusted risk of a quotation based on the bond type, bond value, and bond duration storeed in the db. Function
# render_template() pushes the data to the result.html page in the front-end
def get_adjusted_result(bond_type,bond_value,months):
    #If not bond has been specified, return zero
    if bond_type is None:
        return 0
    else:
        # Get bond risk score and impact factor from Adjusted_risk_table from MYSQL
        bond_type_query = "SELECT bond_risk_score, impact_factor FROM Adjusted_risk_table WHERE bond_type = '{}'".format(bond_type)
        result = engine.execute(bond_type_query).fetchone()
        # If bond type not found, return error message
        if result is None:
            return jsonify({'error': 'Not Valid Bond Type'})
        # Get the Ateco code and impact factor from ateco_code_table from MYSQL
        bond_risk_score, impact_factor = result
        ateco_code_query = "SELECT code, impact_factor FROM ateco_code_table WHERE code = '{}'".format(get_ateco_code())
        print('ateco_code_query: ', ateco_code_query)
        result_ateco = engine.execute(ateco_code_query).fetchone()
        print('result_ateco: ', result_ateco)
        # If the Ateco code is not found, return error message
        if result_ateco is None:
            return jsonify({'error': 'Not Valid Ateco Code'})
        ateco_code, ateco_impact_factor = result_ateco
        # Get the adjusting factor from capacity_track_record_table based on years of experience of the Client from MYSQL 
        incorporation_query = "SELECT factor FROM capacity_track_record_table WHERE years_experience <= {} ORDER BY years_experience DESC LIMIT 1 ".format(get_incorporation())
        result_track_record = engine.execute(incorporation_query).fetchone()
        # If incorporation is not found, return error message. Past performance not found.
        if result_track_record is None:
            return jsonify({'error': 'Not Valid Incorporation'})
        factor = result_track_record[0]
        # Get bond value and corrective factor from bond_value_table based on the selected bond value, from MYSQL.
        bond_value_query = "SELECT bond_value, factor FROM bond_value_table WHERE bond_value <= '{}' ORDER BY bond_value DESC LIMIT 1".format(bond_value)
        result = engine.execute(bond_value_query).fetchone()
        print('bond_value_query: ', bond_value_query)
        print('result: ', result)
        # If bond value is not found, return error message
        if result is None:
            return jsonify({'error': 'Not Valid Bond Value'})
        bond_value, bond_value_factor = result
        # Get loading factor from bond_duration_table based on bond duration, from MYSQL
        bond_duration_query = "SELECT months, loading FROM bond_duration_table WHERE months <= {} ORDER BY months DESC LIMIT 1".format(months)
        result = engine.execute(bond_duration_query).fetchone()
        print('bond_duration_query: ', bond_duration_query)
        print('result: ', result)
        # If bond duration is not found then return error message
        if result is None:
            return jsonify({'error': 'Not Valid Duration'})
        months, loading = result
        # Calculate the adjusted result based on the corrective factors retrieved from MYSQL
        adjusted_result = bond_risk_score * impact_factor
        adjusted_result = adjusted_result * ateco_impact_factor
        adjusted_result = adjusted_result * factor
        adjusted_result = adjusted_result * bond_value_factor
        adjusted_result = adjusted_result * loading
        return adjusted_result


# This function communicate between backend and frontend. Stores the txt input variable from the fron-end saves it in dictionary data
@app.route('/result', methods=['GET','POST'])
def result():
    if request.method == "GET":
        return " not valid"
    if request.method == 'POST':
    # Set the input variables to None. Retrieve input variables from index.html if not empty
        vat_no, bond_value, bond_duration, type_of_bond, tax_code = None, None, None, None, None   
        # If insert-text field in index.html is not empty retrieve value and assign it to variable vat_no
        if request.form.get('insert-text') is not None and request.form.get('insert-text') != '':
            vat_no = request.form.get('insert-text') 
        # If bond value field in index.html is not empty retrieve value and assign it to variable bond_value
        if request.form.get('bond_value') is not None and request.form.get('bond_value') != '':
            bond_value = request.form.get('bond_value')
        # If bnd duration field in index.html is not empty retrieve value and assign it to variable bond_duration
        if request.form.get('bond_duration') is not None and request.form.get('bond_duration') != '':
            bond_duration = request.form.get('bond_duration')
        # If type of bond field in index.html is not empty retrieve value and assign it to variable type_of_bond
        if request.form.get('type-of-bond') is not None and request.form.get('type-of-bond') != '':
            type_of_bond = request.form.get('type-of-bond')
        # If tax code field in index.html is not empty retrieve value and assign it to variable tax_code
        if request.form.get('tax_code') is not None and request.form.get('tax_code') != '':
            tax_code = request.form.get('tax_code')
        # Initialize dictionaries to store data and error messages
        data = {}
        error = {}
        # Error message if vat_no 
        if vat_no is None and tax_code is None:
            error['vat_no'] = 'Please Enter Vat No'
            return redirect(url_for('index', error=error))
        # If VAT n. is not None, retrieve data from balance sheet, otherwise display error message and re-direct to index.html    
        if vat_no is not None :
            data['json_data'] = json_output()
            data['output'] = return_result()
            data['assigned_rating'] = get_assigned_rating()[0]
            data['company_name'] = get_data_for_key('company_name').replace('"', '')
            # Check for inputs:  bond value, bond duration and bond type. Dispaly error message if any values is None and re-direct to index.html
            if bond_value is not None or bond_duration is not None or type_of_bond is not None:
                print('bond_value: ', bond_value)
                print('bond_duration: ', bond_duration)
                print('type_of_bond: ', type_of_bond)
                if bond_value is None or bond_value == '':
                    error['bond_value'] = 'Please Select Bond Value'
                    return redirect(url_for('index', error=error))
                if bond_duration is None or bond_value == '':
                    error['bond_duration'] = 'Please Select Bond Duration'
                    return redirect(url_for('index', error=error))
                if type_of_bond is None or type_of_bond == '':
                    error['type_of_bond'] = 'Please Select Type Of Bond'
                    return redirect(url_for('index', error=error))
                # Otherwise call the functions to handle the final calculations to calculate, credit limit, sublimits, assigned rating, and adjusted final score, and save results in data dictionary
                experience_factor = get_experience_factor(int(request.form.get('bond_value')), get_incorporation())
                print('experience factor', experience_factor)
                assigned_rating = get_assigned_rating()[0]
                credit_limit = get_credit_limit(experience_factor, assigned_rating)
                data['sublimits'] = get_sublimits(credit_limit)
                #Formats the maximum credit limit in result.html page 
                data['credit_limit'] = f"{credit_limit:.2f}"
                data['credit_limit'] = f"{float(data['credit_limit']):,.2f}"
                data['ateco_description'] = return_ateco_description().replace('"','')
                adjusted_score = get_adjusted_result(request.form.get('type-of-bond'),request.form.get('bond_value'),request.form.get('bond_duration'))
                if not isinstance(adjusted_score, float):
                    error['adjusted_score'] = adjusted_score.get_json()
                    return redirect(url_for('index', error=error))
                data['underwriter'] = get_underwriter(adjusted_score)
                data['final_score'] = f"{ get_final_score(adjusted_score):.2f}"
        # If tax code is entered, retrieve building data, mortgages, and calculate value of the co-obbligation offered. Save in data dictionary 
        if tax_code is not None:
            mortgage_data = []
            propeties_count = get_number_proprieties()
            if propeties_count is None:
                error['tax_code'] = 'Please Enter Valid Tax Code'
                redirect(url_for('index', error=error))
            else:
                cadastral_income = get_cadastral_income()
                mortgage_start = get_mortgage_info()
                mortgage_years = get_years_mortgage()
                mortgage_amount = get_mortgage_value()
                ownership_percent = get_percentage_ownership_buildings()
                debt_type = debt_descriptions
                final_result = calculate_restriction_value(cadastral_income,ownership_percent,mortgage_amount,mortgage_years,mortgage_start)
                for i in range(propeties_count):
                    mortgage_data.append({
                        'cadastral_income': '{:,.2f}'.format(cadastral_income[i]),
                        'ownership_percent': ownership_percent[i],
                        'mortgage_amount': '{:,.2f}'.format(mortgage_amount[i]),
                        'mortgage_duration_years': mortgage_years[i],
                        'mortgage_start_date': mortgage_start[i],
                        'debt_type': debt_type[i],
                        'Security Adjusted Net Value': "{:,.2f}".format(final_result[i])
                    })
                data['mortgage_data'] = mortgage_data
        # Check if any field is empty, in which case return error message
        if request.form.get('insert-text') is None or request.form.get('bond_value') is None or request.form.get('bond_duration') is None or request.form.get('type-of-bond') is None or request.form.get('tax_code') is None:
            error['empty_fields'] = 'Please Fill-in all fields'
            return redirect(url_for('index', error=error))
        # Return the result template with the data
        return render_template('result.html', data=data)
    else:
        # If tax code is not entered, return error message
        vat_no = 'Not Specified'
        output = 'Page has been directly acccessed, so No results here!'
        return render_template('result.html')

#This function renders the main form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the VAT number entered in the input form
        vat_no = request.form.get('insert-text')
        # Call the differenziale_dilazioni_ratio function to calculate the output
        output = return_result()
        # Render the results template and pass in the output value
        return render_template('result.html', vat_no=vat_no, output=output)
    else:
        # Render the index template if the request is a GET request
        if request.args.get('error') is not None:
            error = request.args.get('error')
            error = json.loads(error.replace("'", "\""))
            print(error)
            return render_template('index.html', error=error)
        return render_template('index.html', error=None)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5001, debug=True)
