from shareproject import create_app
from config import ProdConfig
app = create_app(ProdConfig)

if __name__ == "__main__":
    app.run()
