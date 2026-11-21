import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gamma, nbinom
from pytwalk import pytwalk
from scipy.integrate import odeint

np.random.seed(123)
plt.ion()



# ===========================
# Modelo 
# ===========================
def disease_model(y, t, params):
    S_h, V_h, E_h, I_h, R_h, S_r, I_r = y
    beta_1, beta_2, beta_3, epsilon, alpha_h, omega, xi = params

    lambda_h = (beta_1 * I_h + beta_2 * I_r) / N_h
    lambda_r = (beta_3 * I_r) / N_r

    dS_h = phi_h - lambda_h * S_h - (mu_h + alpha_h) * S_h + xi * V_h
    dV_h = alpha_h * S_h - omega * lambda_h * V_h - (mu_h + xi) * V_h
    dE_h = lambda_h * S_h + omega * lambda_h * V_h - (epsilon + mu_h) * E_h
    dI_h = epsilon * E_h - (mu_h + rho_h + delta_h) * I_h
    dR_h = rho_h * I_h - mu_h * R_h
    dS_r = phi_r - lambda_r * S_r - mu_r * S_r
    dI_r = lambda_r * S_r - (mu_r + delta_r) * I_r

    return [dS_h, dV_h, dE_h, dI_h, dR_h, dS_r, dI_r]

# ===========================
# Resolver el modelo ODE
# ===========================

def solve_disease_model(t_data, model_params):
    # condiciones iniciales 
    y0 = [10000., 1000., 100., 50., 0., 1000., 10.]
    sol = odeint(disease_model, y0, t_data, args=(model_params,))
    return sol

# ===========================
# Usar datos simulados o reales
# ===========================
USAR_DATOS_SIMULADOS = True # Cambia a False para usar datos reales

# ===========================
# Cargar y preparar los datos
# ===========================
df = pd.read_csv('C:/Users/jessi/Downloads/mpox-daily-confirmed-cases.csv',
                 on_bad_lines='skip')

# ===========================
# Preparar datos observados (reales o simulados)
# ===========================
if not USAR_DATOS_SIMULADOS:
    paises = df['Entity'].unique()
    print("\nPaíses (Entidades) en el conjunto de datos:")
    for pais in paises:
        print(pais)

    df_select = df[df['Entity'] == 'Democratic Republic of Congo'].copy()
    df_select['Day'] = pd.to_datetime(df_select['Day'])
    df_select['Daily cases smoothed'] = df_select['Daily cases'].rolling(window=7, min_periods=1).mean()
    df_select_clean = df_select.dropna(subset=['Daily cases smoothed']).copy()
    df_select_clean['Daily cases smoothed'] = (
        df_select_clean['Daily cases smoothed'].round().astype(int)
    )
    observed_data = df_select_clean['Daily cases smoothed'].values
    t_data = np.arange(len(observed_data))
else:
    # ===========================
    # Simular datos con el modelo y agregar ruido binomial negativo
    # ===========================
    print("\nSimulando datos con el modelo...")
    # Parámetros "verdaderos" para simulación (ajusta aquí)
    # --- NUEVOS PARÁMETROS PARA OTRA CURVA DE INCIDENCIA ---
    true_beta_1   = 0.01     # Tasa de transmisión humano-humano
    true_beta_2   = 0.02     # Tasa de transmisión animal-humano
    true_beta_3   = 0.08     # Tasa de transmisión animal-animal
    true_epsilon  = 0.03     # Progresión expuesto-infectado 
    true_alpha_h  = 20.0     # Vacunación humana 
    true_omega    = 0.3      # Eficacia vacuna 
    true_xi       = 10.0     # Pérdida de inmunidad
    true_r        = 1000.0  # Dispersión NB (ruido muy bajo)
    n_dias        = 200      # Días simulados

    # Vector de parámetros para el modelo
    true_params = [true_beta_1, true_beta_2, true_beta_3, true_epsilon, true_alpha_h, true_omega, true_xi]

    t_data = np.arange(n_dias)
    # Simular trayectoria
    sol_true = odeint(disease_model, [10000., 0., 1000., 20., 0., 1000., 10.], t_data, args=(true_params,))
    E_h_true = sol_true[:, 2]
    incidencia_true = true_epsilon * E_h_true
    # Evitar valores negativos o cero
    incidencia_true = np.maximum(incidencia_true, 1e-8)
    # Generar datos observados con error binomial negativo
    np.random.seed(123)
    p_nb = true_r / (true_r + incidencia_true)
    observed_data = nbinom.rvs(true_r, p_nb)
    print("Datos simulados binomial negativo generados. Tamaño:", observed_data.shape)
