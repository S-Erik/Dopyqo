import os
import numpy as np
import dopyqo
import warnings
import pandas as pd
from dopyqo.colors import *
from dopyqo import cube


if __name__ == "__main__":
    # Run QE SCF calculation and QE pp calculation beforehand
    # using the input files Mg2Si.scf.in and Mg2Si.pp.in

    base_folder = os.path.join("qe_files", "Mg2Si")
    prefix = "Mg2Si"
    active_electrons = 6
    active_orbitals = 5
    path_to_bader_executable = {"bader": os.path.join(os.path.expanduser("~"), "bader/bader")}

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

    atoms = [element["element"] for element in wfc_obj.atoms]
    valence = {x.element: x.z_valence for x in wfc_obj.pseudopots}

    overlaps = wfc_obj.get_overlaps()
    if not np.allclose(overlaps, np.eye(overlaps.shape[0])):
        warnings.warn("The wavefunctions are not orthonormal!")

    c_ip = wfc_obj.evc        # shape (#bands, #waves)
    mill = wfc_obj.mill       # Miller indices, shape (#waves, 3)
    nbands = wfc_obj.nbnd
    max_min = wfc_obj.fft_grid
    ks_total_electrons = wfc_obj.nelec

    ########################################################
    #         Saving FCI/VQE state data for reuse          #
    ########################################################
    npz_path = os.path.join(base_folder, f"statevecs_{active_electrons}e_{active_orbitals}o.npz")
    save_data = {"norb": h_ks.norb, "nelec": h_ks.nelec}
    if len(h_ks.fci_evcs) > 0:
        save_data["fci_evcs"] = h_ks.fci_evcs[0]
    vqe_ci_vec = None
    if h_ks.tcc_vqe_result is not None:
        vqe_ci_vec = h_ks.tcc_ansatz.civector(h_ks.tcc_vqe_params)
        save_data["vqe_ci_vec"] = vqe_ci_vec
        save_data["vqe_params"] = h_ks.tcc_vqe_params
    np.savez(npz_path, **save_data)

    ########################################################
    #           Calculating real-space densities           #
    ########################################################
    c_ip_array = np.zeros((nbands, *max_min), dtype=c_ip.dtype)
    for idx, (x, y, z) in enumerate(mill):
        c_ip_array[:, x + max_min[0] // 2, y + max_min[1] // 2, z + max_min[2] // 2] = c_ip[:, idx]

    psi_r = np.array([
        np.fft.ifftn(np.fft.ifftshift(c_ip_array[i])) * np.sqrt(np.prod(max_min))
        for i in range(nbands)
    ])

    ks_single_density = np.abs(psi_r) ** 2
    ks_tot_density = cube.get_density_cube(ks_single_density, wfc_obj.occupations_xml)
    ks_tot_density = ks_tot_density / (wfc_obj.cell_volume / np.prod(wfc_obj.fft_grid) / 2.0)

    save_dir = os.path.join(base_folder, "Bader_dopyqo")
    cube.make_cube(base_folder, prefix, ks_tot_density, save_dir, path_to_bader_executable, max_min)
    ks_bader = cube.extract_charge(atoms, os.path.join(save_dir, "ACF.dat"), valence)

    ppx_dir = os.path.join(base_folder, "Bader_QE")
    ppx_file = os.path.join(base_folder, f"{prefix}_pp.cube")
    cube.run_ppx(ppx_file, path_to_bader_executable, ppx_dir, prefix)
    qe_bader = cube.extract_charge(atoms, os.path.join(ppx_dir, "ACF.dat"), valence)

    merged = pd.DataFrame(
        {
            "ELEMENT": atoms,
            "Bader charge QE": qe_bader["EFFECTIVE CHARGE"].values,
            "Bader charge Dopyqo": ks_bader["EFFECTIVE CHARGE"].values,
        }
    )

    if len(h_ks.fci_evcs) > 0:
        fci_rdm1 = h_ks.fci_solver.make_rdm1(h_ks.fci_evcs[0], h_ks.norb, (h_ks.nelec, h_ks.nelec))
        passive_filled = round((ks_total_electrons - active_electrons) / 2)
        fci_rdm1_total = np.zeros((nbands, nbands))
        for i in range(passive_filled):
            fci_rdm1_total[i, i] = 1.0
        fci_rdm1_total[
            passive_filled : passive_filled + h_ks.norb,
            passive_filled : passive_filled + h_ks.norb,
        ] = fci_rdm1 / 2.0
        fci_tot_density = np.zeros(max_min, dtype=c_ip.dtype)
        for i in range(nbands):
            for j in range(nbands):
                # ρ(r) = Σ_ij γ_ij ϕ*_i(r) ϕ_j(r)
                fci_tot_density += fci_rdm1_total[i, j] * psi_r[i].conj() * psi_r[j]
        fci_tot_density = (fci_tot_density / (wfc_obj.cell_volume / np.prod(wfc_obj.fft_grid) / 2.0)).real

        cube.make_cube(base_folder, prefix, fci_tot_density, save_dir, path_to_bader_executable, max_min)
        fci_bader = cube.extract_charge(atoms, os.path.join(save_dir, "ACF.dat"), valence)
        merged = pd.concat(
            [merged, pd.DataFrame({"Bader charge Dopyqo CASCI": fci_bader["EFFECTIVE CHARGE"].values})],
            axis=1,
        )

    if h_ks.tcc_vqe_result is not None:
        dim_spin = int(np.sqrt(vqe_ci_vec.size))
        vqe_rdm1 = h_ks.fci_solver.make_rdm1(
            vqe_ci_vec.reshape((dim_spin,) * 2), h_ks.norb, (h_ks.nelec, h_ks.nelec)
        )
        passive_filled = round((ks_total_electrons - active_electrons) / 2)
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
                # ρ(r) = Σ_ij γ_ij ϕ*_i(r) ϕ_j(r)
                vqe_tot_density += vqe_rdm1_total[i, j] * psi_r[i].conj() * psi_r[j]
        vqe_tot_density = (vqe_tot_density / (wfc_obj.cell_volume / np.prod(wfc_obj.fft_grid) / 2.0)).real

        cube.make_cube(base_folder, prefix, vqe_tot_density, save_dir, path_to_bader_executable, max_min)
        vqe_bader = cube.extract_charge(atoms, os.path.join(save_dir, "ACF.dat"), valence)
        merged = pd.concat(
            [merged, pd.DataFrame({"Bader charge Dopyqo VQE": vqe_bader["EFFECTIVE CHARGE"].values})],
            axis=1,
        )

    print(f"{GREEN}Bader charge results:{RESET_COLOR}")
    print(merged)
