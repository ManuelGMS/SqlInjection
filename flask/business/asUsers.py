from integration.queryFactory import QueryFactory

class asUsers:
    
    def getUserPurchasesOf(self, transfer):

        try:        
        
            return QueryFactory().selectPurchasesOfUserDuringTimeInterval().execute(transfer)
            
        except Exception as ex:
            
            print("EX:", ex)

    def getProducts(self):

        try:        
        
            return QueryFactory().getProductsCatalog().execute()
            
        except Exception as ex:
            
            print("EX:", ex)

    def buyProducts(self, transfer, user_id, id):
        
        try:        
        
            QueryFactory().buyProducts().execute(transfer, user_id, id)
            return "La compra se ha realizado con exito."
        except Exception as ex:
            print("EX:", ex)
            return ex
