CL SCR

SET SERVEROUTPUT ON;

/*
DROP USER USUARIO CASCADE;
CREATE USER USUARIO IDENTIFIED BY USUARIO;
GRANT CONNECT TO USUARIO;
GRANT RESOURCE TO USUARIO;
GRANT CREATE TABLE TO USUARIO;
GRANT CREATE TRIGGER TO USUARIO;
GRANT CREATE SEQUENCE TO USUARIO;
GRANT CREATE PROCEDURE TO USUARIO;
GRANT SELECT ANY DICTIONARY TO USUARIO;
*/

DROP SEQUENCE pedidos_seq;
DROP SEQUENCE usuarios_seq;
DROP SEQUENCE productos_seq;

CREATE SEQUENCE pedidos_seq START WITH 1 INCREMENT BY 1 MINVALUE 0 NOMAXVALUE NOCYCLE;
CREATE SEQUENCE usuarios_seq START WITH 0 INCREMENT BY 1 MINVALUE 0 NOMAXVALUE NOCYCLE;
CREATE SEQUENCE productos_seq START WITH 1 INCREMENT BY 1 MINVALUE 0 NOMAXVALUE NOCYCLE;

drop table pedidos cascade constraints;
drop table usuarios cascade constraints;
drop table productos cascade constraints;
drop table linea_pedido cascade constraints;

CREATE TABLE usuarios (
    cod             INT PRIMARY KEY,
    nombre          VARCHAR2(30) NOT NULL CHECK ( length(TRIM(nombre)) > 0 ),
    apellidos       VARCHAR2(40) NOT NULL CHECK ( length(TRIM(apellidos)) > 0 ),
    direccion       VARCHAR2(200) NOT NULL CHECK ( length(TRIM(direccion)) > 0 ),
    correo          VARCHAR2(200) NOT NULL UNIQUE CHECK ( length(TRIM(correo)) > 0 ),
    contraseña      VARCHAR2(200) NOT NULL CHECK ( length(contraseña) >= 8 ),
    saldo           FLOAT DEFAULT 0 NOT NULL CHECK ( saldo >= 0 ),
    administrador   NUMBER(1,0) DEFAULT 0 NOT NULL CHECK (administrador BETWEEN 0 and 1)
);

CREATE TABLE pedidos (
    cod             INT PRIMARY KEY,
    cod_usuario     INT REFERENCES usuarios ON DELETE CASCADE,
    coste           FLOAT NOT NULL CHECK ( coste >= 0 ),
    fecha_realizado DATE DEFAULT sysdate NOT NULL,
    fecha_enviado   DATE DEFAULT NULL,
    fecha_entrega   DATE DEFAULT NULL,
    fecha_recibido  DATE DEFAULT NULL
);

CREATE TABLE productos (
    cod         INT PRIMARY KEY,
    nombre      VARCHAR2(20) NOT NULL CHECK ( length(TRIM(nombre)) > 0 ),
    precio      FLOAT NOT NULL CHECK ( precio >= 0 ),
    unidades    INT NOT NULL CHECK ( unidades >= 0 ),
    descripcion VARCHAR2(60) NOT NULL CHECK ( length(TRIM(descripcion)) > 0 )
);

CREATE TABLE linea_pedido (
    cod_pedido   INT REFERENCES pedidos ON DELETE CASCADE,
    cod_producto INT REFERENCES productos,
    cantidad     INT NOT NULL CHECK ( cantidad > 0 ),
    PRIMARY KEY ( cod_pedido, cod_producto )
);

CREATE OR REPLACE TRIGGER ped_tg 
BEFORE INSERT ON pedidos 
FOR EACH ROW
BEGIN
  SELECT pedidos_seq.NEXTVAL
  INTO   :new.cod
  FROM   dual;
END;
/

CREATE OR REPLACE TRIGGER prod_tg 
BEFORE INSERT ON productos 
FOR EACH ROW
BEGIN
  SELECT productos_seq.NEXTVAL
  INTO   :new.cod
  FROM   dual;
END;
/

CREATE OR REPLACE PROCEDURE SORTEO IS

  TYPE CURSOR_REFERENCE IS REF CURSOR;
    
  MY_CURSOR CURSOR_REFERENCE;
    
  TYPE MY_RECORD_TYPE IS RECORD (
    COD_USUARIO PEDIDOS.COD_USUARIO%TYPE
  );
    
  MY_RECORD MY_RECORD_TYPE;

  MY_QUERY VARCHAR2(200) := '';

  RND1 INT := FLOOR(DBMS_RANDOM.VALUE(0, 10));
  RND2 INT := FLOOR(DBMS_RANDOM.VALUE(0, 10));
  RND3 INT := FLOOR(DBMS_RANDOM.VALUE(0, 10));
    
