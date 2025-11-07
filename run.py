from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           🤖 WEB CRAWLER - SERUTI                     ║
    ║           Automated Login & Download System           ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    
    Server running on: http://localhost:{Config.PORT}
    
    Press CTRL+C to quit
    """)
    
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
