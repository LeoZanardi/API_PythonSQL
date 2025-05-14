from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host="db",
        port=3306,
        user="root",
        password="root",
        database="DBuser"
    )

@app.route('/')
def index():
    return jsonify({"message": "API Flask rodando dentro do container!"})

@app.route('/users',methods=['GET'])
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, phone, data, hora FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()

    users_list = []
    for user in users:
        users_list.append({
            "id": user[0],
            "name": user[1],
            "phone": user[2],
            "data": str(user[3]),
            "hora": str(user[4])
        })

    return jsonify({"users": users_list})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, phone, data, hora FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        return jsonify({
            "id": user[0],
            "name": user[1],
            "phone": user[2],
            "data": str(user[3]),
            "hora": str(user[4])
        })
    else:
        return jsonify({"message": "Usuário não encontrado."}), 404

@app.route('/post/users', methods=['POST'])
def save_user():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    date_str = data.get('data')
    hour_str = data.get('hora')

    if not all([name, phone, date_str, hour_str]):
        return jsonify({"error": "Por favor, forneça todos os detalhes do usuário."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO users (name, phone, data, hora)
    VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (name, phone, date_str, hour_str))
        connection.commit()
        user_id = cursor.lastrowid

        cursor.execute("SELECT id, name, phone, data, hora FROM users WHERE id = %s", (user_id,))
        new_user = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "user": {
                "id": new_user[0],
                "name": new_user[1],
                "phone": new_user[2],
                "data": str(new_user[3]),
                "hora": str(new_user[4])
            }
        }), 201

    except pymysql.Error as e:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({"error": f"Erro ao salvar o usuário: {e}"}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    date_str = data.get('data')
    hour_str = data.get('hora')

    if not any([name, phone, date_str, hour_str]):
        return jsonify({"error": "Por favor, forneça ao menos um detalhe para atualizar."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    query_parts = []
    values = []

    if name:
        query_parts.append("name = %s")
        values.append(name)
    if phone:
        query_parts.append("phone = %s")
        values.append(phone)
    if date_str:
        query_parts.append("data = %s")
        values.append(date_str)
    if hour_str:
        query_parts.append("hora = %s")
        values.append(hour_str)

    query = f"UPDATE users SET {', '.join(query_parts)} WHERE id = %s"
    values.append(user_id)

    try:
        cursor.execute(query, tuple(values))
        connection.commit()

        if cursor.rowcount > 0:
            cursor.execute("SELECT id, name, phone, data, hora FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            cursor.close()
            connection.close()
            return jsonify({"message": "Usuário atualizado com sucesso!", "user": {
                "id": updated_user[0],
                "name": updated_user[1],
                "phone": updated_user[2],
                "data": str(updated_user[3]),
                "hora": str(updated_user[4])
            }}), 200
        else:
            cursor.close()
            connection.close()
            return jsonify({"message": "Usuário não encontrado."}), 404

    except pymysql.Error as e:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({"error": f"Erro ao atualizar o usuário: {e}"}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    connection.commit()

    if cursor.rowcount > 0:
        response = jsonify({"message": "Usuário deletado com sucesso!"}), 200
    else:
        response = jsonify({"message": "Este usuário não foi encontrado."}), 404

    cursor.close()
    connection.close()
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)