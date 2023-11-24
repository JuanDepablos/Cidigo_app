from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            database='proyecto',
            user='root',
            password=None,
            port=3307
        )
        return conn
    except Exception as e:
        print(e)
        return None

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['user_id'] = user[0]
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Perfil no encontrado. Verifica tus credenciales.', 'danger')

    return render_template('login.html')

@app.route('/registro', methods=['POST', 'GET'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        username = request.form['username']
        correo = request.form['correo']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
        else:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (nombre, username, correo, password) VALUES (%s, %s, %s, %s)",
                               (nombre, username, correo, password))
                conn.commit()
                cursor.close()
                conn.close()

                flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error en la base de datos. Inténtalo de nuevo.', 'danger')

    return render_template('registro.html')

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                nombre_usuario = user[2]
                return render_template('inicio.html', nombre=nombre_usuario)

    flash('Inicia sesión para ver tu perfil', 'info')
    return redirect(url_for('login'))

@app.route('/info')
def info():
    if 'user_id' in session:
        user_id = session['user_id']

        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM registros_envios WHERE usuario_id = %s", (user_id,))
            envios = cursor.fetchall()
            cursor.close()
            conn.close()

            return render_template('info.html', envios=envios)
    
    flash('Inicia sesión para ver la información de envío', 'info')
    return redirect(url_for('login'))


@app.route('/check_unique_username')
def check_unique_username():
    username = request.args.get('username')
    conn = connect_to_database()
    
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({'unique': count == 0})
    else:
        return jsonify({'unique': False})

@app.route('/check_unique_email')
def check_unique_email():
    email = request.args.get('email')
    conn = connect_to_database()
    
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE correo = %s", (email,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({'unique': count == 0})
    else:
        return jsonify({'unique': False})



@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                if request.method == 'POST':
                    new_nombre_usuario = request.form['nombre_usuario']
                    new_correo = request.form['correo']
                    new_password = request.form['password']

                    if new_correo != user[3]:
                        cursor = conn.cursor(buffered=True)
                        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (new_correo,))
                        existing_user = cursor.fetchone()
                        cursor.close()
                        if existing_user:
                            flash('El correo ya está en uso. Elije otro.', 'danger')
                            return redirect(url_for('edit_profile'))

                    # Validar que el nuevo nombre de usuario no esté en uso
                    if new_nombre_usuario != user[2]:
                        cursor = conn.cursor(buffered=True)
                        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (new_nombre_usuario,))
                        existing_user = cursor.fetchone()
                        cursor.close()
                        if existing_user:
                            flash('El nombre de usuario ya está en uso. Elije otro.', 'danger')
                            return redirect(url_for('edit_profile'))

                    # Actualizar la información del usuario en la base de datos
                    cursor = conn.cursor(buffered=True)
                    cursor.execute("UPDATE usuarios SET username = %s, correo = %s WHERE id = %s", (new_nombre_usuario, new_correo, user_id))
                    conn.commit()
                    cursor.close()

                    # Actualizar la contraseña si se proporcionó una nueva
                    if new_password:
                        cursor = conn.cursor(buffered=True)
                        cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s", (new_password, user_id))
                        conn.commit()
                        cursor.close()

                    flash('Cambios guardados exitosamente', 'success')
                    return redirect(url_for('profile'))

                return render_template('editar_info.html', usuario=user)  # Nombre del archivo HTML

    flash('Inicia sesión para acceder a esta página', 'info')
    return redirect(url_for('login'))

@app.route('/registro_envio', methods=['POST', 'GET'])
def registro_envio():
    if request.method == 'POST':
        if 'user_id' in session:
            usuario_id = session['user_id']
            fecha = request.form['fecha']
            descripcion = request.form['descripcion']

            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO registros_envios (usuario_id, fecha, descripcion) VALUES (%s, %s, %s)",
                               (usuario_id, fecha, descripcion))
                conn.commit()
                cursor.close()
                conn.close()

                flash('Registro de envío exitoso', 'success')
                return redirect(url_for('info'))

    return render_template('registro_envio.html')


if __name__ == '__main__':
    app.run(debug=True)
