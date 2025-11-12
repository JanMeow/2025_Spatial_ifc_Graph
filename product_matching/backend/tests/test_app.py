import pytest, numpy as np
from requirement_profiles.service import apply_comparison, filter_all_buildups
from requirement_profiles.model import RequirementProfileRequest
from buildups.model import buildups
from cache.service import get_cache
#=========================================================================================
#  Unit Tests
#=========================================================================================
def test_apply_comparison():
    values = np.array([1, 2, 3, 4, 5])
    threshold = 3
    operator = "=="
    expected_result = np.array([False, False, True, False, False])
    result = apply_comparison(values, threshold, operator)
    assert np.array_equal(result, expected_result)

def test_filter_all_buildups():
    rp_request = {
        "product": "Aussenwand 1.1",
        "tThresh":  400,
        "pThresh":   350,
        "uThresh":   0.2,
        "tTol":  20,
        "uTol": 0.1,
        "tThreshOp":  "~=",
        "pThreshOp":  "<=",
        "uThreshOp": "<=",
        "sampling":  "horizontal",
        "preFilter":  None,
    }
    rp_request = RequirementProfileRequest(**rp_request)
    buildups_data = buildups.data
    result = filter_all_buildups(rp_request, buildups_data, get_cache())
    assert result is not None
#=========================================================================================
#  End to End Tests
#=========================================================================================