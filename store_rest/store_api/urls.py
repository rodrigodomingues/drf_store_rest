from rest_framework.routers import SimpleRouter

from .views import (
    UserRegisterAPIView,
    UserViewSet,
    ProductViewSet,
    ProductsViewSet,
    OrderViewSet,
    OrdersViewSet,
    OrderItemViewSet
)

router = SimpleRouter()
router.register('register', UserRegisterAPIView)
router.register('user', UserViewSet)
router.register('orders', OrdersViewSet)
router.register('order', OrderViewSet)
router.register('order_item', OrderItemViewSet)
router.register('products', ProductsViewSet)
router.register('product', ProductViewSet)

urlpatterns = router.urls
