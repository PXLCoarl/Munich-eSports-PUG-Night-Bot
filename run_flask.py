from api import create_app
from utilities import logger
from waitress import serve
import socket, os




def get_local_ip():
    try:
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)
        return local_ip
    except Exception as e:
        logger.error(f"An error occurred while getting local IP: {e}")
        return None



if __name__ == '__main__':
    app = create_app()
    ip = get_local_ip()
    port = int(os.getenv('WEB_INTERFACE'))
    #app.run(debug=True, port=port)
    serve(app, host=ip, port=port)

    