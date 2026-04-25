Bader Charge Analysis
======================

.. seealso::
   Full script: ``examples/bader_charges.py``

Bader charge analysis partitions the total electron density into atomic contributions,
giving an effective charge per atom. Dopyqo enables this analysis at three levels of
theory: DFT (Kohn-Sham density), CASCI (FCI density from the one-particle reduced
density matrix), and VQE (VQE density from the one-particle reduced density matrix).
This tutorial walks through all three using Mg\ :sub:`2`\ Si as the example system.

Prerequisites
--------------

Before running this script you need:

* A completed QE SCF calculation (``Mg2Si.scf.in``).
* A charge density written as a ``.cube`` file using the QE ``pp.x`` post-processing
  tool (``Mg2Si.pp.in`` with ``plot_num=0``). Dopyqo uses this as the QE reference.
* The `Bader executable <http://theory.cm.utexas.edu/henkelman/code/bader/>`_ installed
  and its path set in ``path_to_bader_executable``.

Running the Dopyqo calculation
---------------------------------

Set up the config with both FCI and VQE enabled. The ``uccsd_reps`` parameter controls
the number of UCCSD layers in the VQE ansatz:

.. code-block:: python

   import os
   import numpy as np
   import dopyqo

   base_folder = os.path.join("qe_files", "Mg2Si")
   prefix = "Mg2Si"
   active_electrons = 6
   active_orbitals  = 5
   path_to_bader_executable = {
       "bader": os.path.join(os.path.expanduser("~"), "bader/bader")
   }

   config = dopyqo.DopyqoConfig(
       base_folder=base_folder,
       prefix=prefix,
       active_electrons=active_electrons,
       active_orbitals=active_orbitals,
       run_fci=True,
       run_vqe=True,
       vqe_optimizer=dopyqo.VQEOptimizers.L_BFGS_B,
       n_threads=10,
       uccsd_reps=1,
   )

   energy_dict, wfc_obj, h_ks, mats = dopyqo.run(config)

Saving FCI/VQE state data
---------------------------

Immediately after the run, save the FCI eigenvectors and VQE CI vector to a ``.npz``
file. This lets you reload the wavefunctions later (e.g. for a follow-up Bader analysis
or a different active space) without re-running the full DFT post-processing:

.. code-block:: python

   npz_path = os.path.join(base_folder,
                            f"statevecs_{active_electrons}e_{active_orbitals}o.npz")
   save_data = {"norb": h_ks.norb, "nelec": h_ks.nelec}

   if len(h_ks.fci_evcs) > 0:
       save_data["fci_evcs"] = h_ks.fci_evcs[0]

   vqe_ci_vec = None
   if h_ks.tcc_vqe_result is not None:
       vqe_ci_vec = h_ks.tcc_ansatz.civector(h_ks.tcc_vqe_params)
       save_data["vqe_ci_vec"] = vqe_ci_vec
       save_data["vqe_params"]  = h_ks.tcc_vqe_params

   np.savez(npz_path, **save_data)

``h_ks.fci_evcs[0]`` is the FCI ground-state coefficient vector in the Fock-space
basis. ``vqe_ci_vec`` is the analogous vector reconstructed from the TenCirChem ansatz
at the optimised parameters. Both are stored alongside ``norb`` and ``nelec`` so that
:meth:`pyscf.fci.direct_spin1.FCIBase.make_rdm1` can be called on them later without
the ``h_ks`` object being present.

Note that ``vqe_ci_vec`` is computed here once and reused below in the VQE Bader
section, avoiding a second call to ``civector``.

Transforming KS orbitals to real space
-----------------------------------------

Bader analysis requires the electron density on a real-space grid. The Kohn-Sham
orbitals :math:`\psi_i(\mathbf{r})` are obtained by inverse Fourier transform of the
plane-wave coefficients. First, map the coefficients from the flat plane-wave list onto
a 3D grid indexed by Miller indices:

