from .models import *
from rest_framework import serializers


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'start_date', 'start_time', 'is_ready', 'count', 'order_item_cost')
        read_only_fields = ['order_item_cost']


class OrderNestedSerializer(serializers.ModelSerializer):
    order_item = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'table', 'start_date', 'start_time', 'is_active', 'order_item', 'order_cost')
        read_only_fields = ['id', 'order_cost']

    def create(self, validated_data):
        order_items = validated_data.pop('order_item')
        order = Order.objects.create(**validated_data)
        for item in order_items:
            OrderItem.objects.create(order=order, **item)

        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_item')
        order = instance.order_item.all()
        order = list(order)
        instance.table = validated_data.get('table', instance.table)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        for item in order_items_data:
            order_item = order.pop(0)
            order_item.name = item.get('name', order_item.name)
            order_item.product = item.get('product', order_item.product)
            order_item.start_time = item.get('start_time', order_item.start_time)
            order_item.is_ready = item.get('is_ready', order_item.is_ready)
            order_item.count = item.get('count', order_item.count)
            order_item.save()
        return instance


class OrderCookSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'count', 'start_time', 'is_ready', ]
        read_only_fields = ['id', 'order', 'product', 'count', 'start_time']
