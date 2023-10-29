from rest_framework import serializers
from .models import Room, Reservation, CustomUser

class RoomSerializer(serializers.ModelSerializer):
    """Сериализатор для комнат"""
    class Meta:
        model = Room
        fields = ('number', 'price_per_night', 'capacity')

class ReservationSerializer(serializers.ModelSerializer):
    """Сериализатор для бронирований"""
    class Meta:
        """Поля бронирования"""
        model = Reservation
        fields = ('room', 'check_in_date', 'check_out_date')

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""
    # Поле для ввода пароля, не будет отображаться в результатах сериализации
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')


    def create(self, validated_data):
        """Хеширование паролей пользователей"""
        # Извлекаем пароль из входных данных
        password = validated_data.pop('password', None)
        # Создаем пользователя с хешированным паролем
        user = CustomUser(**validated_data)
        user.set_password(password)  # Хешируем пароль
        user.save()
        return user
