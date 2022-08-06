# -*- coding: utf-8 -*-
"""Unit tests for all time series regressors."""

__author__ = ["mloning", "TonyBagnall", "fkiraly"]


import numpy as np
import pytest

from sktime.datatypes import check_is_scitype
from sktime.tests.test_all_estimators import BaseFixtureGenerator, QuickTester
from sktime.utils._testing.scenarios_classification import (
    ClassifierFitPredictMultivariate,
)


class RegressorFixtureGenerator(BaseFixtureGenerator):
    """Fixture generator for classifier tests.

    Fixtures parameterized
    ----------------------
    estimator_class: estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
    estimator_instance: instance of estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
        instances are generated by create_test_instance class method
    scenario: instance of TestScenario
        ranges over all scenarios returned by retrieve_scenarios
    """

    # note: this should be separate from _TestAllRegressors
    #   additional fixtures, parameters, etc should be added here
    #   _TestAllRegressors should contain the tests only

    estimator_type_filter = "regressor"


class _TestAllRegressors(RegressorFixtureGenerator, QuickTester):
    """Module level tests for all sktime regressors."""

    def test_multivariate_input_exception(self, estimator_instance):
        """Test univariate regressors raise exception on multivariate X."""
        # check if multivariate input raises error for univariate regressors

        # if handles multivariate, no error is to be raised
        #   that classifier works on multivariate data is tested in test_all_estimators
        if estimator_instance.get_tag("capability:multivariate"):
            return None

        error_msg = "multivariate series"

        # we can use the classifier scenario for multivariate regressors
        #   because the classifier scenario y is float
        scenario = ClassifierFitPredictMultivariate()

        # check if estimator raises appropriate error message
        #   composites will raise a warning, non-composites an exception
        if estimator_instance.is_composite():
            with pytest.warns(UserWarning, match=error_msg):
                scenario.run(estimator_instance, method_sequence=["fit"])
        else:
            with pytest.raises(ValueError, match=error_msg):
                scenario.run(estimator_instance, method_sequence=["fit"])

    def test_regressor_output(self, estimator_instance, scenario):
        """Test regressor outputs the correct data types and values.

        Test predict produces a np.array or pd.Series with only values seen in the train
        data, and that predict_proba probability estimates add up to one.
        """
        X_new = scenario.args["predict"]["X"]
        # we use check_is_scitype to get the number instances in X_new
        #   this is more robust against different scitypes in X_new
        _, _, X_new_metadata = check_is_scitype(X_new, "Panel", return_metadata=True)
        X_new_instances = X_new_metadata["n_instances"]

        # run fit and predict
        y_pred = scenario.run(estimator_instance, method_sequence=["fit", "predict"])

        # check predict
        assert isinstance(y_pred, np.ndarray)
        assert y_pred.shape == (X_new_instances,)
        assert np.issubdtype(y_pred.dtype, np.floating)
