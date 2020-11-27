from dataclasses import dataclass
import logging
from math import floor
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.typing_alias import *


@dataclass
class DatasetSplitter(Dataset):
    """This splitter makes sure that we always use the same training/validation split"""

    parent_dataset: Dataset
    split: "slice" = slice(None, None)

    def __post_init__(self):
        if len(self) <= 0:
            raise ValueError(f"Dataset split {self.split} is not positive")

    def __len__(self):
        # absolute indices
        _indices = self.split.indices(len((self.parent_dataset)))
        # compute length
        return len(range(*_indices))

    def __getitem__(self, index):
        assert index < len(self), "index out of bounds in split_datset"
        return self.parent_dataset[index + int(self.split.start or 0)]


def _get_CIFAR10_dataset(root: "Path") -> "Union[Dataset,Dataset]":
    normalize = transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))

    train_transform = transforms.Compose(
        [
            transforms.Pad(4, padding_mode="reflect"),
            transforms.RandomCrop(32),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            normalize,
        ]
    )

    test_transform = transforms.Compose([transforms.ToTensor(), normalize])

    full_dataset = datasets.CIFAR10(
        root, train=True, transform=train_transform, download=True
    )
    test_dataset = datasets.CIFAR10(
        root, train=False, transform=test_transform, download=False
    )

    return full_dataset, test_dataset


def _get_Mini_Imagenet_dataset(root: "Path") -> "Union[Dataset,Dataset]":
    pass


def _get_MNIST_dataset(root: "Path") -> "Union[Dataset,Dataset]":
    normalize = transforms.Normalize((0.1307,), (0.3081,))
    transform = transforms.Compose([transforms.ToTensor(), normalize])

    full_dataset = datasets.MNIST(root, train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root, train=False, transform=transform)

    return full_dataset, test_dataset


def get_dataloaders(
    name: str,
    root: "Path",
    batch_size: int = 1,
    test_batch_size: int = 1,
    validation_split: float = 0.0,
    max_threads: int = 3,
):
    """Creates augmented train, validation, and test data loaders."""

    assert name in registry.keys()
    full_dataset, test_dataset = registry[name](root)

    # we need at least two threads in total
    max_threads = max(2, max_threads)
    val_threads = 2 if max_threads >= 6 else 1
    train_threads = max_threads - val_threads

    # Split into train and val
    train_dataset = full_dataset
    if validation_split:
        split = int(floor((1.0 - validation_split) * len(full_dataset)))
        train_dataset = DatasetSplitter(full_dataset, slice(None, split))
        val_dataset = DatasetSplitter(full_dataset, slice(split, None))

    train_loader = DataLoader(
        train_dataset,
        batch_size,
        num_workers=train_threads,
        pin_memory=False,
        shuffle=True,
        multiprocessing_context="fork",
    )

    if validation_split:
        valid_loader = DataLoader(
            val_dataset,
            test_batch_size,
            num_workers=val_threads,
            pin_memory=False,
            multiprocessing_context="fork",
        )

    test_loader = DataLoader(
        test_dataset,
        test_batch_size,
        shuffle=False,
        num_workers=1,
        pin_memory=False,
        multiprocessing_context="fork",
    )
    logging.info(f"Train dataset length {len(train_dataset)}")
    logging.info(f"Val dataset length {len(val_dataset) if validation_split else 0}")
    logging.info(f"Test dataset length {len(test_dataset)}")

    if not validation_split:
        logging.info("Running periodic eval on test data.")
        valid_loader = test_loader

    return train_loader, valid_loader, test_loader


registry = {
    "CIFAR10": _get_CIFAR10_dataset,
    "Mini-Imagenet": _get_Mini_Imagenet_dataset,
    "MNIST": _get_MNIST_dataset,
}