.. code-block:: python

   from dopyqo import cube

   atoms   = [at["element"] for at in wfc_obj.atoms]
   valence = {x.element: x.z_valence for x in wfc_obj.pseudopots}

   c_ip    = wfc_obj.evc        # plane-wave coefficients, shape (#bands, #waves)
   mill    = wfc_obj.mill       # Miller indices, shape (#waves, 3)
   nbands  = wfc_obj.nbnd
   max_min = wfc_obj.fft_grid   # FFT grid dimensions

   c_ip_array = np.zeros((nbands, *max_min), dtype=c_ip.dtype)
   for idx, (x, y, z) in enumerate(mill):
       c_ip_array[:, x + max_min[0] // 2,
                     y + max_min[1] // 2,
                     z + max_min[2] // 2] = c_ip[:, idx]

Then apply the inverse FFT to obtain :math:`\psi_i(\mathbf{r})` for each band:

.. code-block:: python

   psi_r = np.array([
       np.fft.ifftn(np.fft.ifftshift(c_ip_array[i])) * np.sqrt(np.prod(max_min))
       for i in range(nbands)
   ])

DFT (Kohn-Sham) Bader charges
---------------------------------

The total KS electron density is built by summing :math:`|\psi_i(\mathbf{r})|^2`
weighted by occupations. :func:`~dopyqo.cube.get_density_cube` handles the weighted
sum; the result is then normalised to units of electrons per unit volume:

.. code-block:: python

   ks_single_density = np.abs(psi_r) ** 2
   ks_tot_density = cube.get_density_cube(ks_single_density, wfc_obj.occupations_xml)
   ks_tot_density /= wfc_obj.cell_volume / np.prod(wfc_obj.fft_grid) / 2.0

Write the density as a ``.cube`` file, run the Bader executable, and parse the
``ACF.dat`` output:

.. code-block:: python

   save_dir = os.path.join(base_folder, "Bader_dopyqo")
   cube.make_cube(base_folder, prefix, ks_tot_density, save_dir,
                  path_to_bader_executable, max_min)
   ks_bader = cube.extract_charge(atoms,
                                   os.path.join(save_dir, "ACF.dat"), valence)

For reference, also run Bader analysis on the ``.cube`` file written by QE ``pp.x``:

.. code-block:: python

   ppx_dir  = os.path.join(base_folder, "Bader_QE")
   ppx_file = os.path.join(base_folder, f"{prefix}_pp.cube")
   cube.run_ppx(ppx_file, path_to_bader_executable, ppx_dir, prefix)
   qe_bader = cube.extract_charge(atoms,
                                   os.path.join(ppx_dir, "ACF.dat"), valence)

CASCI (FCI) Bader charges
----------------------------

At the CASCI level, the electron density is computed from the one-particle reduced
density matrix (1-RDM) :math:`\gamma_{ij}` of the FCI wavefunction:

.. math::

   \rho(\mathbf{r}) = \sum_{ij} \gamma_{ij}\, \psi^*_i(\mathbf{r})\, \psi_j(\mathbf{r})

Build the 1-RDM for the active space using PySCF and embed it into a full-space matrix
that accounts for the doubly occupied core orbitals:

.. code-block:: python

   import pandas as pd

   if len(h_ks.fci_evcs) > 0:
       fci_rdm1 = h_ks.fci_solver.make_rdm1(
           h_ks.fci_evcs[0], h_ks.norb, (h_ks.nelec, h_ks.nelec)
       )

       passive_filled = round((wfc_obj.nelec - active_electrons) / 2)
       fci_rdm1_total = np.zeros((nbands, nbands))
       for i in range(passive_filled):
           fci_rdm1_total[i, i] = 1.0       # core orbitals fully occupied
       fci_rdm1_total[
           passive_filled : passive_filled + h_ks.norb,
           passive_filled : passive_filled + h_ks.norb,
       ] = fci_rdm1 / 2.0

Reconstruct the density on the real-space grid and normalise:

.. code-block:: python

       fci_tot_density = np.zeros(max_min, dtype=c_ip.dtype)
       for i in range(nbands):
           for j in range(nbands):
               fci_tot_density += fci_rdm1_total[i, j] * psi_r[i].conj() * psi_r[j]
       fci_tot_density = (fci_tot_density / (
           wfc_obj.cell_volume / np.prod(wfc_obj.fft_grid) / 2.0
       )).real

Run Bader analysis on the FCI density exactly as for the KS density:

.. code-block:: python

       cube.make_cube(base_folder, prefix, fci_tot_density, save_dir,
                      path_to_bader_executable, max_min)
       fci_bader = cube.extract_charge(atoms,
                                        os.path.join(save_dir, "ACF.dat"), valence)

VQE Bader charges
------------------

The VQE 1-RDM is built from ``vqe_ci_vec``, which was already computed and saved above.
The density reconstruction and Bader analysis are then identical to the FCI case:

.. code-block:: python

   if h_ks.tcc_vqe_result is not None:
       dim_spin = int(np.sqrt(vqe_ci_vec.size))
       vqe_rdm1 = h_ks.fci_solver.make_rdm1(
           vqe_ci_vec.reshape((dim_spin,) * 2), h_ks.norb, (h_ks.nelec, h_ks.nelec)
       )

       passive_filled = round((wfc_obj.nelec - active_electrons) / 2)
       vqe_rdm1_total = np.zeros((nbands, nbands))
       for i in range(passive_filled):
           vqe_rdm1_total[i, i] = 1.0
       vqe_rdm1_total[
           passive_filled : passive_filled + h_ks.norb,
           passive_filled : passive_filled + h_ks.norb,
       ] = vqe_rdm1 / 2.0

       vqe_tot_density = np.zeros(max_min, dtype=c_ip.dtype)
       for i in range(nbands):
           for j in range(nbands):
               vqe_tot_density += vqe_rdm1_total[i, j] * psi_r[i].conj() * psi_r[j]
       vqe_tot_density = (vqe_tot_density / (
           wfc_obj.cell_volume / np.prod(wfc_obj.fft_grid) / 2.0
       )).real

       cube.make_cube(base_folder, prefix, vqe_tot_density, save_dir,
                      path_to_bader_executable, max_min)
       vqe_bader = cube.extract_charge(atoms,
                                        os.path.join(save_dir, "ACF.dat"), valence)

Comparing results
------------------

Collect all Bader charges into a ``pandas`` DataFrame for a side-by-side comparison:

.. code-block:: python

   merged = pd.DataFrame({
       "ELEMENT":             atoms,
       "Bader charge QE":     qe_bader["EFFECTIVE CHARGE"].values,
       "Bader charge KS":     ks_bader["EFFECTIVE CHARGE"].values,
       "Bader charge CASCI":  fci_bader["EFFECTIVE CHARGE"].values,
       "Bader charge VQE":    vqe_bader["EFFECTIVE CHARGE"].values,
   })
   print(merged)

Differences between the QE and KS columns indicate numerical differences between the
``pp.x`` density grid and the plane-wave grid used internally by Dopyqo. Differences
between the KS and CASCI/VQE columns reflect genuine many-body corrections to the
single-particle picture.
