
from models.survival import Model

model = Model()
model.get_data()


def test_logit():
    model.set_model_type('Logit')
    spec = ['ctgrCardLevel','ctgrSalesChannel','dmMassOffer','nIsPayroll']
    assert model.fit(spec, fit_intercept=True)


def test_km():
    model.set_model_type('Kaplan-Meier')
    assert model.fit()


def test_cox():
    model.set_model_type('Cox')
    spec = ['ctgrCardLevel','ctgrSalesChannel','dmMassOffer','nIsPayroll']
    assert model.fit(id_col='nAgrmntId', stop_col='nMonth', specification=spec)
