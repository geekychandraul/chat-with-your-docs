import uvicorn

"""
This script runs the server for the application. It also handles the creation or update
of the OpenAPI specification in the development environment.
"""

if __name__ == "__main__":
    """
    Main entry point for the server script. If the environment is set to 'dev',
    it attempts to create or update the OpenAPI specification. Then, it starts
    the Uvicorn server to serve the application.
    """

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
    )
