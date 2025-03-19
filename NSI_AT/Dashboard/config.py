class Config:
    # Flask settings
    SECRET_KEY = 'your-secret-key'
    DEBUG = False
    
    # Logging settings
    LOG_LEVEL = 'DEBUG'
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_FILE = 'app.log'

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False