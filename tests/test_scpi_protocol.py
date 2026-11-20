import pytest
from usb_operator.protocols.scpi import validate_scpi_query
@pytest.mark.parametrize("query",["*IDN?","MEAS:VOLT?","SYST:ERR?"])
def test_allowlisted_queries(query): assert validate_scpi_query(query)==query
@pytest.mark.parametrize("query",["VOLT 230","OUTP ON","SYST:REM","*RST?","MEAS:VOLT?;OUTP ON"])
def test_non_allowlisted_or_mutating_scpi_rejected(query):
 with pytest.raises((ValueError,PermissionError)): validate_scpi_query(query)
