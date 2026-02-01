if st.button("💾 GUARDAR ENTRENAMIENTO"):
    # Creamos la fila con los datos que pusiste en la App
    nueva_fila = pd.DataFrame([{
        "Fecha": datetime.now().strftime("%d/%m/%Y"),
        "Ejercicio": ejercicio,
        "Peso": peso,
        "Reps": reps
    }])

    # Leemos lo que hay ahora en DATOS
    df_historial = conn.read(worksheet="DATOS", ttl=0)
    
    # Juntamos lo viejo con lo nuevo
    df_actualizado = pd.concat([df_historial, nueva_fila], ignore_index=True)
    
    # Lo mandamos de vuelta al Excel
    conn.update(worksheet="DATOS", data=df_actualizado)
    
    st.balloons()
    st.success(f"¡Guardado en el Excel! {ejercicio} - {peso}kg")
