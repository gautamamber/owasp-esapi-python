#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
OWASP Enterprise Security API (ESAPI)
 
This file is part of the Open Web Application Security Project (OWASP)
Enterprise Security API (ESAPI) project. For details, please see
<a href="http://www.owasp.org/index.php/ESAPI">http://www.owasp.org/index.php/ESAPI</a>.
Copyright (c) 2009 - The OWASP Foundation

The ESAPI is published by OWASP under the BSD license. You should read and 
accept the LICENSE before you use, modify, and/or redistribute this software.

@author Craig Younkins (craig.younkins@owasp.org)
"""

from esapi.core import ESAPI
from esapi.reference.default_encoder import DefaultEncoder

from esapi.validation_rule import ValidationRule

from esapi.reference.validation.base_validation_rule import BaseValidationRule
from esapi.reference.validation.string_validation_rule import StringValidationRule

from esapi.exceptions import ValidationException

CC_MAX_LENGTH = 19

class CreditCardValidationRule(BaseValidationRule):
    """
    This validator is used to perform syntax and semantic validation of a credit
    card number using the Luhn algorithm.
    """
    def __init__(self, type_name, encoder):
        BaseValidationRule.__init__(self, type_name, encoder)
        self.ccrule = self.get_cc_rule(encoder)
        
    def get_cc_rule(self, encoder):
        pattern = ESAPI.security_configuration().get_validation_pattern("CreditCard")
        ccr = StringValidationRule("ccrule", encoder, pattern)
        ccr.set_maximum_length(CC_MAX_LENGTH)
        ccr.set_allow_none(False)
        return ccr
        
    def get_valid(self, context, input_, error_list=None):
        # check null
        if input_ is None or len(input_) == 0:
            if self.allow_none:
                return None
            raise ValidationException( context + ": Input credit card required", 
                    "Input credit card required: context=" + context + ", input=" + input_, context )
                    
        # canonicalize
        canonical = self.ccrule.get_valid(context, input_)
        
        digits_only = ''.join([char for char in canonical if char.isdigit()])
        
        # Lugn alogrithm checking
        sum_ = 0
        times_two = False
        for digit in reversed(digits_only):
            assert 0 <= digit <= 9
            if times_two:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum_ += digit
            times_two = not times_two
        if (sum_ % 10) != 0:
            raise ValidationException( context + ": Invalid credit card input", "Invalid credit card input: context=" + context, context )

        return canonical
        
    def sanitize(self, context, input_):
        return self.whitelist(input_, DefaultEncoder.CHAR_DIGITS)