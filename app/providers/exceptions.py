class GeneralProviderException(Exception):
    def __init__(self, provider_name):
        self.message = f"An issue occurred with the provider {provider_name} while retrieving data"
        super().__init__(self.message)
    
    def __str__(self):
        return self.message