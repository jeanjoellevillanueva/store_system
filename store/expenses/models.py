from django.db import models

from mixins.models import ModelMixin

class Expense(ModelMixin):
    """
    The cost you incur when paying bills, taxes, services for running
    the business.
    """

    ADS = 'ads'
    COMS = 'coms'
    ELECTRICITY = 'electricity'
    ENTERTAIN = 'entertain'
    FOOD = 'food'
    INSURANCE = 'insurance'
    INTERNET = 'internet'
    LOAN = 'loan'
    MAINTENANCE = 'maintenance'
    MISC = 'misc'
    PROF_FEE = 'prof_fee'
    RENT = 'rent'
    SALARY = 'salary'
    SOFTWARE = 'software'
    TAX = 'tax'
    TOOL = 'tool'
    TRANSPO = 'transpo'
    WATER = 'water'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (ADS, 'Advertisement'),
        (COMS, 'Communication'),
        (ELECTRICITY, 'Electricity'),
        (ENTERTAIN, 'Entertainment'),
        (FOOD, 'Food'),
        (INSURANCE, 'Insurance'),
        (INTERNET, 'Internet'),
        (LOAN, 'Loan'),
        (MAINTENANCE, 'Maintenance'),
        (MISC, 'Miscellaneous'),
        (PROF_FEE, 'Professional Fee'),
        (RENT, 'Rent'),
        (SALARY, 'Salary'),
        (SOFTWARE, 'Software'),
        (TAX, 'Taxes & Legal Fees'),
        (TOOL, 'Tools & Equipments'),
        (TRANSPO, 'Transportation & Fuel'),
        (WATER, 'Water'),
        (OTHER, 'Other'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
