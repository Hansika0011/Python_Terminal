from app.main import app
import os

if __name__ == '__main__':
    # Set environment variables if needed
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
