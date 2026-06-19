class SecurityHeadersMiddleware:
   
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add Permissions-Policy
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        response['Cross-Origin-Resource-Policy'] = 'same-site'
        
        return response

