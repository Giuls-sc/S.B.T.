import re
import copy 


file_path = '/Users/giuls/Desktop/SBT 4/download-file-api.txt'

tags = {
    # Shareholder's equity C13
    'patrimonio_netto': 'TotalePatrimonioNetto',             
    'totale_crediti': 'TotaleCrediti',
    'crediti_esigibili_entro_esercizio': 'CreditiEsigibiliEntroEsercizioSuccessivo',
    'disponibilita_liquide': 'TotaleDisponibilitaLiquide',
    # Inventories C31
    'rimanenze': 'TotaleRimanenze',
    'debiti_esigibili_entro_esercizio': 'DebitiEsigibiliEntroEsercizioSuccessivo',
    'totale_valore_produzione': 'TotaleValoreProduzione',
    'valore_produzione_altri_ricavi': 'ValoreProduzioneAltriRicaviProventiTotaleAltriRicaviProventi',
    #'totale_passivo': 'TotalePassivo',                       
    'utile_perdita': 'UtilePerditaEsercizio',
    'totale_attivo_circolante': 'TotaleAttivoCircolante',    
    # Liquid Assets C22
    'EBIT': "DifferenzaValoreCostiProduzione",   
    # Total liabilities C23         
    'totale_debiti': 'TotaleDebiti',                         
    'interessi_passivi': 'ProventiOneriFinanziariInteressiAltriOneriFinanziariAltri',
    # Total Assets C24
    'totale_attivo': 'TotaleAttivo',      
     # Share capital C14                   
    'capitale_sociale': 'PatrimonioNettoCapitale',          
    'company_name': 'DatiAnagraficiDenominazione',
    #'anno': 'DatiAnagraficiSede'
}


