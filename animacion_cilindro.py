import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit as st
import time # Importado pero no usado directamente en el flujo principal

# --- Configuración de la Página de Streamlit ---
st.set_page_config(layout="wide", page_title="Simulador de Cilindro Rotando")
st.title("Simulador de Cilindro Rotando con Cuerda")
st.write("Ajusta los parámetros para ver cómo cambian la rotación y el desenrollado de la cuerda.")

# --- Creamos las dos columnas ---
col1, col2 = st.columns([1, 2])

# --- Columna Izquierda: Parámetros ajustables (sliders) ---
with col1:
    st.header("Parámetros del Cilindro")
    masa = st.slider("Masa del Cilindro (kg)", 1.0, 100.0, 50.0, 0.5)
    radio = st.slider("Radio Externo del Cilindro (m)", 0.05, 1.0, 0.06, 0.01)

    tipo_solido = st.radio(
        "Tipo de Sólido:",
        ("Cilindro Sólido", "Cilindro Hueco", "Cilindro de Pared Delgada"),
        index=0
    )

    radio_interno = 0.0
    if tipo_solido == "Cilindro Hueco":
        max_inner_radio = radio - 0.01
        if max_inner_radio < 0.01:
            max_inner_radio = 0.01
        radio_interno = st.slider("Radio Interno del Cilindro (m)", 0.01, max_inner_radio, 0.03, 0.01)
        if radio_interno >= radio:
            st.warning("El radio interno debe ser menor que el radio externo. Ajusta el radio externo o interno.")
    elif tipo_solido == "Cilindro de Pared Delgada":
        st.info(f"Para un cilindro de pared delgada, el momento de inercia se calcula como $MR^2$, donde $R$ es el radio externo.")

    # Calcular Momento de Inercia (I) para todos los modos de cálculo
    if tipo_solido == "Cilindro Sólido":
        I = 0.5 * masa * radio**2
    elif tipo_solido == "Cilindro Hueco":
        I = 0.5 * masa * (radio**2 + radio_interno**2)
    else: # Cilindro de Pared Delgada
        I = masa * radio**2
    
    st.write(f"Momento de Inercia (I): **{I:.2f}** kg·m²")
    st.write("---")

    st.header("Modo de Entrada de la Simulación")
    modo_entrada = st.radio(
        "Selecciona cómo definir la simulación:",
        ("Fuerza y Distancia de Cable Desenrollado", "Torque Constante Aplicado"),
        index=0
    )

    if modo_entrada == "Fuerza y Distancia de Cable Desenrollado":
        st.subheader("Entrada por Trabajo y Energía")
        fuerza = st.slider("Fuerza Aplicada (N)", 1.0, 50.0, 9.0, 0.1)
        distancia_desenrollada = st.slider("Distancia de Cable Desenrollado (m)", 0.1, 5.0, 2.0, 0.1)

        # --- Cálculos Basados en Trabajo y Energía ---
        work = fuerza * distancia_desenrollada
        omega_final = np.sqrt((2 * work) / I) if I != 0 else 0
        theta_final = distancia_desenrollada / radio if radio != 0 else 0

        if theta_final > 0 and omega_final > 0:
            alpha = (omega_final**2) / (2 * theta_final)
        else:
            alpha = 0

        if alpha > 0:
            t_final = omega_final / alpha
        else:
            t_final = 0.0

        # Torque equivalente para la visualización
        torque_usado = I * alpha
        st.info(f"El torque equivalente que produce esta aceleración angular es: **{torque_usado:.2f}** N·m")

    else: # modo_entrada == "Torque Constante Aplicado"
        st.subheader("Entrada por Torque Constante")
        torque_usado = st.slider("Torque Constante Aplicado (N·m)", 0.1, 10.0, 0.54, 0.01)
        t_final = st.slider("Tiempo Total de Simulación (s)", 0.1, 10.0, 1.00, 0.01)
        
        # --- Cálculos Basados en Torque y Tiempo ---
        alpha = torque_usado / I if I != 0 else 0
        omega_final = alpha * t_final
        theta_final = 0.5 * alpha * t_final**2
        distancia_desenrollada = theta_final * radio # Aunque no se muestra, se calcula para la animación
        
        st.info(f"Se aplica un torque constante de **{torque_usado:.2f}** N·m durante **{t_final:.2f}** segundos.")


    # --- Resultados Comunes a Ambos Modos ---
    velocidad_lineal_final = omega_final * radio
    aceleracion_tangencial = alpha * radio
    
    # Cálculo de energías cinéticas al final del movimiento
    energia_cinetica_rotacional_final = 0.5 * I * omega_final**2
    # La energía cinética translacional aquí se refiere a la energía cinética del punto en la periferia (o del cable desenrollado).
    energia_cinetica_translacional_final = 0.5 * masa * velocidad_lineal_final**2 
    energia_cinetica_total_final = energia_cinetica_rotacional_final + energia_cinetica_translacional_final

    st.write("---")
    st.header("Resultados de la Simulación")
    st.write(f"Aceleración Angular (α): **{alpha:.2f}** rad/s²")
    st.write(f"Aceleración Tangencial (a_t): **{aceleracion_tangencial:.2f}** m/s²")
    st.write(f"**Velocidad Angular Final (ω_final):** **{omega_final:.2f}** rad/s")
    st.write(f"**Velocidad Lineal Final (v_final):** **{velocidad_lineal_final:.2f}** m/s")
    st.write(f"**Ángulo Girado (θ_final):** **{theta_final:.2f}** rad")
    st.write(f"**Energía Cinética Rotacional Final (E_kr):** **{energia_cinetica_rotacional_final:.2f}** J")
    st.write(f"**Energía Cinética Traslacional Final (E_kt):** **{energia_cinetica_translacional_final:.2f}** J")
    st.write(f"**Energía Cinética Total Final (E_total):** **{energia_cinetica_total_final:.2f}** J")


    fps_display = 30 # Velocidad fija para la animación


    st.write("---")
    st.header("Fórmulas Clave Utilizadas")
    st.markdown(
        """
        Las fórmulas se adaptan según el modo de entrada seleccionado:

        ### Momento de Inercia (I):
        * **Cilindro Sólido:** $I = \\frac{1}{2}MR^2$
        * **Cilindro Hueco:** $I = \\frac{1}{2}M(R^2 + r^2)$
        * **Cilindro de Pared Delgada:** $I = MR^2$

        ---

        ### Si se usa **Fuerza y Distancia de Cable Desenrollado**:
        * **Trabajo (W):** $W = F \\times d_{desenrollada}$
        * **Velocidad Angular Final ($\\omega_f$):** Derivada del Teorema de Trabajo y Energía: $\\omega_f = \\sqrt{\\frac{2 W}{I}}$ (asumiendo $\\omega_i = 0$)
        * **Desplazamiento Angular ($\\theta$):** $\\theta = \\frac{d_{desenrollada}}{R}$
        * **Aceleración Angular ($\\alpha$):** $\\alpha = \\frac{\\omega_f^2}{2\\theta}$ (derivado de cinemática rotacional)
        * **Tiempo Total de Simulación ($t_{final}$):** $t_{final} = \\frac{\\omega_f}{\\alpha}$

        ---

        ### Si se usa **Torque Constante Aplicado**:
        * **Aceleración Angular ($\\alpha$):** Se calcula directamente de la segunda ley de Newton para la rotación: $\\alpha = \\frac{\\tau}{I}$
        * **Velocidad Angular Final ($\\omega_f$):** $\\omega_f = \\alpha t_{final}$ (asumiendo $\\omega_i = 0$)
        * **Desplazamiento Angular ($\\theta$):** $\\theta = \\frac{1}{2}\\alpha t_{final}^2$
        * **Distancia de Cable Desenrollado ($d_{desenrollada}$):** $d_{desenrollada} = \\theta R$

        ---

        ### Fórmulas Comunes a Ambos Modos:
        * **Velocidad Lineal (v):** $v = \\omega R$
        * **Aceleración Tangencial (a_t):** $a_t = \\alpha R$
        * **Energía Cinética Rotacional (E_kr):** $E_{kr} = \\frac{1}{2}I\\omega^2$
        * **Energía Cinética Traslacional (E_kt):** $E_{kt} = \\frac{1}{2}mv^2$ (del punto en la periferia o del cable)
        * **Energía Cinética Total (E_total):** $E_{total} = E_{kr} + E_{kt}$
        """
    )


