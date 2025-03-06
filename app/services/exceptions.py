class ServiceProviderUnknownException(Exception):
    def __init__(self, provider_name: str, exception: Exception):
        self.exception = exception
        self.message = f"An untracked error occurred when calling the {provider_name} provider"
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.message}\n{self.exception}"