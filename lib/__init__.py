"""<https://github.com/gbv/validation-api-ws/>"""

from .service import ValidationService
from .report import ValidationReport
from .validate import Validator, ValidationError, parseJSON, parseXML
from .validate import JSONSchemaValidator, XSDValidator, SchematronValidator

__all__ = [ValidationService, Validator, ValidationError, ValidationReport,
           parseJSON, parseXML,
           JSONSchemaValidator, XSDValidator, SchematronValidator]