# --- Columna Derecha: Animación ---
with col2:
    st.header("Visualización de la Simulación")

    frames = int(t_final * fps_display) if t_final > 0 else 1 

    # --- Gráficas de Movimiento y Energía (Figuras separadas para manipulación) ---
    st.markdown("---")
    st.header("Gráficas de Movimiento y Energía")

    time_points = np.linspace(0, t_final, frames)
    
    omega_points = alpha * time_points
    v_lineal_points = omega_points * radio

    E_kr_points = 0.5 * I * omega_points**2
    E_kt_points = 0.5 * masa * v_lineal_points**2 
    E_total_points = E_kr_points + E_kt_points

    fig_plots, axs = plt.subplots(3, 1, figsize=(8, 12)) 

    axs[0].plot(time_points, omega_points, label='Velocidad Angular (ω)', color='blue')
    axs[0].set_title('Velocidad Angular vs. Tiempo')
    axs[0].set_xlabel('Tiempo (s)')
    axs[0].set_ylabel('Velocidad Angular (rad/s)')
    axs[0].grid(True)
    axs[0].legend()
    line_omega, = axs[0].plot([0, 0], axs[0].get_ylim(), 'k--', linewidth=1)

    axs[1].plot(time_points, v_lineal_points, label='Velocidad Lineal (v)', color='green')
    axs[1].set_title('Velocidad Lineal vs. Tiempo')
    axs[1].set_xlabel('Tiempo (s)')
    axs[1].set_ylabel('Velocidad Lineal (m/s)')
    axs[1].grid(True)
    axs[1].legend()
    line_v_lineal, = axs[1].plot([0, 0], axs[1].get_ylim(), 'k--', linewidth=1)

    # MODIFICACIÓN CLAVE AQUÍ: Eliminación de la sintaxis LaTeX en las etiquetas
    axs[2].plot(time_points, E_kr_points, label='Energía Cinética Rotacional (E_kr)', color='purple')
    axs[2].plot(time_points, E_kt_points, label='Energía Cinética Traslacional (E_kt)', color='brown', linestyle='--')
    axs[2].plot(time_points, E_total_points, label='Energía Cinética Total (E_total)', color='red', linewidth=2)
    axs[2].set_title('Energías Cinéticas vs. Tiempo')
    axs[2].set_xlabel('Tiempo (s)')
    axs[2].set_ylabel('Energía (J)')
    axs[2].grid(True)
    axs[2].legend()
    line_energy, = axs[2].plot([0, 0], axs[2].get_ylim(), 'k--', linewidth=1)

    # La línea plt.tight_layout() que causaba el error se mantiene, ya que el problema real era el texto.
    plt.tight_layout()

    # --- Función para obtener la animación ---
    def get_animation_with_timer(masa, radio, radio_interno, tipo_solido, alpha_anim, t_final_anim, fps_display_anim, 
                                 line_omega, line_v_lineal, line_energy): 
        
        frames_cached = int(t_final_anim * fps_display_anim) if t_final_anim > 0 else 1

        fig_cached, ax_cached = plt.subplots(figsize=(6,6))
        ax_cached.set_xlim(-0.6, 0.3)
        ax_cached.set_ylim(-0.3, 0.3)
        ax_cached.set_aspect('equal')
        ax_cached.axis('off')

        circle_cached = plt.Circle((0, 0), radio, color='orange', alpha=0.8)
        ax_cached.add_patch(circle_cached)

        inner_circle_cached = None
        if tipo_solido == "Cilindro Hueco" and radio_interno > 0:
            inner_circle_cached = plt.Circle((0, 0), radio_interno, color='white', alpha=1.0)
            ax_cached.add_patch(inner_circle_cached)
        elif tipo_solido == "Cilindro de Pared Delgada":
            if radio * 0.9 > 0: # Ensure valid inner radius for visualization
                inner_circle_cached = plt.Circle((0, 0), radio * 0.9, color='white', alpha=1.0)
                ax_cached.add_patch(inner_circle_cached)

        marca_cached, = ax_cached.plot([0, radio], [0, 0], color='black', linewidth=4)
        cuerda_cached, = ax_cached.plot([], [], color='red', linewidth=3)

        timer_text_mpl = ax_cached.text(0.05, 0.95, '', transform=ax_cached.transAxes,
                                            fontsize=14, color='blue', ha='left', va='top')
        vel_lineal_text_mpl = ax_cached.text(0.05, 0.88, '', transform=ax_cached.transAxes,
                                             fontsize=14, color='green', ha='left', va='top')
        acc_tangencial_text_mpl = ax_cached.text(0.05, 0.81, '', transform=ax_cached.transAxes,
                                                 fontsize=14, color='purple', ha='left', va='top')

        def init_cached():
            cuerda_cached.set_data([], [])
            marca_cached.set_data([0, radio], [0, 0])
            timer_text_mpl.set_text('')
            vel_lineal_text_mpl.set_text('')
            acc_tangencial_text_mpl.set_text('')
            line_omega.set_xdata([0, 0])
            line_v_lineal.set_xdata([0, 0])
            line_energy.set_xdata([0, 0])
            elements = [cuerda_cached, marca_cached, timer_text_mpl, vel_lineal_text_mpl, acc_tangencial_text_mpl,
                        line_omega, line_v_lineal, line_energy]
            if inner_circle_cached:
                elements.append(inner_circle_cached)
            return elements

        def update_cached(frame_num):
            t = frame_num / fps_display_anim
            if t > t_final_anim:
                t = t_final_anim
                
            theta = 0.5 * alpha_anim * t**2
            omega = alpha_anim * t

            v_lineal = omega * radio
            a_tangencial = alpha_anim * radio

            x_origen_cuerda = -radio
            y_origen_cuerda = 0

            long_desenrollada = theta * radio

            x_cuerda = [x_origen_cuerda, x_origen_cuerda - long_desenrollada]
            y_cuerda = [y_origen_cuerda, y_origen_cuerda]

            marca_cached.set_data([0, radio * np.cos(theta)], [0, radio * np.sin(theta)])
            cuerda_cached.set_data(x_cuerda, y_cuerda)

            timer_text_mpl.set_text(f'Tiempo: {t:.2f} s')
            vel_lineal_text_mpl.set_text(f'Vel. Lineal: {v_lineal:.2f} m/s')
            acc_tangencial_text_mpl.set_text(f'Accel. Tang.: {a_tangencial:.2f} m/s²')

            line_omega.set_xdata([t, t])
            line_v_lineal.set_xdata([t, t])
            line_energy.set_xdata([t, t])

            elements = [cuerda_cached, marca_cached, timer_text_mpl, vel_lineal_text_mpl, acc_tangencial_text_mpl,
                        line_omega, line_v_lineal, line_energy]
            if inner_circle_cached:
                elements.append(inner_circle_cached)
            return elements

        ani_cached = FuncAnimation(fig_cached, update_cached, init_func=init_cached,
                                 frames=frames_cached, blit=True, interval=1000/fps_display_anim)

        return fig_cached, ani_cached

    # --- Mostrar la Animación Principal y luego las Gráficas ---
    # Se añade un bloque try-except alrededor de la generación de la animación para capturar errores de Matplotlib
    # si persistieran, aunque la modificación de las etiquetas debería resolver el problema principal.
    try:
        fig_animation, ani = get_animation_with_timer(masa, radio, radio_interno, tipo_solido, alpha, t_final, fps_display,
                                                     line_omega, line_v_lineal, line_energy)
        animation_html = ani.to_jshtml()
        st.components.v1.html(animation_html, height=650)
        
        st.pyplot(fig_plots) # Mostrar las gráficas después de la animación

        plt.close(fig_animation) # Cierra la figura de la animación para liberar memoria
        plt.close(fig_plots)     # Cierra la figura de las gráficas para liberar memoria

    except Exception as e:
        st.error(f"¡Oops! Ocurrió un error al generar la visualización. Esto puede deberse a la configuración de los parámetros o a un problema en el renderizado. Intenta ajustar los valores.")
        st.exception(e) # Muestra el error completo para depuración
