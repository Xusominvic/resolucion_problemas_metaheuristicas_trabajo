import matplotlib.pyplot as plt

# Configuramos el texto para que use LaTeX
plt.rc('text', usetex=False) # No necesitas instalar TeX en tu sistema, Matplotlib lo emula
plt.rc('font', family='serif')

fig, ax = plt.subplots(figsize=(10, 6))

# El contenido del algoritmo
algoritmo = r"""
$\mathbf{Algoritmo\ 1:\ Construcción\ de\ Solución\ Inicial\ (GRASP)}$

$\mathbf{Procedimiento:}\ \mathit{construct\_grasp\_solution}$
$\mathbf{Entradas:}\ \text{Instancia } \mathcal{I}, \text{ parámetro } \alpha \in [0, 1].$
$\mathbf{Salida:}\ \text{Secuencia } S.$

$\mathbf{Inicio}$
   Sea $C$ el conjunto de tareas pendientes $\{t_1, t_2, \dots, t_n\}$;
   Inicializar secuencia vacía $S = \emptyset$;
   $\mathbf{Mientras}\ C \neq \emptyset\ \mathbf{hacer:}$
      Para cada $t \in C$, calcular tiempo de finalización $f(t)$;
      Determinar límites: $c_{min} = \min_{t \in C} f(t)$ y $c_{max} = \max_{t \in C} f(t)$;
      Definir umbral: $Threshold = c_{min} + \alpha \cdot (c_{max} - c_{min})$;
      Construir $RCL = \{t \in C \mid f(t) \leq Threshold\}$;
      Seleccionar aleatoriamente $t^* \in RCL$;
      Actualizar $S \leftarrow S \cup \{t^*\}$ y $C \leftarrow C \setminus \{t^*\}$;
   $\mathbf{Fin\ Mientras}$
   $\mathbf{Retornar}\ S$;
$\mathbf{Fin}$
"""

# Dibujar el texto
ax.text(0.05, 0.95, algoritmo, fontsize=14, va='top', ha='left', linespacing=1.8)

# Limpiar el gráfico para que solo se vea el texto
ax.axis('off')

plt.show()