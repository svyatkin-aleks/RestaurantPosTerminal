from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework.generics import UpdateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, \
    GenericAPIView
from rest_framework import mixins
from .filters import OrderAdminFilter, OrderWaiterFilter, OrderCookFilter
from .serializers import OrderCookSerializer, ProductSerializer, \
    TableSerializer, OrderNestedSerializer
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from rest_framework.response import Response
from .permissions import IsAdmin, IsWaiter, IsCook
from utils.errors import ErrorSerializer
import pdb;


@extend_schema(description='Create table. Allowed only for Admin.')
class TableListCreateView(ListCreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated & IsAdmin]


@extend_schema(description='Admin only')
class TableSingleView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated & IsAdmin]

    @method_decorator(name='get', decorator=extend_schema(
        description='Get table',
        responses={
            200: TableSerializer,
            400: ErrorSerializer,
            401: ErrorSerializer,
        }
    ))
    def get(self, request, *args, **kwargs):
        pdb.set_trace()
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@extend_schema(description='Admin only')
class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated & IsAdmin]


@extend_schema(description='Admin only')
class ProductSingleView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated & IsAdmin]


@extend_schema(description='Admin and Waiter')
class OrderNestedAdminListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderNestedSerializer
    filterset_class = OrderAdminFilter
    permission_classes = [IsAuthenticated & (IsAdmin | IsWaiter)]

    def get(self, request, *args, **kwargs):
        order = Order.objects.all()
        filterset = OrderAdminFilter(request.GET, queryset=order)
        if filterset.is_valid():
            order = filterset.qs
        serializer = OrderNestedSerializer(order, many=True)
        total_income = order.aggregate(Sum('order_cost'))['order_cost__sum']
        return Response({'Total income': total_income if total_income else 0, 'Orders': serializer.data})


@extend_schema(description='Admin and Waiter')
class OrderNestedWaiterListCreateView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderNestedSerializer
    filterset_class = OrderWaiterFilter
    permission_classes = [IsAuthenticated & (IsAdmin | IsWaiter)]


@extend_schema(description='Admin and Cook')
class OrderItemCookerListView(ListAPIView):
    queryset = OrderItem.objects.all().order_by('is_ready')
    serializer_class = OrderCookSerializer
    filterset_class = OrderCookFilter
    permission_classes = [IsAuthenticated & (IsAdmin | IsCook)]


@extend_schema(description='Admin and Cook')
class OrderItemCookerUpdateView(UpdateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderCookSerializer
    permission_classes = [IsAuthenticated & (IsAdmin | IsCook)]
