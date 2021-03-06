import pickle
from unittest import mock

import numpy as np
import pytest
import tensorflow as tf

from garage.tf.baselines import GaussianCNNBaselineWithModel
from garage.tf.envs import TfEnv
from tests.fixtures import TfGraphTestCase
from tests.fixtures.envs.dummy import DummyBoxEnv
from tests.fixtures.regressors import SimpleGaussianCNNRegressor


class TestGaussianCNNBaselineWithModel(TfGraphTestCase):
    @pytest.mark.parametrize('obs_dim', [[1], [2], [1, 1], [2, 2]])
    def test_fit(self, obs_dim):
        box_env = TfEnv(DummyBoxEnv(obs_dim=obs_dim))
        with mock.patch(('garage.tf.baselines.'
                         'gaussian_cnn_baseline_with_model.'
                         'GaussianCNNRegressorWithModel'),
                        new=SimpleGaussianCNNRegressor):
            gcb = GaussianCNNBaselineWithModel(env_spec=box_env.spec)
        paths = [{
            'observations': [np.full(obs_dim, 1)],
            'returns': [1]
        }, {
            'observations': [np.full(obs_dim, 2)],
            'returns': [2]
        }]
        gcb.fit(paths)

        obs = {'observations': [np.full(obs_dim, 1), np.full(obs_dim, 2)]}
        prediction = gcb.predict(obs)
        assert np.array_equal(prediction, [1, 2])

    @pytest.mark.parametrize('obs_dim', [[1], [2], [1, 1], [2, 2]])
    def test_param_values(self, obs_dim):
        box_env = TfEnv(DummyBoxEnv(obs_dim=obs_dim))
        with mock.patch(('garage.tf.baselines.'
                         'gaussian_cnn_baseline_with_model.'
                         'GaussianCNNRegressorWithModel'),
                        new=SimpleGaussianCNNRegressor):
            gcb = GaussianCNNBaselineWithModel(env_spec=box_env.spec)
            new_gcb = GaussianCNNBaselineWithModel(
                env_spec=box_env.spec, name='GaussianCNNBaselineWithModel2')

        # Manual change the parameter of GaussianCNNBaselineWithModel
        with tf.variable_scope('GaussianCNNBaselineWithModel', reuse=True):
            return_var = tf.get_variable('SimpleGaussianCNNModel/return_var')
        return_var.load(1.0)

        old_param_values = gcb.get_param_values()
        new_param_values = new_gcb.get_param_values()
        assert not np.array_equal(old_param_values, new_param_values)
        new_gcb.set_param_values(old_param_values)
        new_param_values = new_gcb.get_param_values()
        assert np.array_equal(old_param_values, new_param_values)

    @pytest.mark.parametrize('obs_dim', [[1], [2], [1, 1], [2, 2]])
    def test_get_params_internal(self, obs_dim):
        box_env = TfEnv(DummyBoxEnv(obs_dim=obs_dim))
        with mock.patch(('garage.tf.baselines.'
                         'gaussian_cnn_baseline_with_model.'
                         'GaussianCNNRegressorWithModel'),
                        new=SimpleGaussianCNNRegressor):
            gcb = GaussianCNNBaselineWithModel(
                env_spec=box_env.spec, regressor_args=dict())
        params_interal = gcb.get_params_internal()
        trainable_params = tf.trainable_variables(
            scope='GaussianCNNBaselineWithModel')
        assert np.array_equal(params_interal, trainable_params)

    def test_is_pickleable(self):
        box_env = TfEnv(DummyBoxEnv(obs_dim=(1, )))
        with mock.patch(('garage.tf.baselines.'
                         'gaussian_cnn_baseline_with_model.'
                         'GaussianCNNRegressorWithModel'),
                        new=SimpleGaussianCNNRegressor):
            gcb = GaussianCNNBaselineWithModel(env_spec=box_env.spec)
        obs = {'observations': [np.full(1, 1), np.full(1, 1)]}

        with tf.variable_scope('GaussianCNNBaselineWithModel', reuse=True):
            return_var = tf.get_variable('SimpleGaussianCNNModel/return_var')
        return_var.load(1.0)

        prediction = gcb.predict(obs)

        h = pickle.dumps(gcb)

        with tf.Session(graph=tf.Graph()):
            gcb_pickled = pickle.loads(h)
            prediction2 = gcb_pickled.predict(obs)

            assert np.array_equal(prediction, prediction2)
