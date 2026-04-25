Calculating the Hamiltonian
===========================

.. seealso::
   Full script: ``examples/calculate_hamiltonian.py``

This example shows how to run Dopyqo to obtain the second-quantized Hamiltonian matrix
elements for a Beryllium calculation, and how to solve it manually using the FCI solver.

Setting up the configuration
-----------------------------

A minimal :class:`~dopyqo.DopyqoConfig` requires only the QE output folder, the
calculation prefix, and the active space definition. No solver flags are set here —
the goal is to inspect the raw matrix elements rather than run FCI or VQE automatically:

.. code-block:: python

   import os
   import dopyqo

   config = dopyqo.DopyqoConfig(
       base_folder=os.path.join("qe_files", "Be"),
       prefix="Be",
       active_electrons=2,
       active_orbitals=4,
       n_threads=10,
   )

Running the calculation
------------------------

Calling :func:`~dopyqo.run` with this config computes all matrix elements and returns
four objects. The ``mats`` object holds the raw integrals:

.. code-block:: python

   energy_dict, wfc_obj, h_ks, mats = dopyqo.run(config)

Inspecting the matrix elements
--------------------------------

The :class:`~dopyqo.MatrixElements` object ``mats`` exposes the one- and two-electron
integrals along with the scalar energy contributions that make up the total energy offset:

.. code-block:: python

   h_pqrs = mats.h_pqrs              # two-electron integrals, shape (N, N, N, N)
   h_pq   = mats.h_pq                # one-electron integrals, shape (N, N)

   energy_frozen_core = mats.energy_frozen_core
   energy_ewald       = mats.energy_ewald
   energy_e_self      = mats.energy_e_self

   print(f"{h_pqrs.shape=}")
   print(f"{h_pq.shape=}")
   print(f"{energy_frozen_core=}")
   print(f"{energy_ewald=}")
   print(f"{energy_e_self=}")

``N`` is the number of active orbitals (4 in this example). The indices follow the
physicists' convention :math:`h_{pqrs} = \langle pq | rs \rangle`.

Solving the Hamiltonian manually
----------------------------------

The :class:`~dopyqo.Hamiltonian` object ``h_ks`` can be used to call the FCI solver
directly, independently of the ``run_fci`` config flag:

.. code-block:: python

   fci_energies = h_ks.solve_fci()
   print(f"{fci_energies=}")

This returns an array of the lowest FCI eigenvalues. By default only the ground state is
computed; use :attr:`~dopyqo.DopyqoConfig.n_fci_energies` to request more states.
