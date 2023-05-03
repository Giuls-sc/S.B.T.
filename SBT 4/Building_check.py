import xml.etree.ElementTree as ET
from datetime import datetime
from calculation import *
from datetime import date



# Function that reads in the locator file and checks for any buildings
def get_number_proprieties():  
    file_path_locator = '/Users/giuls/Desktop/SBT 4/locator.txt'
    tree = ET.parse(file_path_locator)
    root = tree.getroot()
    n_of_buildings = 0
    for elem in root.iter("TotalRealEstateUnitBuildingNumber"):
        n_of_buildings = int(elem.text)
    return n_of_buildings
n_of_buildings = get_number_proprieties()
print(n_of_buildings, "number of buildings in the locator file\n")


# Set the path of the XML file. If n. of buildings above, is greater than zero, then extracts building details below
file_path_gravami = '/Users/giuls/Desktop/SBT 4/plus_gravami.txt'
tree = ET.parse(file_path_gravami)
root = tree.getroot()


# Retrieve cadastral income for each propriety
def get_cadastral_income():
    cadastral_income = []
    for unit_building in root.iter('RealEstateUnitBuilding'):
        for cadastral_annuity in unit_building.iter('CadastralAnnuity'):  
            cadastral_income.append(float(cadastral_annuity.text))
    return cadastral_income
cadas_income = get_cadastral_income()
print(cadas_income, "cadastral_income#Í")


note_list = root.find('.//NoteList')
mortgage = "IP.VOL.X CONC.MUTUO GAR.MUTUO FONDIARIO"
debt_descriptions = []

# Chec if there are any active mortgages on proprieties 
def get_mortgage_info():
    mortgage_start_date = []
    for i, unit_building in enumerate(root.iter('RealEstateUnitBuilding')):
        for note_list in unit_building.iter('NoteList'):
            for note in note_list.iter('Note'):
                for financial_instr in note_list.iter('NoteDescription'):
                    if financial_instr.text == mortgage:
                        debt_descriptions.append(financial_instr.text)
                        for note_date in note_list.iter('NoteDate'):
                            year = note_date.attrib['year']
                            month = note_date.attrib['month']
                            day = note_date.attrib['day']
                            date_str = f"{year}-{month}-{day}"
                            mortgage_start_date.append(date_str )
            break
        if i+1 == n_of_buildings:
            break
    return mortgage_start_date
mortgage_start_date = get_mortgage_info()
print(mortgage_start_date, " mortgages start date")

# Function that extracts the mortgae duration in years
def get_years_mortgage():
    years_mortgage = []
    for i, office_list in enumerate(root.iter('TerritoryOfficeList')):
        for duration in office_list.iter('DurationYears'):
            years_mortgage.append(int(duration.text))
        if i+1 == n_of_buildings:
            break
    return years_mortgage
years_mortgage = get_years_mortgage()
print(years_mortgage, "years mortgage")

# Function that extracts the mortgage value in floating point number - value Euro
def get_mortgage_value():
    mortgage_value = []
    for i, office_list in enumerate(root.iter('TerritoryOfficeList')):
        for amount in office_list.iter('PrincipalAmountEur'):
            mortgage_value.append(float(amount.text))
        if i+1 == n_of_buildings:
            break
    return mortgage_value
mortgage_value = get_mortgage_value()
print(mortgage_value, "mortgage value")

# Function that extracts the percentage of ownership for each building/propriety
def get_percentage_ownership_buildings():
    real_charge = []
    percentage_ownership  = []
    for owner_list in root.iter('OwnerList'):
        for numerator in owner_list.iter('RealChargeNumerator'):
            real_charge.append(int(numerator.text))
            for denominator in owner_list.iter('RealChargeDenominator'):
                real_charge.append(int(denominator.text))
                break  # exit the inner loop after finding the first denominator
            break  # exit the outer loop after finding the first numerator and denominator pair
        if len(real_charge) >= n_of_buildings * 2:  # exit the loop after finding the numerator and denominator for each property 
            break
    else:
        print("Error: Not enough RealChargeNumerator and RealChargeDenominator elements found.")
    for i in range(0, len(real_charge), 2):
        numerator = real_charge[i]
        denominator = real_charge[i+1]
        fraction = numerator / denominator
        percentage_ownership.append(fraction)
    return percentage_ownership
percentage_ownership = get_percentage_ownership_buildings()
print(percentage_ownership, "percentage ownership")
print(mortgage_value, "mortage_value" )


#Function that takes in as parameter the value extracted above ti calculate the security adjusted value for each propriety owned by the co-obligor - TAX Code check
def calculate_restriction_value(cadastral_income, percentage_ownership, mortage_value, years_mortgage, note_dates):
    tax_authority_coefficent= 170
    restriction_value = []
    # Calculate the security adjusted value
    security_adjusted_value = [round((cadastral_annuity * tax_authority_coefficent), 2)  for cadastral_annuity in cadastral_income]
    print(security_adjusted_value , "security_adjusted_value ")
    # Calculate the mortgage residual
    today = date.today()
    mortgage_residual_years = [round(30 - (today - datetime.strptime(date_str, '%Y-%m-%d').date()).days / 365.25, 2) for date_str in note_dates]
    print(mortgage_residual_years , "mortgage_residual in years")
    # Calculate the annual debt
    annual_debt = [round(mortgage_amount / mortgage_duration , 2) for mortgage_amount, mortgage_duration in zip(mortage_value, years_mortgage)]
    print(annual_debt , "annual_debt ")
    # Calculate the restriction value
    residual_debt = [ round( mortgage_residual_years * annual_debt, 2)for mortgage_residual_years, annual_debt in zip(mortgage_residual_years, annual_debt) ]
    restriction_value = [ (sec_val - res_debt  ) * ownership for sec_val, res_debt, ownership in zip(security_adjusted_value, residual_debt, percentage_ownership)]
    return restriction_value
restriction_value = calculate_restriction_value(cadas_income, percentage_ownership, mortgage_value, years_mortgage, mortgage_start_date) 

















