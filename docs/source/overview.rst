Overview
========

Dopyqo performs many-body post-processing of Kohn-Sham density functional theory (DFT)
calculations. Starting from a `Quantum ESPRESSO <https://www.quantum-espresso.org/>`_
plane-wave DFT result, it constructs a second-quantized many-body Hamiltonian and solves
it with classical (FCI) or quantum (VQE) algorithms, and then can compute Bader charges
from the resulting many-body charge density.

Workflow
--------

.. code-block:: text

   Quantum ESPRESSO (DFT)
          │
          │  wfc.dat / wfc.hdf5
          │  data-file-schema.xml
          ▼
   Kohn-Sham orbitals & crystal structure
          │
          │  active space selection
          ▼
   Many-body Hamiltonian (matrix elements and constant energies)
          │
          ├──► FCI (PySCF)   ──► ground-state energy & density
          └──► VQE (TenCirChem / Qiskit) ──► ground-state energy & density
                                                    │
                                                    ▼
                                           Bader charge analysis


Many-body Hamiltonian
---------------------

The electronic Hamiltonian in second quantization is (see our `paper <https://arxiv.org/abs/2510.12887>`_):

.. math::

   \hat{H} = \sum_{tu} h_{tu}\, a_t^\dagger a_u
           + \frac{1}{2} \sum_{tuvw} h_{tuvw}\, a_t^\dagger a_u^\dagger a_v a_w
           + E_{\text{n-n}} + E_{\text{e-self}}

where :math:`a_t^\dagger` and :math:`a_t` are fermionic creation and annihilation operators
for spin-orbital :math:`t`, :math:`E_{\text{n-n}}` is the nuclear repulsion (Ewald) energy,
and :math:`E_{\text{e-self}}` is the electron self-interaction energy.

Electron Repulsion Integrals
----------------------------

The two-electron integrals are computed efficiently in reciprocal space via pair densities:

.. math::

   h_{tuvw} = \frac{4\pi}{V} \sum_{\mathbf{G} \neq 0}
              \frac{\tilde{\rho}^*_{wt}(\mathbf{G})\,\tilde{\rho}_{uv}(\mathbf{G})}{G^2}

where :math:`V` is the unit-cell volume, :math:`\mathbf{G}` are reciprocal-lattice vectors,
and :math:`\tilde{\rho}_{tu}(\mathbf{G})`
is the Fourier transform of the real-space pair density :math:`\rho_{tu}(\mathbf{r})=\psi^\ast_t(\mathbf{r}) \psi_u(\mathbf{r})`, where :math:`\psi_t(\mathbf{r})` is the real-space representation of the :math:`t`-th Kohn-Sham orbital.

The :math:`\mathbf{G} = 0` term is omitted, as it cancels with the compensating background charge in a periodic system.

Bader Charge Analysis
---------------------

After obtaining the many-body ground-state charge density
:math:`\rho(\mathbf{r})`, atoms are assigned charges by integrating over their Bader
regions :math:`\mathcal{B}_I`:

.. math::

   Q_I = \int_{\mathcal{B}_I} \rho(\mathbf{r})\, d^3r

Each region :math:`\mathcal{B}_I` is bounded by zero-flux surfaces running through minima of the charge density. The external `Bader charge analysis code <https://theory.cm.utexas.edu/henkelman/code/bader/>`_ is used
to determine the region boundaries.

Active Space
------------

Because exactly solving the many-body Hamiltonian with classical algorithms scales exponentially with system size, Dopyqo uses an
*active space* approach: only :math:`N_e` electrons in :math:`N_o` orbitals are treated
at the many-body level. Orbitals outside the active space are either frozen (occupied) or
discarded (virtual). The frozen orbitals are treated on a mean-field level using the frozen-core approximation.

The active-space parameters are set via :attr:`~dopyqo.DopyqoConfig.active_electrons`
and :attr:`~dopyqo.DopyqoConfig.active_orbitals` in :class:`~dopyqo.DopyqoConfig`.