# ===========================
# Graficar datos observados (reales o simulados)
# ===========================
plt.figure(figsize=(12, 6))
if not USAR_DATOS_SIMULADOS:
    plt.plot(df_select['Day'], df_select['Daily cases'], color='blue')
    plt.xlabel('Fecha')
    plt.ylabel('Casos diarios')
    plt.title('Casos de mpox diarios en la República Democrática del Congo')
else:
    plt.scatter(t_data, observed_data, color='blue', label='Simulados (BN)')
    # Graficar la curva verdadera (sin error)
    plt.plot(t_data, incidencia_true, color='orange', linestyle='--', linewidth=2, label='Curva sin error')
    plt.xlabel('Día')
    plt.ylabel('Casos diarios simulados')
    plt.title('Casos simulados de mpox (con y sin error NB)')
    plt.legend()
    plt.show()
plt.grid(True)

# ===========================
# Parámetros del modelo (constantes)
# ===========================

N_h = 1_000_000
N_r = 10_000

phi_h = 50.0
phi_r = 1.37

mu_h = 0.000039
mu_r = 0.00137

delta_h = 0.001022
delta_r = 0.1

rho_h = 0.046538

# ===========================
# Priors (Gamma para todos los parámetros, incluido r)
# ===========================
alpha_prior = 2.0
beta_prior = 0.1

def gamma_logprior(x):
    if x <= 0:
        return -np.inf
    return gamma.logpdf(x, a=alpha_prior, scale=1.0/beta_prior)

# ===========================
# Graficar la distribución a priori (gamma)
# ===========================
plt.figure(figsize=(6, 4))
x = np.linspace(0, 500, 300)
y = gamma.pdf(x, a=2, scale=10)
plt.plot(x, y, label=f'Gamma({alpha_prior}, {beta_prior})')
plt.title('Prior')
plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# ===========================
# Verosimilitud (incidencia: epsilon * E_h)
# ===========================
def log_likelihood(params_vector, t_data, observed_data):
    try:
        # últimos = dispersión r
        model_params = params_vector[:-1]        # primeros 7 -> ODE
        r_disp = params_vector[-1]               # dispersión NB (último)

        # comprobación simple
        if r_disp <= 0 or np.any(np.array(model_params) <= 0):
            return -np.inf

        sol = solve_disease_model(t_data, model_params)

        # === INCIDENCIA: epsilon * E_h ===
        E_h = sol[:, 2]              # E_h
        epsilon = model_params[3]    # epsilon es el 4to parámetro (index 3)
        model_mean = epsilon * E_h   # incidencia esperada por día

        # evitar valores negativos o exactamente cero (numéricos)
        eps = 1e-8
        model_mean = np.maximum(model_mean, eps)

        # NB: p = r/(r+mean)
        p = r_disp / (r_disp + model_mean)
        p = np.clip(p, 1e-10, 1 - 1e-10)

        k = observed_data.astype(int)

        # Si hay longitudes distintas, recortar o verificar
        if len(k) != len(model_mean):
            
            m = min(len(k), len(model_mean))
            k = k[:m]
            model_mean = model_mean[:m]
            p = p[:m]

        log_pmf = nbinom.logpmf(k, r_disp, p)
        if np.any(np.isnan(log_pmf)):
            return -np.inf

        return np.sum(log_pmf)

    except Exception as e:
        
        return -np.inf


# ===========================
# Funciones para el t-walk
# ===========================
def disease_supp(params):
    # Soporte: todos los parámetros deben ser positivos. 
    return np.all(np.array(params) > 0)

