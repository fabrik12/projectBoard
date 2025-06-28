from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Lo haremos en la fábrica de la aplicación.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)