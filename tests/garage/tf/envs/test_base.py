import gym
import pytest

from garage.tf.envs.base import TfEnv
from tests.helpers import step_env_with_gym_quirks


class TestTfEnv:
    @pytest.mark.nightly
    @pytest.mark.parametrize('spec', list(gym.envs.registry.all()))
    def test_all_gym_envs(self, spec):
        env = TfEnv(spec.make())
        step_env_with_gym_quirks(env, spec)

    @pytest.mark.nightly
    @pytest.mark.parametrize('spec', list(gym.envs.registry.all()))
    def test_all_gym_envs_pickleable(self, spec):
        env = TfEnv(env_name=spec.id)
        step_env_with_gym_quirks(
            env, spec, n=1, render=True, serialize_env=True)
