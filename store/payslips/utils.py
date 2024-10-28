from .models import Payslip


def parse_deduction(orig_dict):
    """
    Parse the deduction type and amount in the dict.
    """

    deductions = []
    for key, value in orig_dict.items():
        if key.startswith('deduction_type_'):
            _, _, number = key.split('_')
            deduction_type_key = f'deduction_type_{number}'
            amount_key = f'deduction_amount_{number}'
            deductions.append({
                'deduction_type': orig_dict[deduction_type_key],
                'amount': orig_dict[amount_key],
            })
    return deductions


def format_deductions(deductions):
    """
    Converts deduction choice into human-readable
    """
    deductions_dict = dict(Payslip.DEDUCTION_CHOICES)
    for deduction in deductions:
        deduction['deduction_type'] = deductions_dict.get(deduction['deduction_type'])
    return deductions
