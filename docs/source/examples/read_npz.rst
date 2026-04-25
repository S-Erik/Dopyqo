Reading Saved Output Files
===========================

.. seealso::
   Full script: ``examples/read_npz_file.py``

After a Dopyqo run, energies and statevectors are saved to compressed NumPy archives
(``.npz``) in the calculation folder. This example shows how to load and inspect those
files without re-running the calculation.

Locating the saved file
------------------------

Dopyqo writes two kinds of ``.npz`` files. The energy archive is named after the active
space: ``energies_{n_elec}e_{n_orb}o.npz``. Set the active-space parameters to match
the run you want to inspect:

.. code-block:: python

   import os
   import numpy as np

   base_folder = os.path.join("qe_files", "Be")
   prefix = "Be"
   active_electrons = 2
   active_orbitals = 2

   npz_path = os.path.join(base_folder,
                            f"energies_{active_electrons}e_{active_orbitals}o.npz")

Loading and iterating over entries
------------------------------------

Load the archive with ``allow_pickle=True`` (required for dict-valued arrays) and
print every stored key–value pair:

.. code-block:: python

   data = np.load(npz_path, allow_pickle=True)
   for key, val in data.items():
       print(f"{key}: {val}")

Typical keys include ``dft_energy``, ``fci_energy``, ``vqe_energy``, and
``vqe_parameters``. A second archive named ``statevecs_{n_elec}e_{n_orb}o.npz``
stores the FCI and VQE statevectors and is used for post-processing such as Bader
charge analysis.