def disease_potential_energy(params):
    # U = - log_likelihood - log_prior
    if not disease_supp(params):
        return np.inf

    # sumar log-priors para *todos* los parámetros (incluido r)
    log_prior_sum = 0.0
    for p in params:
        lp = gamma_logprior(p)
        if not np.isfinite(lp):
            return np.inf
        log_prior_sum += lp

    loglik = log_likelihood(params, t_data, observed_data)
    if not np.isfinite(loglik):
        return np.inf

    U = -loglik - log_prior_sum
    return U

# ===========================
# Iniciar MCMC (t-walk) estimando r también (n = 8)
# ===========================

# Mejor inicialización: cerca de los parámetros verdaderos si se usan datos simulados
if USAR_DATOS_SIMULADOS:
    
    base_params = np.array(true_params + [true_r])
    # Añadir ruido gaussiano pequeño (5% del valor)
    initial_params_chain1 = base_params * (1 + 0.05 * np.random.randn(8))
    initial_params_chain2 = base_params * (1 + 0.05 * np.random.randn(8))
    # asegurarse positivos con un floor pequeño:
    initial_params_chain1 = np.maximum(initial_params_chain1, 1e-8)
    initial_params_chain2 = np.maximum(initial_params_chain2, 1e-8)
else:
    initial_params_chain1 = np.array([
        0.01,     # Tasa de transmisión humano-humano
        0.02,     # Tasa de transmisión animal-humano
        0.08,     # Tasa de transmisión animal-animal
        0.03,     # Progresión expuesto-infectado 
        20.0,     # Vacunación humana 
        0.3,      # Eficacia vacuna 
        10.0,     # Pérdida de inmunidad 
        1000.0  # Dispersión NB 
    ])
    initial_params_chain2 = initial_params_chain1 * (1 + 0.1 * np.random.randn(8))
    initial_params_chain2 = np.abs(initial_params_chain2)

Enfermedad = pytwalk(
    n=8,
    U=disease_potential_energy,
    Supp=disease_supp
)

Enfermedad.par_names = [r"$\beta_1$", r"$\beta_2$", r"$\beta_3$", r"$\epsilon$",
                        r"$\alpha_h$", r"$\omega$", r"$\xi$", r"$r$"]

# Ejecutar 
Enfermedad.Run(T=500_000, x0=initial_params_chain1, xp0=initial_params_chain2)

posterior_samples = np.array(Enfermedad.Output)
print("Shape posterior samples:", posterior_samples.shape)

# ===========================
# Resumen posterior y ajuste del modelo
# ===========================
n_params = posterior_samples.shape[1]
burn_in = int(0.3 * posterior_samples.shape[0])  # descartar 30% inicial
samples_post_burn = posterior_samples[burn_in:, :]


# ==========================================
# Graficar múltiples curvas del posterior (incidencia eps * E_h) y MAP
# ==========================================

# Encontrar los parámetros con la máxima probabilidad posterior (mínima energía)
energias = [disease_potential_energy(params) for params in samples_post_burn]
indice_map = np.argmin(energias)
parametros_map = samples_post_burn[indice_map]

print("Parámetros MAP encontrados:")
for i, nombre in enumerate(Enfermedad.par_names):
    print(f"{nombre}: {parametros_map[i]:.6f}")

# Resolver el modelo con parámetros MAP
sol_map = solve_disease_model(t_data, parametros_map[:-2])

# Calcular incidencia esperada con MAP
E_h_map = sol_map[:, 2]
epsilon_map =parametros_map[:-2][3]
incidencia_map = epsilon_map * E_h_map




num_curves = 50
n_available = samples_post_burn.shape[0]
num_curves = min(num_curves, n_available)

idx = np.random.choice(n_available, num_curves, replace=False)

plt.figure(figsize=(12, 6))
plt.plot(t_data, observed_data, 'o', label='Observados', color='blue')

for i in idx:
    params_i = samples_post_burn[i, :-2]   # parámetros del modelo (todos menos r)
    sol_i = solve_disease_model(t_data, params_i)
    E_h_i = sol_i[:, 2]
    epsilon_i = params_i[3]
    inc_i = epsilon_i * E_h_i
    plt.plot(t_data[:len(inc_i)], inc_i, color='gray', alpha=0.3)
    
