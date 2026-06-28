"""<https://github.com/gbv/validation-api-ws/>"""

from .service import ValidationService
from .dvrf import ValidationError, ValidationReport
from .validate import Validator, parseJSON, parseXML
from .validate import JSONSchemaValidator, XSDValidator, SchematronValidator

__all__ = [ValidationService, Validator, ValidationError, ValidationReport,
           parseJSON, parseXML,
           JSONSchemaValidator, XSDValidator, SchematronValidator]
