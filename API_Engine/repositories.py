"""REPOSITORIES
Methods to interact with the database
"""
# # Installed # #
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import requests
import json
import pickle
from fastapi.responses import JSONResponse      

# # Package # #
from .models import *
from .exceptions import *
from .utils import get_time, get_uuid

__all__ = ("ChatBotRepository", "LoanRepository",)


class ChatBotRepository:
    @staticmethod
    def actions():
        return "Hello"

    
class LoanRepository:
    @staticmethod
    def getLoanAmount(customer_id: str):
        data = requests.get('http://20.198.81.29:5000/admin/customer/' + customer_id).json()
        
        customerData = {
            "customer_id" : data["customer"]["id"],
            'customer_income': data["customer"]['annualIncome'],
            'customer_electricity_bill': data["customer"]['electricityBill'],
            'residence_latitude': data["customer"]['residenceAddress']['latitude'],
            'residence_longitude': data["customer"]['residenceAddress']['longitude'],
            'customer_cibil': data['customer']['cibilScore'],
            'customer_status': data['customer']['status'],
            'customer_verified': data['customer']['verified'],
            'gurantor_income': data['instantLoanSurrogates']['guarantor']['annualIncome'] if data['instantLoanSurrogates']['guarantor'] else 0,
            'gurantor_electricity_bill': data['instantLoanSurrogates']['guarantor']['electricityBill'] if data['instantLoanSurrogates']['guarantor'] else 0,
            'gurantor_worthy': data['instantLoanSurrogates']['guarantor']['worthy'] if data['instantLoanSurrogates']['guarantor'] else 0,
            'gurantor_cibil': data['instantLoanSurrogates']['guarantor']['cibilScore'] if data['instantLoanSurrogates']['guarantor'] else 0,
            'gurantor_residence_latitude': data['instantLoanSurrogates']["guarantor"]['residenceAddress']['latitude'] if data['instantLoanSurrogates']['guarantor'] else 0,
            'gurantor_residence_longitude': data['instantLoanSurrogates']["guarantor"]['residenceAddress']['longitude'] if data['instantLoanSurrogates']['guarantor'] else 0,
            'location_category': data['instantLoanSurrogates']['locationCategory'],
            'competition': data['instantLoanSurrogates']['competition'],
            'taxReturns': sum(i['tax'] for i in data['instantLoanSurrogates']['taxReturns']),
            'credit': sum(i['creditAmount'] for i in data['instantLoanSurrogates']['creditAmountOfShopCustomers']) if data['instantLoanSurrogates']['creditAmountOfShopCustomers'] else 0,
            'bank_account': sum(i['currentValue'] if i['currentValue'] else 0 for i in data["allBankAccounts"]),
            'shop_latitude': data["shop"]['shopAddress']['latitude'],
            'shop_longitude': data["shop"]['shopAddress']['longitude'],
            'shop_area': data["shop"]['area'],
            'shop_rating': data["shop"]['rating'],
            'shop_electricity_bill': data["shop"]['electricityAmount'],
            'shop_ownership': data["shop"]['ownership'],
            'shop_warehouse_number': data["shop"]['wareHouse']['numberOfWareHouses'],
            'shop_warehouse_area': sum(data["shop"]['wareHouse']['areaOfWareHouses']) / data["shop"]['wareHouse']['numberOfWareHouses'],
            'items': sum(product['quantity'] * product['pricePerUnit'] for product in data["shop"]['wareHouse']['itemsSet']),
            'loan_amount': data['allLoans'][-1]['demandedAmount'],
        }

        customerDf = pd.DataFrame([customerData.values()], columns=customerData.keys())
        customerDf = customerDf.fillna(0)
        
        labelencoder = LabelEncoder()
        customerDf['customer_verified'] = labelencoder.fit_transform(customerDf['customer_verified'])
        customerDf['shop_ownership'] = labelencoder.fit_transform(customerDf['shop_ownership'])
        customerDf['loan_status'] = 0
        
        actual_loan_amount = customerDf['loan_amount'].values[0]
        
        X = customerDf.drop("loan_amount",axis=1)
        
        linreg = pickle.load(open("./API_Engine/model.sav", 'rb'))
        
        prediction = linreg.predict(X)
        predicted_loan_amount = prediction[0]
        
        return JSONResponse(
            content = {
                "customer_id": customer_id,
                'actual_loan_amount': actual_loan_amount,
                'predicted_loan_amount': predicted_loan_amount
            }
        )