FCI and VQE Calculations
========================

.. seealso::
   Full scripts: ``examples/fci_vqe.py``, ``examples/fci_vqe_wannier.py``,
   ``examples/vqe_adapt.py``

This page covers three closely related workflows: a standard FCI + VQE run, the same
calculation with a Wannier transformation applied to the active space, and an ADAPT-VQE
run. All examples use Beryllium as the test system.

Basic FCI + VQE
---------------

Configuration
^^^^^^^^^^^^^

Set ``run_fci=True`` and ``run_vqe=True`` to activate both solvers. Choose a VQE
optimizer and an excitation pool for the UCCSD ansatz:

.. code-block:: python

   import os
   import dopyqo

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Be"),
       prefix="Be",
       active_electrons=2,
       active_orbitals=4,
       run_fci=True,
       run_vqe=True,
       vqe_optimizer=dopyqo.VQEOptimizers.L_BFGS_B,
       vqe_excitations=dopyqo.ExcitationPools.SINGLES_DOUBLES,
       n_threads=10,
   )

Running and extracting energies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:func:`~dopyqo.run` executes both solvers and collects all energies in ``energy_dict``:

.. code-block:: python

   energy_dict, wfc_obj, h_ks, mats = dopyqo.run(config)

   dft_energy = energy_dict["dft_energy"]
   fci_energy = energy_dict["fci_energy"]
   vqe_energy = energy_dict["vqe_energy"]

Plotting VQE convergence
^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`~dopyqo.Hamiltonian` object records every optimizer step. Plotting the
absolute error relative to the FCI reference gives the convergence curve:

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt

   plt.plot(h_ks.vqe_counts, np.abs(h_ks.vqe_values - fci_energy),
            linestyle="-", marker="x")
   plt.yscale("log")
   plt.xlabel("Function evaluations")
   plt.ylabel("|E_VQE - E_FCI| (Ha)")
   plt.grid()
   plt.show()

With Wannier transformation
----------------------------

Dopyqo can transform the Kohn-Sham active-space orbitals into maximally localised
Wannier functions before constructing the Hamiltonian. This requires a Wannier90
``_u.mat`` file generated from a prior Wannier90 run.

Set ``wannier_transform=True`` and point ``base_folder`` at the Wannier output
directory. Increase ``active_electrons`` to match the Wannier orbital count:

.. code-block:: python

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Be_wannier"),
       prefix="Be",
       active_electrons=4,
       active_orbitals=4,
       run_fci=True,
       run_vqe=True,
       vqe_optimizer=dopyqo.VQEOptimizers.L_BFGS_B,
       vqe_excitations=dopyqo.ExcitationPools.SINGLES_DOUBLES,
       wannier_transform=True,
       n_threads=10,
   )

The rest of the workflow — calling :func:`~dopyqo.run` and inspecting energies — is
identical to the basic case above.

If ``wannier_umat`` is not provided, Dopyqo looks for
``{base_folder}/{prefix}_u.mat`` by default. Pass ``wannier_input_file`` to also
validate the active space against the Wannier90 ``.win`` file.

ADAPT-VQE
----------

ADAPT-VQE builds the ansatz iteratively by appending the gradient-largest operator from
a pool at each step, rather than using a fixed UCCSD circuit. Enable it with
``vqe_adapt=True``:

.. code-block:: python

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Be"),
       prefix="Be",
       active_electrons=2,
       active_orbitals=4,
       run_fci=True,
       run_vqe=True,
       vqe_adapt=True,
       vqe_adapt_drain_pool=True,
       vqe_optimizer=dopyqo.VQEOptimizers.L_BFGS_B,
       vqe_excitations=dopyqo.ExcitationPools.SINGLES_DOUBLES,
       n_threads=10,
   )

``vqe_adapt_drain_pool=True`` removes an operator from the pool once it has been
appended to the ansatz, so each operator appears at most once. Set it to ``False`` to
allow repeated use of the same operator.

The call to :func:`~dopyqo.run` and the convergence plot follow the same pattern as
the basic FCI + VQE example.
