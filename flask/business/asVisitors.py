from flask import session
from integration.daoUsuarios import DaoUsuario
from integration.queryFactory import QueryFactory

class asVisitors:

    def createUser(self, transfer):

        message = 'Usuario registrado con exito'

        try:        
        
            DaoUsuario().insert(transfer)
        
        except Exception as ex:
        
            message = ex

        return message

    def checkUser(self, transfer):

        try:        
        
            user = DaoUsuario().read(transfer)
        
            if user is not None:

                session['user'] = user

                transfer = { 'ok': True, 'message': 'Identificación correcta' }

            else:

                transfer = { 'ok': False, 'message': 'Identificación fallida' }

        except Exception as ex:

            transfer = { 'ok': False, 'message': ex }

        return transfer

    def checkAdmin(self, transfer):

        try:

            user = QueryFactory().selectFromUsersWhereMailIsEqualTo().execute(transfer)

            if (user is not None) and (bool(user['administrador']) == True) and (user['contraseña'] == transfer['contraseña']):

                session['user'] = user

                transfer = { 'ok': True, 'message': 'Identificación correcta' }

            else:

                transfer = { 'ok': False, 'message': 'Identificación fallida' }

        except Exception as ex:
            
            transfer = { 'ok': False, 'message': ex }

        return transfer