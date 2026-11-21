# Compartmental Mathematical Model for Mpox Transmission Dynamics

**Author:** Jessica Rubí Lara Rosales  
**Contact:** [jessica.lara@cimat.mx](mailto:jessica.lara@cimat.mx)  
**Institution:** Center for Research in Mathematics (CIMAT)  
**Course:** Epidemiological Modeling  
**Instructor:** Dra. L. Leticia Ramírez Ramírez

---

## Project Overview

This repository contains a project developed for the **Epidemiological Modeling** course at CIMAT, presenting a compartmental mathematical model to analyze the transmission dynamics of **Mpox** (*Monkeypox virus*) and its calibration to real-world data. Building upon the coupled human–rodent framework introduced by **Qian et al. (2025)**—which combines an SVEIR structure for humans with an SI structure for rodent reservoirs—this work extends the model by incorporating the **loss of vaccine-induced immunity**.

## Objectives & Methodology

- **Epidemiological Modeling:** Formulating a coupled system of nonlinear ordinary differential equations (ODEs) that captures human-to-human and zoonotic (rodent-to-human) transmission, demographic vital dynamics, and the loss of vaccine-induced immunity.
- **Parameter Estimation & Real-Data Fitting:** Fixing baseline demographic and clinical parameters from WHO guidelines and literature, while estimating the key transmission and disease progression parameters using **Markov Chain Monte Carlo (MCMC)** against smoothed 7-day moving average incidence data from [Our World in Data](https://ourworldindata.org/mpox).
- **Numerical Simulation & Analysis:** Simulating the calibrated ODE system to compare model trajectories with observed case trends and interpret the estimated epidemiological parameters.

## Repository Contents

- **`Proyecto_Final_MEpi.pdf`:** Technical report covering the epidemiological background, ODE formulation, parameter calibration, and real-data fitting results.
- **`simulacion_numerica.py`:** Python scripts implementing the numerical integration of the ODE system, parameter fitting, and visualizations.
- **`presen_MEpi.pdf`:** Slides summarizing the model assumptions, calibration workflow, and main findings.

## References

1. Qian, et al. (2025). *(Base SVEIR–SI compartmental model for Mpox — complete bibliographic details from report).*
2. Yaga. (2025). *(Mpox clades, smallpox vaccine cross-immunity, and waning immunity models — complete bibliographic details from report).*
3. Frank. (2024). *(Vector-borne compartmental models without vaccination — complete bibliographic details from report).*
4. Tamakloe, et al. (2025). *(Time-series clustering and $R_0$ estimation for Mpox — complete bibliographic details from report).*
5. Mathieu, E., Spooner, F., Dattani, S., Ritchie, H., & Roser, M. *Mpox (monkeypox)*. Our World in Data. Available at: [https://ourworldindata.org/mpox](https://ourworldindata.org/mpox).
