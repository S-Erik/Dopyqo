Using Custom Matrix Elements
============================

.. seealso::
   Full script: ``examples/custom_hamiltonian.py``

Dopyqo normally computes all matrix elements from the QE wavefunction. This example
shows how to override one or more of them with custom values — for instance to test
a solver against a known Hamiltonian, or to inject externally computed integrals.

Creating custom integrals
--------------------------

Here we use TenCirChem's ``random_integral`` helper to generate a random but physically
valid one- and two-electron integral tensor for four spatial orbitals:

.. code-block:: python

   import numpy as np
   from tencirchem.static.hamiltonian import random_integral

   active_orbitals = 4
   h1e_core_custom, h2e_custom = random_integral(active_orbitals)

   # random_integral returns chemists'-ordered ERIs; convert to physicists' order
   h2e_custom = h2e_custom.transpose((0, 2, 3, 1))

The transpose maps from chemists' notation :math:`\langle ij|kl \rangle` to the
physicists' notation :math:`\langle ij|kl \rangle_\text{phys}` expected by Dopyqo.

Wrapping integrals in MatrixElements
--------------------------------------

Pass the custom integrals to :class:`~dopyqo.MatrixElements`. Any field left as
``None`` (the default) will be computed from the QE wavefunction during the run:

.. code-block:: python

   import dopyqo

   mats_custom = dopyqo.MatrixElements(
       h_pq_core=h1e_core_custom,
       h_pqrs=h2e_custom,
       # remaining fields (frozen core energy, Ewald, etc.) computed automatically
   )

Running with the custom Hamiltonian
-------------------------------------

Pass the :class:`~dopyqo.MatrixElements` object as the second argument to
:func:`~dopyqo.run`. Dopyqo uses the provided integrals in place of the ones it would
have computed:

.. code-block:: python

   import os

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Be"),
       prefix="Be",
       active_electrons=2,
       active_orbitals=active_orbitals,
       run_fci=True,
       run_vqe=True,
       vqe_optimizer=dopyqo.VQEOptimizers.L_BFGS_B,
       vqe_excitations=dopyqo.ExcitationPools.SINGLES_DOUBLES,
       n_threads=10,
   )
   energy_dict, wfc_obj, h_ks, mats = dopyqo.run(config, mats_custom)

   fci_energy = energy_dict["fci_energy"]
   vqe_energy = energy_dict["vqe_energy"]

Plotting VQE convergence
--------------------------

Because the custom integrals are random, the VQE convergence plot shows how well the
ansatz approximates a generic active-space Hamiltonian rather than a real material:

.. code-block:: python

   import matplotlib.pyplot as plt

   plt.plot(h_ks.vqe_counts, np.abs(h_ks.vqe_values - fci_energy),
            linestyle="-", marker="x")
   plt.yscale("log")
   plt.xlabel("Function evaluations")
   plt.ylabel("|E_VQE - E_FCI| (Ha)")
   plt.grid()
   plt.show()
