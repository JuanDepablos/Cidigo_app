from flask import Flask, render_template, request, redirect, url_for, flash, session
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

# Ruta para procesar el inicio de sesión (POST)
@app.route('/', methods=['POST'])
def login_post():
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

    return redirect(url_for('login'))

# Ruta para procesar el registro de usuario (POST)
@app.route('/registro', methods=['POST'])
def registro_post():
    nombre = request.form['nombre']
    username = request.form['username']
    correo = request.form['correo']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    print(request.form)  # Imprime los datos del formulario para depuración
    nombre = request.form['nombre']
    
    if password != confirm_password:
        flash('Las contraseñas no coinciden', 'danger')
        return redirect(url_for('registro'))

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

    return redirect(url_for('registro'))

# Ruta para la página de inicio (GET)
@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

# Ruta para la página de registro (GET)
@app.route('/registro', methods=['GET'])
def registro():
    return render_template('registro.html')

# Ruta para el perfil del usuario (GET)
@app.route('/profile', methods=['GET'])
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
                return render_template('inicio.html', user=user)
    
    flash('Inicia sesión para ver tu perfil', 'info')
    return redirect(url_for('login'))
@app.route('/info', methods=['GET'])
def info():
    # Lógica para mostrar la información de envío
    return render_template('info.html')


if __name__ == '__main__':
    app.run(debug=True)
