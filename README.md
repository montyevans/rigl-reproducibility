# [Reproducibilty Challenge] RigL

This repository hosts source code for our reproducibility report on [Rigging the Lottery: Making all Tickets Winners](https://arxiv.org/abs/1911.11134), published at ICML 2020.


<span class="img_container center" style="display: block;">
    <p align="center">
    <img alt="RigL main image" height=350 src="img/dyn_sparse_train.png" style="display:block; margin-left: auto; margin-right: auto;" title="caption" />
    <br />
    <span class="img_caption" style="display: block; text-align: center;">Figure Courtsey: Evci et al. 2020.</span>
    </p>
</span>

## Getting Started

<details><summary><b>Install</b></summary>
<p>

* `python3.8`
* `pytorch`: 1.7.0+ (GPU support preferable).

Then,
* `make install`
</p>
</details>

<details><summary><b>W&B API key</b></summary>
<p>

Copy your WandB API key to `wandb_api.key`.
Will be used to login to your dashboard for visualisation. 
Alternatively, you can skip W&B visualisation, 
and set `wandb.use=False` while running the python code or `USE_WANDB=False` while running make commands.
</p>
</details>

<details><summary><b>Unit Tests</b></summary>
<p>

`make test`. Run `make help` to see specific make commands.
</p>
</details>

## Example Code

<details><summary><b>Train WideResNet-22-2 with RigL on CIFAR10</b></summary>
<p>

```
make cifar10.ERK.RigL DENSITY=0.2 SEED=0
```

Change `DENSITY` incase you want to use a different density (1 - sparsity) level.
See `outputs/CIFAR10/RigL/0.2` for checkpoints etc. 
</p>
</details>

<details><summary><b>Train ResNet-50 with SNFS on CIFAR100</b></summary>
<p>

```
make cifar100.ERK.SNFS DENSITY=0.2 SEED=0
```

See `outputs/CIFAR100/SNFS/0.2` for checkpoints etc.  
</p>
</details>

<details><summary><b>Evaluate WideResNet-22-2 with RigL on CIFAR10</b></summary>
<p>

Either train WRN-22-2 with RigL as described above, or download checkpoints from here.
Place under `outputs/CIFAR10/RigL/0.2`.

```
make cifar10.ERK.RigL DENSITY=0.2 SEED=0
```
</p>
</details>

<details><summary><b>Evaluate ResNet-50 with SNFS on CIFAR100</b></summary>
<p>

Either train ResNet-50 with SNFS as described above, or download checkpoints from here.
Place under `outputs/CIFAR100/SNFS/0.2`.

```
make cifar100.ERK.SNFS DENSITY=0.2 SEED=0
```  
</p>
</details>

## Main Results

<details><summary><b>Commands</b></summary>
<p>

The following make command runs all the main results described in our reproducibility report.

```
make cifar10 DENSITY=0.05,0.1,0.2,0.5
make cifar100 DENSITY=0.05,0.1,0.2,0.5
make cifar10_tune DENSITY=0.05,0.1,0.2,0.5
```

Use the `-n` flag to see which commands are executed.
Note that these runs are executed sequentially, although we include parallel processes for cifar10 runs of a particular method.
Eg: `cifar10.Random.RigL` runs RigL Random for densities `0.05,0.1,0.2,0.5`, `seed=0` in parallel.

It may be preferable to run specific make commands in parallel for this reason. See `make help` for an exhaustive list.

</p>
</details>

<details><summary><b>Table of Results</b></summary>
<p>

Shown for 80% sparsity (20% density) on CIFAR10. For exhaustive results and their analysis refer to our report.
</p>
</details>


<details><summary><b>Visualization & Plotting Code</b></summary>
<p>

Run `make vis`.
</p>
</details>

## Misc

This section may be useful if you desire to extend this code base or understand its structure.
`main.py` is the python file used for training-evaluating, and the `make` commands serve as a wrapper for it.

<details><summary><b>Print current config</b></summary>
<p>

We use [hydra](https://hydra.cc/docs/intro) to handle configs.

```
python main.py --cfg job
```

See `conf/configs` for a detailed list of default configs, and under each folder of `conf` for possible options.

</p>
</details>

<details><summary><b>Understanding the config setup</b></summary>
<p>

We split configs into various config groups for brevity.

Config groups (example):
* masking
* optimizer
* dataset 
etc.

Hydra allows us to override these either group-wise or globally as described below.
</p>
</details>

<details><summary><b>Overrriding options / group configs</b></summary>
<p>

`python main.py masking=RigL wandb.use=True`

Refer to hydra's documentation for more details.
</p>
</details>


<details><summary><b>Exhaustive config options</b></summary>
<p>

See `conf/config.yaml` and the defaults it uses (eg: `dataset: CIFAR10`, `optimizer: SGD`, etc.).
</p>
</details>


<details><summary><b>Using specific configs</b></summary>
<p>

Sometimes, we want to store the specific config of a run with tuned options across mutliple groups (masking, optimizer etc.)

To do so:

* store your config under `specific/`. 
* each YAML file must start with a `# @package _global_` directive. See `specific/` for existing examples. 
* override only what has changed, i.e., donot keep redundant arguments, which the base config (`config.yaml`) already covers.

Syntax:

`python main.py +specific=cifar_wrn_22_2_rigl`
</p>
</details>

## References

1. Rigging the Lottery: Making All Tickets Winners, [Original Paper](https://arxiv.org/abs/1911.11134).

2. Our report on OpenReview.