Quickstart
==========

Python API
----------

The primary way to use Dopyqo is through its Python interface. Provide a
:class:`~dopyqo.DopyqoConfig` object and call :func:`~dopyqo.run`:

.. code-block:: python

   import os
   import dopyqo

   config = dopyqo.DopyqoConfig(
       base_folder="path/to/your/qe/calculation",
       prefix="PrefixUsedInYourQECalculation",
       active_electrons=2,
       active_orbitals=4,
       run_fci=True,
       run_vqe=True,
       use_qiskit=False,        # Use TenCirChem (default); True for Qiskit
       vqe_optimizer=dopyqo.VQEOptimizers.L_BFGS_B,
       vqe_excitations=dopyqo.ExcitationPools.SINGLES_DOUBLES,
       n_threads=10,
   )
   energy_dict, wfc_obj, h_ks, mats = dopyqo.run(config)

The ``base_folder`` must contain a ``{prefix}.save/`` directory as produced by
Quantum ESPRESSO. The required files inside are ``data-file-schema.xml`` and the
wavefunction files (``wfc.dat`` or ``wfc.hdf5``).

The returned ``energy_dict`` contains the computed energies, e.g.
``energy_dict["dft_energy"]``, ``energy_dict["fci_energy"]``,
``energy_dict["vqe_energy"]``.

CLI (TOML input)
----------------

Dopyqo can also be launched from the command line using a TOML input file:

.. code-block:: bash

   dopyqo -i your_input_file.toml

The TOML interface currently covers only a subset of the Python API's functionality.
See the |dopyqo.input_md|_ on GitHub for the full input file specification, and the |dopyqo.toml|_ file for a working example.

.. |dopyqo.input_md| replace:: ``INPUT.md``
.. _dopyqo.input_md: https://github.com/dlr-wf/Dopyqo/blob/main/INPUT.md

.. |dopyqo.toml| replace:: ``examples/dopyqo.toml``
.. _dopyqo.toml: https://github.com/dlr-wf/Dopyqo/blob/main/examples/dopyqo.toml

K-point calculations
--------------------

For calculations involving multiple k-points, specify which k-point to load
using ``kpoint_idx`` (zero-based index) or set it to ``"all"`` to process
every k-point:

.. code-block:: python

   config = dopyqo.DopyqoConfig(
       ...,
       kpoint_idx=0,   # or kpoint_idx="all"
   )

General k-point calculations currently only work with Qiskit or PySCF solvers.
:math:`\Gamma`-only calculations also work with TenCirChem.

Modifying a configuration
--------------------------

:class:`~dopyqo.DopyqoConfig` is a frozen dataclass. Use
:func:`dataclasses.replace` to create a modified copy:

.. code-block:: python

   import dataclasses

   config2 = dataclasses.replace(config, run_vqe=False, run_fci=True)
