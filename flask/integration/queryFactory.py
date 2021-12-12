import cx_Oracle
from flask import current_app as app

# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************

# Simulamos una clase interfaz
class Query:
    def execute(self, params):
            pass

# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************

# Creamos una query que implementa el interfaz
class SelectFromUsersWhereMailIsEqualTo(Query):
    
    def execute(self, transfer):

        user = None

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:

                '''
                Brechas de seguridad: 

                Registrarse con un UNION ATTACK, campo nombre:  ' UNION SELECT NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL FROM DUAL -- 
                                                                ' UNION SELECT NULL, '11112222', '11112222', '11112222', '11112222', '11112222', NULL, NULL FROM DUAL --
                                                                ' UNION SELECT 1, '11112222', '11112222', '11112222', '11112222', '11112222', 1, 1 FROM DUAL --
                '''
                cursor.execute("select * from usuarios where correo = '" + transfer['correo'] + "'")
                
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

# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************

# Creamos una query que implementa el interfaz
class SelectPurchasesOfUserDuringTimeInterval(Query):
    
    def execute(self, transfer):

        purchases = dict()

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:

                '''
                Brechas de seguridad:
                
                UNION ATTACK a través del hidden input uid para la extracción de información:       1 UNION SELECT NULL, NULL, NULL, NULL, NULL, NULL, NULL FROM DUAL --
                                                                                                    1 UNION SELECT NULL, NULL, 'A', 'B', NULL, NULL, NULL FROM DUAL --
                                                                                                    1 UNION SELECT 1, 2, 'A', 'B', 3, 4, 5 FROM DUAL --
                
                Ataque mediante Serialized SQL-Injection para obtener información concentrada:      (SELECT XMLAGG(XMLELEMENT(&quot;USUARIO&quot;, XMLFOREST(NOMBRE, SALDO, CONTRASEÑA))).getStringVal() FROM USUARIOS)
                                                                                                    (SELECT XMLAGG(XMLELEMENT(&quot;OBJECT&quot;, XMLFOREST(OBJECT_NAME))).getStringVal() FROM USER_PROCEDURES WHERE OBJECT_TYPE = 'PROCEDURE')
                                                                                                    (SELECT XMLAGG(XMLELEMENT(&quot;LINE&quot;, XMLFOREST(TEXT))).getStringVal() FROM ALL_SOURCE WHERE NAME = 'SORTEO' ORDER BY LINE)
                                                                                                    
                                                                                                    (SELECT VALUE FROM NLS_SESSION_PARAMETERS WHERE PARAMETER = 'NLS_DATE_FORMAT')
                '''
                for row in cursor.execute(
                    "select pe.cod, pe.coste, pr.nombre, pr.descripcion, pr.precio, lp.cantidad, (pr.precio * lp.cantidad) " +
                    "from pedidos pe, productos pr, linea_pedido lp " +
                    "where (pr.cod = lp.cod_producto) and (pe.cod = lp.cod_pedido) and " +
                    "(fecha_realizado >= to_date('"+ transfer['from'] +" 00:00:00','YYYY-MM-DD hh24:mi:ss')) and " + 
                    "(fecha_realizado <= to_date('"+ transfer['to'] +" 23:59:59','YYYY-MM-DD hh24:mi:ss')) and " +
                    "pe.cod_usuario = "+ transfer['uid'] +" " +
                    "order by pe.cod, pr.nombre"
                ):

                    if row[0] not in purchases:

                        purchases[row[0]] = list()

                    purchases[row[0]].append(row) 
        
        return purchases


class SelectAllProducts(Query):

    def execute(self):

        products = list()

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:

                for row in cursor.execute("select * from productos"):
                    products.append(row) 
        
        return products


class buyProducts(Query):

    def execute(self,transfer,id_user, id):

        # Solicitamos una conexion a la bbdd
        with cx_Oracle.connect(user=app.config["USER"], password=app.config["PASSWORD"], dsn=app.config["DATABASE_URI"]) as connection:

            # Abre un cursor para manipular la bbdd
            with connection.cursor() as cursor:
                '''
                Brechas de seguridad:
                Hacer compras a otro usuario mediante la url:  http://127.0.0.1:5000/users/buyProducts/<id_usuario>/<id_articulo>?quantity=<cantidad> 
                '''
                cursor.execute(
                    "DECLARE "
                    "   AUX_precio FLOAT; "
                    "BEGIN " + 
                    "   select productos.precio into AUX_precio from productos where productos.cod ="+ id +";" +
                    "   insert into PEDIDOS(COD_USUARIO, COSTE, FECHA_REALIZADO) values(" + id_user + ", AUX_precio * " + transfer['quantity'] + ", sysdate);" +
                    "END;")
                connection.commit()
                cursor.execute(
                    "DECLARE "
                    "   AUX_codped FLOAT; "
                    "BEGIN " + 
                    "   select max(pedidos.cod) into AUX_codped from pedidos; "+
                    "   insert into LINEA_PEDIDO(COD_PEDIDO,COD_PRODUCTO, CANTIDAD) values(AUX_codped," + id + ", " + transfer['quantity'] + ");"+
                    "END;")
                connection.commit()

# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************

# Factoria que genera nuestras querys
class QueryFactory:
	
    def selectPurchasesOfUserDuringTimeInterval(self):
        return SelectPurchasesOfUserDuringTimeInterval()

    def selectFromUsersWhereMailIsEqualTo(self):
        return SelectFromUsersWhereMailIsEqualTo()

    def getProductsCatalog(self):
        return SelectAllProducts()

    def buyProducts(self):
        return buyProducts()

# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************
# ********************************************************************************************************************************************************