BEGIN

  MY_QUERY := MY_QUERY || 'SELECT DISTINCT(P.COD_USUARIO) ';
  MY_QUERY := MY_QUERY || 'FROM USUARIOS U, PEDIDOS P ';
  MY_QUERY := MY_QUERY || 'WHERE (U.COD = P.COD_USUARIO) AND ';
  MY_QUERY := MY_QUERY || 'FECHA_REALIZADO >= ''' || SYSDATE || ''' AND ';
  MY_QUERY := MY_QUERY || 'MOD(ASCII(SUBSTR(U.NOMBRE, 1, 1)), 10) ';
  MY_QUERY := MY_QUERY || 'IN('||RND1||','||RND2||','||RND3||')';
    
	OPEN MY_CURSOR FOR MY_QUERY;

	FETCH MY_CURSOR INTO MY_RECORD;

	WHILE(MY_CURSOR%FOUND)
	LOOP
    
    UPDATE USUARIOS SET SALDO = SALDO + 1000 WHERE COD = MY_RECORD.COD_USUARIO;
        
		FETCH MY_CURSOR INTO MY_RECORD;    

	END LOOP;

	CLOSE MY_CURSOR;
    
END;
/

insert into usuarios(cod, nombre, apellidos, direccion, correo, contraseña, saldo, administrador) values(usuarios_seq.NEXTVAL, 'Pepe', 'Perez Lopez', 'Calle de las meninas', 'pepeperez@gmail.com', '12345678', 1000, 1);
insert into usuarios(cod, nombre, apellidos, direccion, correo, contraseña, saldo, administrador) values(usuarios_seq.NEXTVAL, 'Sofía', 'Esposito', 'Calle de la tina', 'sofesp@gmail.com', '14235867', 1000, 1);
insert into usuarios(cod, nombre, apellidos, direccion, correo, contraseña, saldo, administrador) values(usuarios_seq.NEXTVAL, 'Luis', 'Garmendia Morales', 'Calle santa clara', 'luisgm@gmail.com', '09876543', 2000, 0);
insert into usuarios(cod, nombre, apellidos, direccion, correo, contraseña, saldo, administrador) values(usuarios_seq.NEXTVAL, 'Elena', 'San Clemente Sanchez', 'Calle del bastión', 'elesan@gmail.com', '10293847', 2000, 0);

insert into pedidos(cod_usuario, coste, fecha_realizado, fecha_enviado, fecha_entrega, fecha_recibido) values(1, 320, sysdate, sysdate + 1, sysdate + 3, sysdate + 3);
insert into pedidos(cod_usuario, coste, fecha_realizado, fecha_enviado, fecha_entrega, fecha_recibido) values(1, 120, sysdate - 1, sysdate + 3, sysdate + 6, sysdate + 8);
insert into pedidos(cod_usuario, coste, fecha_realizado, fecha_enviado, fecha_entrega, fecha_recibido) values(2, 100, sysdate - 40, sysdate + 2, sysdate + 4, sysdate + 4);
insert into pedidos(cod_usuario, coste, fecha_realizado, fecha_enviado, fecha_entrega, fecha_recibido) values(3, 30, sysdate - 10, sysdate + 3, sysdate + 7, sysdate + 7);

insert into productos(nombre, precio, unidades, descripcion) values('sable laser', 200, 20, 'sable de color verde');
insert into productos(nombre, precio, unidades, descripcion) values('super soaker', 120, 20, 'pistola de agua de alta presion');
insert into productos(nombre, precio, unidades, descripcion) values('jungle speed', 50, 20, 'juego entre amigos');
insert into productos(nombre, precio, unidades, descripcion) values('fundacion', 10, 20, 'libro de isaac asimov');
insert into productos(nombre, precio, unidades, descripcion) values('fundacion e imperio', 10, 20, 'libro de isaac asimov');
insert into productos(nombre, precio, unidades, descripcion) values('segunda fundacion', 10, 20, 'libro de isaac asimov');

insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(1, 1, 1);
insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(1, 2, 1);
insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(2, 2, 1);
insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(3, 3, 2);
insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(4, 4, 1);
insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(4, 5, 1);
insert into linea_pedido(cod_pedido, cod_producto, cantidad) values(4, 6, 1);

COMMIT;