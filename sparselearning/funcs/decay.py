from dataclasses import dataclass

import torch
import torch.optim as optim


@dataclass
class Decay(object):
    def __init__(self):
        self.mode = "current"

    def step(self):
        raise NotImplementedError

    def get_dr(self):
        raise NotImplementedError


class CosineDecay(Decay):
    """Decays a pruning rate according to a cosine schedule

    This class is just a wrapper around PyTorch's CosineAnnealingLR.
    """

    def __init__(
        self,
        prune_rate: float = 0.3,
        T_max: int = 1000,
        eta_min: float = 0.0,
        last_epoch: int = -1,
    ):
        super().__init__()
        self._step = 0
        self.T_max = T_max

        self.sgd = optim.SGD(
            torch.nn.ParameterList([torch.nn.Parameter(torch.zeros(1))]), lr=prune_rate
        )
        self.cosine_stepper = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.sgd, T_max, eta_min, last_epoch
        )

    def step(self, step: int = -1):
        if step >= 0:
            if self._step < self.T_max:
                self.cosine_stepper.step(step)
                self._step = step + 1
            else:
                self._step = self.T_max
            return
        if self._step < self.T_max:
            self.cosine_stepper.step()
            self._step += 1

    def get_dr(self):
        return self.sgd.param_groups[0]["lr"]


class LinearDecay(Decay):
    """Anneals the pruning rate linearly with each step."""

    def __init__(self, prune_rate: float, T_max: int):
        super().__init__()

        self._step = 0
        self.T_max = T_max

        self.decrement = prune_rate / float(T_max)
        self.current_prune_rate = prune_rate
        self.initial_prune_rate = prune_rate

    def step(self, step: int = -1):
        if step >= 0:
            if self._step < self.T_max:
                self.current_prune_rate = self.initial_prune_rate - self.decrement * (
                    step + 1
                )
                self._step = step + 1
            else:
                self._step = self.T_max
            return
        if self._step < self.T_max:
            self.current_prune_rate -= self.decrement
            self._step += 1

    def get_dr(self):
        return self.current_prune_rate


@dataclass
class MagnitudePruneDecay(Decay):
    """
    Anneals according to Zhu et al., "To prune or not to prune"

    We implement cumulative sparsity and take a finite difference to get sparsity(t).

    Amount to prune = sparsity.
    """

    initial_sparsity: float = 0.0
    final_sparsity: float = 0.3
    T_max: int = 30000
    T_start: int = 350
    interval: int = 100

    def __post_init__(self):
        self.mode = "cumulative"
        self.current_prune_rate = 0.0
        self._step = 0

    def cumulative_sparsity(self, step):
        if step < self.T_start:
            return self.initial_sparsity
        elif step < self.T_max:
            mul = (1 - (step - self.T_start) / (self.T_max - self.T_start)) ** 3
            return (
                self.final_sparsity
                + (self.initial_sparsity - self.final_sparsity) * mul
            )
        elif step >= self.T_max:
            return self.final_sparsity

    def step(self, step: int = -1, current_sparsity=-1):
        if step == -1:
            step = self._step

        if current_sparsity == -1:
            current_sparsity = self.cumulative_sparsity(step - self.interval)

        self.current_prune_rate = self.cumulative_sparsity(step) - current_sparsity

        step += 1
        self._step = step

    def get_dr(self):
        return self.current_prune_rate


def decay_test():
    from matplotlib import pyplot as plt

    decay = MagnitudePruneDecay(
        initial_sparsity=0.0, final_sparsity=0.8, T_max=65000, T_start=700, interval=100
    )

    prune_rate = []
    sparsity = []
    i_ll = []
    for i in range(0, 65000, 100):
        i_ll.append(i)
        decay.step(i)
        prune_rate.append(decay.get_dr())
        sparsity.append(decay.cumulative_sparsity(i))

    plt.plot(i_ll, sparsity)
    plt.show()
    plt.plot(i_ll, prune_rate)
    plt.show()


registry = {
    "cosine": CosineDecay,
    "linear": LinearDecay,
    "magnitude-prune": MagnitudePruneDecay,
}

if __name__ == "__main__":
    decay_test()
