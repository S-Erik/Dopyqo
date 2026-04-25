Reading Wannier90 Output
=========================

.. seealso::
   Full script: ``examples/read_wannier90_output.py``

When a Wannier90 calculation has been performed alongside the QE run, Dopyqo provides
utilities to read the transformation matrix and the Hamiltonian in the Wannier basis.
This can be useful for inspecting the Wannier basis independently of a full Dopyqo run.

Reading the unitary transformation matrix
------------------------------------------

The ``_u.mat`` file written by Wannier90 contains the unitary transformation matrices
:math:`U^{(\mathbf{k})}` from the Bloch to the Wannier basis. Use
:func:`~dopyqo.read_u_mat` to load it as a dictionary keyed by k-point index:

.. code-block:: python

   import os
   import dopyqo

   base_folder = os.path.join("qe_files", "Be_wannier")
   filename_umat = os.path.join(base_folder, "Be_u.mat")

   kpt_to_u = dopyqo.read_u_mat(filename=filename_umat)

Each value in ``kpt_to_u`` is a 2D NumPy array of shape ``(n_wann, n_bands)``.

Reading the real-space Hamiltonian
------------------------------------

The ``_hr.dat`` file contains the Hamiltonian matrix elements
:math:`H_{\mathbf{R}}` in the Wannier basis, where :math:`\mathbf{R}` are lattice
vectors. Use :func:`~dopyqo.wannier90.read_hr_dat` to load it:

.. code-block:: python

   import dopyqo.wannier90
   import numpy as np

   filename_hr = os.path.join(base_folder, "Be_hr.dat")
   hr_mat = dopyqo.wannier90.read_hr_dat(filename=filename_hr)

The returned array has shape ``(n_wann, n_wann, n_R)`` where the last index runs over
lattice vectors. The on-site block ``hr_mat[:, :, 0]`` corresponds to :math:`\mathbf{R} = \mathbf{0}`.

Diagonalising and checking unitarity
--------------------------------------

The on-site block gives the Kohn-Sham eigenvalues and eigenvectors in the Wannier basis.
Diagonalise it with NumPy and verify that the transformation matrix is unitary:

.. code-block:: python

   # KS eigenvalues and eigenvectors in the Wannier basis
   eigvals, eigvecs = np.linalg.eig(hr_mat[:, :, 0])

   # Stack all k-point matrices and check unitarity of the first one
   u_mat = np.stack(list(kpt_to_u.values()), axis=2)
   print(f"Unitary: {dopyqo.wannier90.check_unitarity_u(u_mat[:, :, 0])}")
