import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import ElasticNet

import config, model_helper


class Model():
    def __init__(self, past_X, y, future_X,
                 energy, region_name):
        # energy can be 'consumption' or 'peak'
        self.past_X = past_X
        self.y = y
        self.future_X = future_X
        self.energy = energy
        self.region_name = region_name

    def fit(self):
        pass

    def predict(self, gdp_type, indeps=None, verbose=False):
        pass

    def get_predictions_train_test(self, indeps=None):
        pass

    def get_train_test_split(self, yr):
        train_X = self.past_X[self.past_X.index.year != yr]
        test_X = self.past_X[self.past_X.index.year == yr]
        train_y = self.y[self.y.index.year != yr]
        test_y = self.y[self.y.index.year == yr]
        return (train_X, test_X, train_y, test_y)

    def metrics(self, indeps=None, test_yr=2019, silent=False):
        predictions, test_y = self.get_predictions_train_test(indeps, test_yr)
        nll = -np.log(
            sum([abs(test_y[i] - predictions[i])
                 for i in range(len(test_y))])
        )
        if not(silent):
            print(
                f'{self.region_name} {self.energy} \nNegative Log likelihood: {nll}',
                f'\nSquared version Log likelihood: ',
                -np.log(
                    sum([(abs(test_y[i] - predictions[i]))**2
                         for i in range(len(test_y))])
                )
            )
        return (f'{self.region_name}_{self.energy}', nll)

    def plot(self, indeps=None):
        predictions, test_y = self.get_predictions_train_test(indeps)
        plt.plot(test_y.index, predictions, label='predicted')
        plt.plot(test_y, label='actual')
        plt.legend()
        plt.title(f'Out of Sample {self.region_name} Region Daily {self.energy}') 
        plt.show()

    def _get_indep(self, x, indeps):
        if self.indeps:
            x = x[self.indeps]
        if indeps:
            x = x[indeps]
        return x

    def _add_gdp_type(self, df, gdp_type):
        """
        Hack to pull out relevant gdp type from three options
        """
        return model_helper.add_gdp_type(df, gdp_type)


class LinearRegression(Model):
    def __init__(self, past_X, y, future_X,
                 energy, region_name, random_state=0,
                 l1_ratio=.9, normalize=False, max_iter=30000,
                 selection='random', alpha=1.0):
        super().__init__(past_X, y, future_X,
                energy, region_name)
        self.random_state = random_state
        self.l1_ratio = l1_ratio
        self.normalize = normalize
        self.max_iter = max_iter
        self.selection = selection
        self.alpha = alpha
        self.regr = ElasticNet(
            random_state=self.random_state,
            l1_ratio = self.l1_ratio, # combination of l1 and l2 penalty
            normalize=self.normalize,
            max_iter=self.max_iter,
            selection=self.selection, # coefficients updated in random order (faster)
            alpha=self.alpha,
        )
        self.indeps = None
        self.predictions = None

    def fit(self, indeps=None, verbose=False):
        x = self.past_X.copy()
        if indeps:
            self.indeps = indeps
            x = self.past_X[self.indeps]
        self.regr.fit(x, self.y)
        if verbose:
            print('Regression Parameters: ', self.regr.get_params())
            print('Parameter Coefficients: ', self.regr.coef_)
            print('Regression intercept: ', self.regr.intercept_)
        print(f'R2 for {self.region_name} {self.energy}: {self.regr.score(x, self.y)}')


    def predict(self, gdp_type=None, indeps=None, verbose=False, past_yrs=None):
        # yrs is optional list of years to predict from the past
        x = self.future_X.copy()
        if past_yrs:
            x = self.past_X[self.past_X.index.year in past_yrs]
        if self.indeps:
            x = self.future_X[self.indeps]
        if gdp_type:
            x = self._add_gdp_type(x, gdp_type)
        self.predictions = self.regr.predict(x)
        return self.predictions

    
    def get_predictions_train_test(self, indeps=None, test_yr=2019):
        regr = ElasticNet(
            random_state=self.random_state,
            l1_ratio = self.l1_ratio, # combination of l1 and l2 penalty
            normalize=self.normalize,
            max_iter=self.max_iter,
            selection=self.selection, # coefficients updated in random order (faster)
            alpha=self.alpha,
        )

        train_X, test_X, train_y, test_y = self.get_train_test_split(test_yr)
        train_X = self._get_indep(train_X, indeps)
        test_X = self._get_indep(test_X, indeps)

        regr.fit(train_X, train_y)
        return regr.predict(test_X), test_y

