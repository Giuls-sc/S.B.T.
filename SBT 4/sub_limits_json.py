from calculation import *
from calculation_two import *

data = main_data


# Import function
AZ_manufacturing = AZ_score_manufactruing(main_data)
print(AZ_manufacturing,"AZ_manufacturing")


# This function calculates the assigne rating based on the result of the AZ_Score() function
def get_assigned_rating():
    #Initialise the return variable to an empty string
    assigned_rating = ""
    # Check if value exists in data dictionary, if not return error message
    if 'AZ_manufacturing' not in data:
        return "Error: AZ_manufacturing value not found"
    AZ_score_M_1 = round(float(list(AZ_manufacturing.values())[0]),2)
    print(AZ_score_M_1 , "AZ_score_M_1 ")
    # Conditional if elif statement that checks the assigne drating given tha AZ_score value
    if AZ_score_M_1 <= 1.75:                     
        assigned_rating = ('D', 0)
    elif AZ_score_M_1 <= 2.0:
        assigned_rating = ('C', 1)
    elif AZ_score_M_1 <= 2.2:
        assigned_rating = ('CC', 10)
    elif AZ_score_M_1 <= 2.5:
        assigned_rating = ('CCC-', 15)
    elif AZ_score_M_1 <= 3.2:
        assigned_rating = ('CCC', 20)
    elif AZ_score_M_1 <= 3.75:
        assigned_rating = ('CCC+', 20)
    elif AZ_score_M_1 <= 4.15:
        assigned_rating = ('B-', 25)
    elif AZ_score_M_1 <= 4.4:
        assigned_rating = ('B', 30)
    elif AZ_score_M_1 <= 4.75:
        assigned_rating = ('B+', 35)
    elif AZ_score_M_1 <= 4.95:
        assigned_rating = ('BB-', 40)
    elif AZ_score_M_1 <= 5.25:
        assigned_rating = ('BB', 45)
    elif AZ_score_M_1 <= 5.65:
        assigned_rating = ('BB+', 50)
    elif AZ_score_M_1 <= 5.83:
        assigned_rating = ('BBB-', 60)
    elif AZ_score_M_1 <= 6.25:
        assigned_rating = ('BBB', 60)
    elif AZ_score_M_1 <= 6.4:
        assigned_rating = ('BBB+', 65)
    elif AZ_score_M_1 <= 6.65:
        assigned_rating = ('A-', 70)
    elif AZ_score_M_1 <= 6.85:
        assigned_rating = ('A', 70)
    elif AZ_score_M_1 <= 7.2:
        assigned_rating = ('A+', 75)
    elif AZ_score_M_1 <= 7.6:
        assigned_rating = ('AA-', 80)
    elif AZ_score_M_1 <= 8.0:
        assigned_rating = ('AA', 85)
    elif AZ_score_M_1 <= 8.5:
        assigned_rating = ('AA+', 90)
    else:
        assigned_rating = ('AAA', 100)
    return assigned_rating

# This function checks the years of experience of a Company. Takes in bond value and incorporporation year as parameters
def get_experience_factor(bond_value, incorporation_year):  
    print("incorporation year", incorporation_year)
    # checks if data exists. Otherwise return error message
    if bond_value <= 0 or incorporation_year <= 0:
        return "bond_value and incorporation_year must be greater than zero"
    if 'totale_valore_produzione' not in data:    
        return "totale_valore_produzione tag, in get_experience_factor(), not found"
    # Create the return variable and initialise it to 0
    experience_factor = 0  
    #Market practice to calculate works value for Public Tender bonds.
    works_value = 10 * bond_value   
    #Retrieve last two years of total value of production 
    if 'totale_valore_produzione' in data :
        valore_prod_1 = float(list(data['totale_valore_produzione'].values())[0]) 
        valore_prod_2 = float(list(data['totale_valore_produzione'].values())[1])
        print("valore_prod_2",valore_prod_2)
        print("valore_prod_1",valore_prod_1)

    if incorporation_year > 10 and valore_prod_1 > works_value * 2 and valore_prod_2 > works_value * 2 :
            experience_factor = 85      
    elif  5 <incorporation_year <= 10 and valore_prod_1 >= works_value * 2  :
            experience_factor = 90
    elif incorporation_year <= 5 and valore_prod_1 >= works_value:
            experience_factor = 95
    elif incorporation_year > 5 and valore_prod_1 > works_value * 0.5 and valore_prod_2 > works_value * 0.5:
            experience_factor = 100
    elif incorporation_year > 1 and valore_prod_1 > works_value:
            experience_factor = 120
    elif incorporation_year <= 1:
        experience_factor = 200
    else:
        # If no condition is satisfied, return None
        return None
    return experience_factor

# This function calculates the credit limit for a Company based on the experience factor and assigned rating imported as parameters
def get_credit_limit(experience_factor, assigned_rating, data=main_data):   
    #Import acid_test() function 
    acid_test = calculate_acid_test(data)
    acid_test = float(list(acid_test.values())[0])
    # checks total value of production and shareholders equity are in data  {} dictionary and extracts them to use values in the calculations
    if 'totale_valore_produzione' in data and 'patrimonio_netto' in data :
        valore_produzione_1 = float(list(data['totale_valore_produzione'].values())[0])       
        valore_produzione_2 = float(list(data['totale_valore_produzione'].values())[1])
        patrimonio_netto_1 = float(list(data['patrimonio_netto'].values())[0])       
        patrimonio_netto_2 = float(list(data['patrimonio_netto'].values())[1])
    if experience_factor == None:
        return 0
    # Assign experiene factor 85 if shareholders equity of the last two years is 20% greater than total value of production for the last two years
    if experience_factor == 85:                      # 'expert'
        if patrimonio_netto_1 > valore_produzione_1 * 0.20  and patrimonio_netto_2 > valore_produzione_2 * 0.20 and acid_test > 1 and assigned_rating <= 'CCC':
            # If True, assignes credit limit as 20% of the last last year total value of production 
            credit_limit = valore_produzione_1 * 0.20
        else:
            # Otherwise set credit limit as 10% of the last year total value of production 
            credit_limit = valore_produzione_1 * 0.10
    elif experience_factor == 90:                    # 'experienced'
        if valore_produzione_1 * 0.10 < patrimonio_netto_1 and acid_test > 1 and assigned_rating  <= 'CCC':
            credit_limit = valore_produzione_1 * 0.10
        else:
            credit_limit = valore_produzione_1 * 0.05
    elif experience_factor == 95:                   # 'demonstrated':
        if valore_produzione_1 * 0.05 < patrimonio_netto_1 and acid_test > 1 and assigned_rating  <= 'CCC':
            credit_limit = valore_produzione_1 * 0.05
        else:
            credit_limit = valore_produzione_1 * 0.025
    elif experience_factor > 95:                    # 'on the market'
        if valore_produzione_1 * 0.025 < patrimonio_netto_1 and acid_test > 1 and assigned_rating  <= 'CCC':
            credit_limit = valore_produzione_1 * 0.025
        else:
            return 0
    return credit_limit






