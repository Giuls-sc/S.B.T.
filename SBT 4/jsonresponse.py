# This code is a JSON parser that returns a dictionary containing the credit limit and the sublimits for each request.
# The function get_sublimits() takes the credit limit and returns the sublimits.

import json
from calculation import *
from calculation_two import *
from Building_check import *
from sub_limits_json import *


tags_types = {
    'patrimonio_netto' : 'currency',
    'totale_crediti' : 'currency',
    'crediti_esigibili_entro_esercizio' : 'currency',
    'disponibilita_liquide' : 'currency',
    'rimanenze' : 'currency',
    'debiti_esigibili_entro_esercizio' : 'currency',
    'totale_valore_produzione' : 'currency',
    'valore_produzione_altri_ricavi_proventi_totale_altri_ricavi_proventi' : 'float',
    'totale_passivo' : 'currency',
    'utile_perdita' : 'currency',
    'totale_attivo_circolante' : 'currency',
    'EBIT' : 'currency',
    'totale_debiti' : 'currency',
    'interessi_passivi' : 'currency',
    'totale_attivo' : 'currency',
    'capitale_sociale' : 'currency',
    'interest_ratios' : 'float',
    'ROI_ratios' : 'float',
    'valore_produzione_altri_ricavi' : 'float',
    'turnover_impegni_ratios': 'float',
    'AZ_manufacturing' : 'float',
    'AZ_Not_manufacturing' : 'float',
    'financial_laverage' : 'float',
    'assigned_rating' : 'str',
    'Credit_limit' : 'currency',
    'company_name' : 'str',
    'anno' : 'str',
    'acid_test' :  'float',
}

def format_label(key):
    return " ".join(word.capitalize() for word in key.split("_"))

formatted_data = {}

def json_output():
    results = {}
    format_result(data)
    for key, values in formatted_data.items():
        label = format_label(key)
        results[key.lower()] = []
        for context_ref, value in values.items():
            try:
                # Extract the date string from the context_ref
                date_str = context_ref.split("_")[1]  
                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date_str, "%d-%m-%Y") 
                # Format the datetime object as a string 
                formatted_date = date_obj.strftime("%d/%m/%Y")  
            except (IndexError, ValueError):
                formatted_date = "Invalid date"
            formatted_value = {"date": formatted_date, "value": value, "label": label}
            results[key.lower()].append(formatted_value)
    output = results  
    json_output = json.dumps(output)
    return json_output

def get_data_for_key(key):
    formatted_key = key.lower()
    output = json.loads(json_output())
    if formatted_key not in output:
        return None
    return output[formatted_key][0]["value"]

def currency_to_float(value):
    if not isinstance(value, str):
        raise TypeError("The value parameter should be a string")
    return float(value.replace(",", ""))

def currency_format(value):
    value =  f'{float(value):,}'
    # remove the decimal part 
    value = value.split(".")[0]
   
    return value 

def get_sublimits(credit_limit):
    sublimits = {
        "bid_bond": {
            "value": None,
            "label": "Bid Bond"
        },
        "advance_payment_bond": {
            "value": None,
            "label": "Advance Payment Bond"
        },
        "subsidy": {
            "value": None,
            "label": "Subsidy"
        },
        "general_contractor": {
            "value": None, 
            "label": "General Contractor"
        },
        "other": {
            "value": None,
            "label": "Other"
        },
        "housing": {
            "value": None,
            "label": "Housing"
        }
    }
    
    sublimits["bid_bond"]["value"] = currency_format(0.25 * credit_limit)
    sublimits["advance_payment_bond"]["value"] = currency_format(0.5 * credit_limit)
    sublimits["subsidy"]["value"] = currency_format(0.8 * credit_limit)
    sublimits["general_contractor"]["value"] = currency_format(credit_limit)
    sublimits["other"]["value"] = currency_format(0.6 * credit_limit)
    sublimits["housing"]["value"] = currency_format(0.9 * credit_limit)

    return sublimits


def format_result(data):
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_subdict = {}
            for context_ref, context_value in value.items():
                # get type for key 
                format_type = tags_types[key]
                if format_type == "currency":
                    formatted_subdict[context_ref] = currency_format(float(currency_to_float(context_value)))
                elif format_type == "float":
                    formatted_subdict[context_ref] = f"{float(context_value):.2f}"
                elif format_type == "str":
                    formatted_subdict[context_ref] = context_value.replace('"', "")
            formatted_data[key] = formatted_subdict
        else:
            formatted_data[key] = f"{value:.2f}"
    return formatted_data


def return_ateco_description():
    ateco_description = get_attivita()
    json_data = json.dumps(ateco_description)
    return json_data

def get_underwriter(adjusted_risk_score):
        underwriting_approach = {
            0 <= adjusted_risk_score <= 20: 'JUNIOR UNDERWRITER',
            21 <= adjusted_risk_score <= 30: 'UNDERWRITER',
            31 <= adjusted_risk_score <= 40: 'UNDERWRITER',
            41 <= adjusted_risk_score <= 50: 'SENIOR UNDERWRITER',
            51 <= adjusted_risk_score <= 60: 'DAILY BRIEFING',
            61 <= adjusted_risk_score <= 70: 'BOARD MEETING',
            71 <= adjusted_risk_score <= 100: 'DO NOT WRITE !'
        }.get(True, 'Invalid score')
        return underwriting_approach

def get_final_score(adjusted_risk_score):
    return (adjusted_risk_score / 2)