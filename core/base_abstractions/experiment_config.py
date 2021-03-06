"""Defines the `ExperimentConfig` abstract class used as the basis of all
experiments."""

import abc
from typing import Dict, Any, Optional, List

import torch.nn as nn

from core.base_abstractions.task import TaskSampler
from utils.experiment_utils import TrainingPipeline


class FrozenClassVariables(abc.ABCMeta):
    """Metaclass for ExperimentConfig.

    Ensures ExperimentConfig class-level attributes cannot be modified.
    ExperimentConfig attributes can still be modified at the object
    level.
    """

    def __setattr__(cls, attr, value):
        if isinstance(cls, type) and (
            attr != "__abstractmethods__" and not attr.startswith("_abc_")
        ):
            raise RuntimeError(
                "Cannot edit class-level attributes.\n"
                "Changing the values of class-level attributes is disabled in ExperimentConfig classes.\n"
                "This is to prevent problems that can occur otherwise when using multiprocessing.\n"
                "If you wish to change the value of a configuration, please do so for an instance of that"
                "configuration.\nTriggered by attempting to modify {}".format(
                    cls.__name__
                )
            )
        else:
            super().__setattr__(attr, value)


class ExperimentConfig(metaclass=FrozenClassVariables):
    """Abstract class used to define experiments.

    Instead of using yaml or text files, experiments in our framework
    are defined as a class. In particular, to define an experiment one
    must define a new class inheriting from this class which implements
    all of the below methods. The below methods will then be called when
    running the experiment.
    """

    @classmethod
    @abc.abstractmethod
    def tag(cls) -> str:
        """A string describing the experiment."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def training_pipeline(cls, **kwargs) -> TrainingPipeline:
        """Creates the training pipeline.

        # Parameters

        kwargs : Extra kwargs. Currently unused.

        # Returns

        An instantiate `TrainingPipeline` object.
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def machine_params(cls, mode="train", **kwargs) -> Dict[str, Any]:
        """Parameters used to specify machine information.

        Machine information includes at least (1) the number of processes
        to train with and (2) the gpu devices indices to use.

        mode : Whether or not the machine parameters should be those for
            "train", "valid", or "test".
        kwargs : Extra kwargs.

        # Returns

        A dictionary of the form `{"nprocesses": ..., "gpu_ids": ..., ...}`.
        Here `nprocesses` must be a non-negative integer, `gpu_ids` must
        be a sequence of non-negative integers (if empty, then everything
        will be run on the cpu).
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def create_model(cls, **kwargs) -> nn.Module:
        """Create the neural model."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def make_sampler_fn(cls, **kwargs) -> TaskSampler:
        """Create the TaskSampler given keyword arguments.

        These `kwargs` will be generated by one of
        `ExperimentConfig.train_task_sampler_args`,
        `ExperimentConfig.valid_task_sampler_args`, or
        `ExperimentConfig.test_task_sampler_args` depending on whether
        the user has chosen to train, validate, or test.
        """
        raise NotImplementedError()

    def train_task_sampler_args(
        self,
        process_ind: int,
        total_processes: int,
        devices: Optional[List[int]] = None,
        seeds: Optional[List[int]] = None,
        deterministic_cudnn: bool = False,
    ) -> Dict[str, Any]:
        """Specifies the training parameters for the `process_ind`th training
        process.

        These parameters are meant be passed as keyword arguments to `ExperimentConfig.make_sampler_fn`
        to generate a task sampler.

        # Parameters

        process_ind : The unique index of the training process (`0 ≤ process_ind < total_processes`).
        total_processes : The total number of training processes.
        devices : Gpu devices (if any) to use.
        seeds : The seeds to use, if any.
        deterministic_cudnn : Whether or not to use deterministic cudnn.

        # Returns

        The parameters for `make_sampler_fn`
        """
        raise NotImplementedError()

    def valid_task_sampler_args(
        self,
        process_ind: int,
        total_processes: int,
        devices: Optional[List[int]] = None,
        seeds: Optional[List[int]] = None,
        deterministic_cudnn: bool = False,
    ) -> Dict[str, Any]:
        """Specifies the validation parameters for the `process_ind`th
        validation process.

        See `ExperimentConfig.train_task_sampler_args` for parameter
        definitions.
        """
        raise NotImplementedError()

    def test_task_sampler_args(
        self,
        process_ind: int,
        total_processes: int,
        devices: Optional[List[int]] = None,
        seeds: Optional[List[int]] = None,
        deterministic_cudnn: bool = False,
    ) -> Dict[str, Any]:
        """Specifies the test parameters for the `process_ind`th test process.

        See `ExperimentConfig.train_task_sampler_args` for parameter
        definitions.
        """
        raise NotImplementedError()
