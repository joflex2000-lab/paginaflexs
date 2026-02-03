from .cart import Carrito


def cart_context(request):
    """
    Context processor para tener el carrito disponible en todos los templates.
    """
    return {
        'carrito': Carrito(request)
    }
