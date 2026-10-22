"""Keep the unauthenticated personal API inside its local browser boundary."""
from starlette.datastructures import Headers
from starlette.responses import JSONResponse


class LocalBrowserBoundary:
    def __init__(self,app,allowed_origins):
        self.app=app
        self.allowed_origins={origin.rstrip('/') for origin in allowed_origins}

    async def __call__(self,scope,receive,send):
        if scope['type']=='http' and scope['path'].startswith(('/api/','/__forge/')):
            headers=Headers(scope=scope)
            origin=headers.get('origin')
            same_origin=f"{scope.get('scheme','http')}://{headers.get('host','')}"
            # CORS alone only controls response visibility. Even GET endpoints can
            # create a plan or record help, so reject cross-site API requests too.
            if headers.get('sec-fetch-site')=='cross-site' or origin and origin.rstrip('/') not in self.allowed_origins|{same_origin}:
                await JSONResponse({'detail':'Untrusted browser origin'},status_code=403)(scope,receive,send)
                return
        await self.app(scope,receive,send)