plt.plot(t_data, incidencia_map, 'r-', linewidth=2, label='Ajuste MAP')
plt.xlabel('Tiempo (días)')
plt.ylabel('Casos (incidencia)')
plt.title('Trayectorias de incidencia (ε · E_h)')
plt.legend()
plt.grid(True)


# Trazas de los parámetros (mostramos todos)
n_plots = n_params
fig, axes = plt.subplots(4, 2, figsize=(12, 10))
axes = axes.flatten()
for i in range(n_params-1):
    axes[i].plot(samples_post_burn[:, i])
    axes[i].set_title(Enfermedad.par_names[i])
    print(i)
plt.tight_layout()

#los parametros MAP son
print('(beta1, beta2, beta3, epsilon, alpha_h, omega, xi) = ', parametros_map[:-2])




#ahora imprimiremos los histogramas de los parametros 

fig, axes = plt.subplots(4, 2, figsize=(12, 10))   
axes = axes.flatten()
for i in range(n_params-1):
    data = samples_post_burn[:, i]
    axes[i].hist(data, bins=30, density=True, alpha=0.7, label='Histograma')
    mean_val = np.mean(data)
    median_val = np.median(data)
    axes[i].axvline(mean_val, color='red', linestyle='--', linewidth=2, label='Media')
    axes[i].axvline(median_val, color='green', linestyle='-.', linewidth=2, label='Mediana')
    axes[i].set_title(f'Histograma: {Enfermedad.par_names[i]}')
    axes[i].legend()
plt.tight_layout()


# ===========================
# Autocorrelación para cada parámetro
# ===========================

from statsmodels.tsa.stattools import acf

plt.figure(figsize=(15, 10))

for i in range(len(Enfermedad.par_names)):
    plt.subplot(4, 2, i+1)
    
    # Calcular autocorrelación
    autocorr = acf(samples_post_burn[:, i], nlags=50)
    
    plt.stem(autocorr, basefmt=" ")
    plt.axhline(y=0, color='k', linestyle='-')
    plt.axhline(y=0.1, color='r', linestyle='--', alpha=0.7, label='Umbral 0.1')
    plt.axhline(y=-0.1, color='r', linestyle='--', alpha=0.7)
    plt.title(f'Autocorrelación: {Enfermedad.par_names[i]}')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelación')
    if i == 0:
        plt.legend()
plt.tight_layout()


# ===========================
# Thinning manual
# ===========================

# Define aquí el intervalo de thinning manualmente
thinning_interval = 50  # <--- Cambia este valor según lo que desees

samples_thinned = samples_post_burn[::thinning_interval]
print(f"Muestras originales: {len(samples_post_burn)}")
print(f"Muestras después de thinning (intervalo={thinning_interval}): {len(samples_thinned)}")

plt.figure(figsize=(15, 10))
for i in range(len(Enfermedad.par_names)):
    plt.subplot(4, 2, i+1)
    
    # Calcular autocorrelación
    autocorr = acf(samples_thinned[:, i], nlags=50)
    
    plt.stem(autocorr, basefmt=" ")
    plt.axhline(y=0, color='k', linestyle='-')
    plt.axhline(y=0.1, color='r', linestyle='--', alpha=0.7, label='Umbral 0.1')
    plt.axhline(y=-0.1, color='r', linestyle='--', alpha=0.7)
    plt.title(f'Autocorrelación: {Enfermedad.par_names[i]}')
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelación')
    if i == 0:
        plt.legend()

plt.tight_layout()

# ===========================
# Verificar series después del thinning
# ===========================

plt.figure(figsize=(15, 10))

for i in range(len(Enfermedad.par_names)):
    plt.subplot(4, 2, i+1)
    plt.plot(samples_thinned[:, i], alpha=0.7)
    plt.title(f'Serie después de thinning: {Enfermedad.par_names[i]}')
    plt.xlabel('Iteración (thinned)')
    plt.ylabel('Valor del parámetro')
    plt.grid(True, alpha=0.3)
plt.tight_layout()



