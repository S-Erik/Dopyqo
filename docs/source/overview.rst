Overview
========

Dopyqo performs many-body post-processing of Kohn-Sham density functional theory (DFT)
calculations. Starting from a `Quantum ESPRESSO <https://www.quantum-espresso.org/>`_
plane-wave DFT result, it constructs a second-quantized many-body Hamiltonian and solves
it with classical (FCI) or quantum (VQE) algorithms, then computes improved Bader charges
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
   Many-body Hamiltonian (ERIs, kinetic, Ewald, pseudopotential)
          │
          ├──► FCI (PySCF)   ──► ground-state energy & density
          └──► VQE (TenCirChem / Qiskit) ──► ground-state energy & density
                                                    │
                                                    ▼
                                           Bader charge analysis


Many-body Hamiltonian
---------------------

The electronic Hamiltonian in second quantization is (see :ref:`citation`):

.. math::

   \hat{H} = \sum_{tu} h_{tu}\, a_t^\dagger a_u
           + \frac{1}{2} \sum_{tuvw} h_{tuvw}\, a_t^\dagger a_u^\dagger a_v a_w
           + E_{n\text{-}n} + E_{e\text{-}self}

where :math:`a_t^\dagger` and :math:`a_t` are fermionic creation and annihilation operators
for spin-orbital :math:`t`, :math:`E_{n\text{-}n}` is the nuclear repulsion (Ewald) energy,
and :math:`E_{e\text{-}self}` is the pseudopotential self-energy.

Electron Repulsion Integrals
----------------------------

The two-electron integrals are computed efficiently in reciprocal space via pair densities:

.. math::

   h_{tuvw} = \frac{4\pi}{V} \sum_{\mathbf{G} \neq 0}
              \frac{\tilde{\rho}^*_{wt}(\mathbf{G})\,\tilde{\rho}_{uv}(\mathbf{G})}{G^2}

where :math:`V` is the unit-cell volume, :math:`\mathbf{G}` are reciprocal-lattice vectors,
and :math:`\tilde{\rho}_{tu}(\mathbf{G}) = \sum_{\mathbf{p}} c^*_{t,\mathbf{p}+\mathbf{G}}\, c_{u,\mathbf{p}}`
is the Fourier transform of the pair density constructed from plane-wave coefficients
:math:`c_{t,\mathbf{p}}`.

Only the :math:`\mathbf{G} = 0` term (the macroscopic Hartree contribution) is omitted, as
it cancels with the compensating background charge in a periodic system.

Bader Charge Analysis
---------------------

After obtaining the many-body ground-state charge density
:math:`\rho(\mathbf{r})`, atoms are assigned charges by integrating over their Bader
basins :math:`\mathcal{B}_I`:

.. math::

   Q_I = \int_{\mathcal{B}_I} \rho(\mathbf{r})\, d^3r

Each basin :math:`\mathcal{B}_I` is bounded by zero-flux surfaces where
:math:`\nabla\rho(\mathbf{r}) \cdot \hat{n} = 0`. The external
`Bader charge analysis code <https://theory.cm.utexas.edu/henkelman/code/bader/>`_ is used
to determine the basin boundaries.

Active Space
------------

Because the full many-body problem scales exponentially with system size, Dopyqo uses an
*active space* approach: only :math:`N_e` electrons in :math:`N_o` orbitals are treated
at the many-body level. Orbitals outside the active space are either frozen (occupied) or
discarded (virtual). The frozen-core contribution to the one-body matrix elements and the
constant energy offset are computed analytically.

The active-space parameters are set via :attr:`~dopyqo.DopyqoConfig.active_electrons`
and :attr:`~dopyqo.DopyqoConfig.active_orbitals` in :class:`~dopyqo.DopyqoConfig`.