# Helper function to extract financvial data from the XML file . takes in two argments
def get_financial_data(tags, file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    # Create data {} dictionary to store the data retrieved
    data = {}
    for tag_name, tag in tags.items():
        # Regular expression to check for matching tag and value
        tag_matches = re.findall(fr'<(?:itcc-ci:|itccci:){tag}[^>]*contextRef="([id])_([^"]+)"[^>]*>([\d,.]+)</(?:itcc-ci:|itccci:){tag}>',content)
        if tag_name == 'company_name':
            tag_matches = re.findall(fr'<(?:itcc-ci:|itccci:){tag}[^>]*contextRef="([id])_([^"]+)">([^<]+)</(?:itcc-ci:|itccci:){tag}>',content)
        if tag_matches:
            # If a match is found store the corresponding value in tag_value dictionary 
            tag_values = {}
            for match in tag_matches:
                context_type, context_value, tag_value = match
                context_type = 'i' if context_type == 'd' else context_type  # cannot read context_ref 'd'. Replace 'd' with 'i' . For now.
                # check tag_value type and format it 
                if isinstance(tag_value, float):
                    tag_value = float(tag_value.replace(',', '.'))
                else:
                    tag_value = tag_value
                tag_values[f"{context_type}_{context_value}"] = tag_value
            data[tag_name] = tag_values
        else:
            print(f"Error: {tag} tag not found")
    return copy.deepcopy(data)
data = get_financial_data(tags, file_path) 

# Function to calculate the AZ score . Takes in various financial data . Perform the formula calculation. Saves the two years reesult in dictionary AZ_manufacturing{} and return the value
def AZ_score_manufactruing(data):
    AZ_manufacturing = {}
    if 'totale_attivo'in data and data['totale_attivo'] and 'totale_debiti'in data and data['totale_debiti'] != 0:
        for context_ref in data['totale_attivo_circolante']:
            if 'rimanenze' in data and context_ref in data['rimanenze'] \
                    and 'crediti_esigibili_entro_esercizio' in data and context_ref in data['crediti_esigibili_entro_esercizio'] \
                    and 'debiti_esigibili_entro_esercizio' in data and context_ref in data['debiti_esigibili_entro_esercizio'] \
                    and 'totale_attivo_circolante' in data and context_ref in data['totale_attivo_circolante'] \
                    and 'patrimonio_netto' in data and context_ref in data['patrimonio_netto'] \
                    and 'capitale_sociale' in data and context_ref in data['capitale_sociale'] \
                    and 'EBIT' in data and context_ref in data['EBIT'] :
                AZ_M_fomrula =  1.5 * (float(data['rimanenze'][context_ref]) + float(data['crediti_esigibili_entro_esercizio'][context_ref]) - float(data['debiti_esigibili_entro_esercizio'][context_ref]) + float(data['totale_attivo_circolante'][context_ref]) ) / float(data['totale_attivo'][context_ref]) + 1.44* (float(data['patrimonio_netto'][context_ref]) -  float(data['capitale_sociale'][context_ref]) ) / float(data['totale_attivo'][context_ref]) + 3.64 * float(data['EBIT'][context_ref]) / float(data['totale_attivo'][context_ref]) + 0.7 * float(data['patrimonio_netto'][context_ref]) / float(data['totale_debiti'][context_ref]) + 0.64 * second_value
                AZ_manufacturing[context_ref] = AZ_M_fomrula
        data['AZ_manufacturing'] = AZ_manufacturing 
        return AZ_manufacturing
    else:
        print("Error: totale_attivo or  totale_debiti tag, in AZ_score_manufactruing, not found or has no value")
        
# Function that calculate     
def AZ_score_Not_manufactruing(data):
    AZ_Not_manufacturing = {}
    if 'totale_attivo'in data and data['totale_attivo'] and 'totale_debiti'in data and data['totale_debiti'] != 0:
        for context_ref in data['totale_attivo_circolante']:
            if 'rimanenze' in data and context_ref in data['rimanenze'] \
                    and 'crediti_esigibili_entro_esercizio' in data and context_ref in data['crediti_esigibili_entro_esercizio'] \
                    and 'debiti_esigibili_entro_esercizio' in data and context_ref in data['debiti_esigibili_entro_esercizio'] \
                    and 'totale_attivo_circolante' in data and context_ref in data['totale_attivo_circolante'] \
                    and 'patrimonio_netto' in data and context_ref in data['patrimonio_netto'] \
                    and 'capitale_sociale' in data and context_ref in data['capitale_sociale'] \
                    and 'EBIT' in data and context_ref in data['EBIT'] :
                AZ_NOT_M_fomrula =  (6.56 *(float(data['rimanenze'][context_ref]) + float(data['crediti_esigibili_entro_esercizio'][context_ref]) - 
                                       float(data['debiti_esigibili_entro_esercizio'][context_ref]) + float(data['totale_attivo_circolante'][context_ref]))/
                                       float(data['totale_attivo'][context_ref]) )+ 3.26* ((float(data['patrimonio_netto'][context_ref]) - 
                                       float(data['capitale_sociale'][context_ref]) ) / float(data['totale_attivo'][context_ref])) + 6.72 * (float(data['EBIT'][context_ref]) / float(data['totale_attivo'][context_ref])) + 1.05 * (float(data['patrimonio_netto'][context_ref]) / float(data['totale_debiti'][context_ref])) 
                AZ_Not_manufacturing[context_ref] = AZ_NOT_M_fomrula
        data['AZ_Not_manufacturing'] = AZ_Not_manufacturing 
    else:
        print("Error: totale_attivo or  totale_debiti tag, in AZ_score_manufactruing, not found or has no value")


# Calculate Acid Test
def calculate_acid_test(data):
    if 'debiti_esigibili_entro_esercizio' in data and data['debiti_esigibili_entro_esercizio'] != 0:
        # Create dictionary sto store vales
        acid_test = {}
        # Check value exists 
        for context_ref in data['debiti_esigibili_entro_esercizio']:
            if 'crediti_esigibili_entro_esercizio' in data and context_ref in data['crediti_esigibili_entro_esercizio'] \
                    and 'disponibilita_liquide' in data and context_ref in data['disponibilita_liquide'] :
                a_t = (float(data['crediti_esigibili_entro_esercizio'][context_ref].replace(',','')) + 
                             float(data['disponibilita_liquide'][context_ref]) ) / float(data['debiti_esigibili_entro_esercizio'][context_ref])
                acid_test [context_ref] = a_t 
        data['acid_test'] = acid_test
        return acid_test 
    else:
        print("Error: DebitiEsigibiliEntroEsercizioSuccessivo tag, calculate_acid_test, not found or has no value")

# Calculate current Ratio        
def calculate_current_ratios(data):
    if 'debiti_esigibili_entro_esercizio' in data and data['debiti_esigibili_entro_esercizio'] != 0:
        current_ratios = {}
        for context_ref in data['debiti_esigibili_entro_esercizio']:
            if 'crediti_esigibili_entro_esercizio' in data and context_ref in data['crediti_esigibili_entro_esercizio'] \
                    and 'disponibilita_liquide' in data and context_ref in data['disponibilita_liquide'] \
                    and 'rimanenze' in data and context_ref in data['rimanenze']:
                curre_ratio_formula = (float(data['crediti_esigibili_entro_esercizio'][context_ref]) + 
                                 float(data['disponibilita_liquide'][context_ref]) + 
                                 float(data['rimanenze'][context_ref])) / float(data['debiti_esigibili_entro_esercizio'][context_ref])       
                current_ratios[context_ref] = curre_ratio_formula
        data['current_ratios'] = current_ratios
        return current_ratios
    else:
        print("Error: DebitiEsigibiliEntroEsercizioSuccessivo tag, calculate_current_ratios, not found or has no value")

# Calculate ROI
def calculate_ROI(data):
    if 'totale_attivo_circolante' in data and data['totale_attivo_circolante'] != 0:
        ROI_ratios = {}
        for context_ref in data['totale_attivo_circolante']:
            if 'EBIT' in data and context_ref in data['EBIT']\
                    and 'totale_attivo_circolante' in data and context_ref in data['totale_attivo_circolante'] :
                r_o_i = (float(data['EBIT'][context_ref]) / 
                        float(data['totale_attivo_circolante'][context_ref]))
                ROI_ratios[context_ref] = r_o_i 
        data['ROI_ratios'] = ROI_ratios 
        return ROI_ratios
    else:
        print("Error: totale_attivo_circolante tag, in calculate_ROI, not found or has no value")

# Calculate Giorni Dilazione clienti (C25/C15) * 365
def giorni_dilazione_clienti_ratio(data):
    if 'totale_crediti' in data and data['totale_crediti'] != 0:
        giorni_dilazione_clienti = {}
        for context_ref in data['totale_crediti']:
            #if 'totale_crediti' in data and context_ref in data['totale_crediti']:
            if 'totale_crediti' in data and context_ref in data['totale_crediti']: #\
                    #and 'disponibilita_liquide' in data and context_ref in data['disponibilita_liquide'] \
                    #and 'rimanenze' in data and context_ref in data['rimanenze']:    
                giorni_dc  = (data['totale_crediti'][context_ref] )# data['totale_valore_produzione'][context_ref]) * 365
                giorni_dilazione_clienti[context_ref] = giorni_dc
                data['giorni_dilazione_clienti'] = giorni_dilazione_clienti
                return giorni_dilazione_clienti
            else:
                print("Error: TotaleCrediti tag, in giorni_dilazione_clienti_ratio, not found or has no value")
    

# Calculate Giorni Dilazione Fornitori 
def giorni_dilazione_fornitori_ratio(data):   #(C21+C15) * 365 = (DebitiFornitori / TotaleValoreProduzione) * 365
    if 'totale_valore_produzione' in data and data['totale_valore_produzione'] != 0:
        giorni_dilazione_fornitori= {}
        for context_ref in data['totale_valore_produzione']:
            if 'totale_valore_produzione' in data and context_ref in data['totale_valore_produzione']: #\
                    #and 'debiti_verso_fornitori' in data and context_ref in data['debiti_verso_fornitori'] :
                giorni_df  = (data['totale_valore_produzione'][context_ref]) #/ data['totale_valore_produzione'][context_ref]) * 365 # data['totale_valore_produzione'][context_ref]) * 365
                giorni_dilazione_fornitori[context_ref] = giorni_df
                data['giorni_dilazione_fornitori'] = giorni_dilazione_fornitori
                return giorni_dilazione_fornitori
            else:
                print("Error: totale_valore_produzione tag, in giorni_dilazione_fornitori_ratio, not found or has no value")
    

# Interest  = C29 / C19  = Interest and financial expenses / totale debiti
def calculate_interest_ratios(data):
    if 'totale_debiti' in data and data['totale_debiti'] != 0:
        interest_ratios = {}
        for context_ref in data['totale_debiti']:
            if 'interessi_passivi' in data and context_ref in data['interessi_passivi'] \
                    and 'totale_debiti' in data and context_ref in data['totale_debiti'] :
                interest_formula = (float(data['interessi_passivi'][context_ref]) / 
                        float(data['totale_debiti'][context_ref]))
                interest_ratios[context_ref] = interest_formula 
        data['interest_ratios'] = interest_ratios 
        return interest_ratios
    else:
        print("Error: totale_debiti tag, in calculate_interest_ratios, not found or has no value")

# Result Interes = C81 - C82 = ROI - Interest 
def differenziale_interessi_ratios(data):
    if 'totale_attivo_circolante' in data and data['totale_attivo_circolante'] != 0:
        differenziale_interessi_ratios = {}
        for context_ref in data['totale_attivo_circolante']:
            if 'EBIT' in data and context_ref in data['EBIT'] \
                    and 'totale_attivo_circolante' in data and context_ref in data['totale_attivo_circolante'] \
                    and 'interessi_passivi' in data and context_ref in data['interessi_passivi']    :
                differenziale_interessi_formula =((data['EBIT'][context_ref] / 
                        data['totale_attivo_circolante'][context_ref]) - data['interessi_passivi'][context_ref] )
                differenziale_interessi_ratios[context_ref] = differenziale_interessi_formula 
        data['differenziale_interessi_ratios'] = differenziale_interessi_ratios 
        return differenziale_interessi_ratios
    else:
        print("Error: totale_attivo_circolante tag, in differenziale_interessi_ratios, not found or has no value")

# ROE = C27/C13 = UtilePerditaEsercizio / TotalePatrimonioNetto
def calculate_ROE(data):
    if 'patrimonio_netto' in data and data['patrimonio_netto'] != 0:
        ROE_ratio = {}
        for context_ref in data['patrimonio_netto']:
            if 'utile_perdita' in data and context_ref in data['utile_perdita']\
                    and 'patrimonio_netto' in data and context_ref in data['patrimonio_netto'] :
                r_o_e=  (float(data['utile_perdita'][context_ref] )/ float(data['patrimonio_netto'][context_ref]))
                ROE_ratio[context_ref] = r_o_e 
        data['ROE_ratio'] = ROE_ratio 
        return ROE_ratio
    else:
        print("Error: TotalePatrimonioNetto tag, in ROE, not found or has no value")

# Turnover magazzino = C15 / C31 = totale valore produzione / inventories 
def calculate_turnover_magazzino(data):
    if 'rimanenze' in data and data['rimanenze'] != 0:
        turnover_magazzino_ratios = {}
        for context_ref in data['totale_valore_produzione']:
            if 'totale_valore_produzione' in data and context_ref in data['totale_valore_produzione']\
                    and 'rimanenze' in data and context_ref in data['rimanenze'] :
                turnover_magazzino_formula =  (data['totale_valore_produzione'][context_ref] / 
                        data['rimanenze'][context_ref])
                turnover_magazzino_ratios[context_ref] = turnover_magazzino_formula 
        data['turnover_magazzino_ratios'] = turnover_magazzino_ratios 
        return turnover_magazzino_ratios
    else:
        print("Error: Rimanenze tag, in Turnover magazzino, not found or has no value")

# Giacenza del magazzino = (C31 / C15) * 365 = (Inventories / Totale valore produzione ) * 365
def calculate_giacenza_magazzino(data):
    if 'totale_valore_produzione' in data and data['totale_valore_produzione'] != 0:
        giacenza_magazzino_ratios = {}
        for context_ref in data['rimanenze']:
            if 'rimanenze' in data and context_ref in data['rimanenze']\
                    and 'rimanenze' in data and context_ref in data['rimanenze'] :
                giacenza_magazzino_formula =  (float(data['rimanenze'][context_ref] )/ float(data['totale_valore_produzione'][context_ref]))* 365
                giacenza_magazzino_ratios[context_ref] = giacenza_magazzino_formula 
        data['giacenza_magazzino_ratios'] = giacenza_magazzino_ratios 
        return giacenza_magazzino_ratios
    else:
        print("Error: totale_valore_produzione tag, in calculate_giacenza_magazzino, not found or has no value")

# Turnover degli impegni = (C15 / C24) Totale valore produzione / Totale attivo 
def calculate_turnover_impegni(data):
    if 'totale_attivo_circolante' in data and data['totale_attivo_circolante'] != 0:
        turnover_impegni_ratios = {}
        for context_ref in data['totale_attivo_circolante']:
            if 'totale_valore_produzione' in data and context_ref in data['totale_valore_produzione']\
                    and 'totale_attivo_circolante' in data and context_ref in data['totale_attivo_circolante'] :
                turnover_impegni_formula =  (float(data['totale_valore_produzione'][context_ref]) / 
                        float(data['totale_attivo_circolante'][context_ref]))
                turnover_impegni_ratios[context_ref] = turnover_impegni_formula 
                data['turnover_impegni_ratios'] = turnover_impegni_ratios 
            else:
                print("Error: totale_attivo_circolante tag, in calculate_turnover_impegni, not found or has no value")
    return turnover_impegni_ratios

#Calculate Differenziale Dilazioni
def differenziale_dilazioni_ratio(data, giorni_dilazione_fornitori, giorni_dilazione_clienti):
    if 'giorni_dilazione_fornitori' not in data or 'giorni_dilazione_clienti' not in data:
        return "Error: giorni_dilazione_fornitori or giorni_dilazione_clienti tag not found"
    differenziale_dil = {}
    for context_ref in giorni_dilazione_clienti:
        iterator = iter(giorni_dilazione_fornitori.items())
        next(iterator)
        second_pair_fornitori = next(iterator)
        iterator = iter(giorni_dilazione_clienti.items())
        next(iterator)
        second_pair_clienti = next(iterator)
        differenziale_dilazioni_formula = second_pair_fornitori[1] - second_pair_clienti[1]
        differenziale_dil[context_ref] = differenziale_dilazioni_formula
        data['differenziale_dilazioni'] = differenziale_dil 
    return differenziale_dil[context_ref]                                           

# Calculate Financial Laverage C24/C13  Total Assets / Shareholder's Equity
def financial_laverage(data):
    if 'patrimonio_netto' in data and data['patrimonio_netto'] != 0:
        financial_laverage = {}
        for context_ref in data['patrimonio_netto']:
            if 'totale_attivo' in data and context_ref in data['totale_attivo'] \
                    and 'patrimonio_netto' in data and context_ref in data['patrimonio_netto'] :
                financial_laverage_formula = float(data['totale_attivo'][context_ref]) / float(data['patrimonio_netto'][context_ref])
                financial_laverage [context_ref] = financial_laverage_formula 
                data['financial_laverage'] = financial_laverage 
                return financial_laverage  
            else:
                print("Error: patrimonio_netto tag, in financial_laverage, not found or has no value") 


interest_result = calculate_interest_ratios(data)
calculate_interest_ratios(data)
calculate_ROI(data)
turnover_impegni = calculate_turnover_impegni(data)
second_value = list(turnover_impegni.values())[1]
AZ_score_manufactruing(data)
AZ_score_Not_manufactruing(data)
financial_laverage(data)
AZ_score_M = AZ_score_manufactruing(data)
fin_lev = financial_laverage(data)
calculate_giacenza_magazzino(data)
calculate_ROE(data)
calculate_acid_test(data)
calculate_current_ratios(data)




main_data = data

def return_result():
   
    result = "\n <br>".join([f"{key} ({context_ref}): {value}"
                        for key, values in data.items()
                        for context_ref, value in values.items()])
    print(result)                      
    return result



