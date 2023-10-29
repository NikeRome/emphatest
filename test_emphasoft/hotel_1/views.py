from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Room, Reservation, CustomUser
from .serializers import RoomSerializer, ReservationSerializer, UserSerializer

# Create your views here.
class RoomListAPIView(generics.ListAPIView):
	"""Представление для просмотра комнат"""
	serializer_class = RoomSerializer

	def get_queryset(self):
		min_price = self.request.query_params.get('min_price')
		max_price = self.request.query_params.get('max_price')
		min_capacity = self.request.query_params.get('min_capacity')

		# Получаем комнаты, которые соответствуют параметрам фильтрации
		queryset = Room.objects.all()

		if min_price:
			queryset = queryset.filter(price_per_night__gte=min_price)
		if max_price:
			queryset = queryset.filter(price_per_night__lte=max_price)
		if min_capacity:
			queryset = queryset.filter(capacity__gte=min_capacity)

		# Получаем комнаты, которые НЕ забронированы в заданный временной интервал
		check_in_date = self.request.query_params.get('check_in_date')
		check_out_date = self.request.query_params.get('check_out_date')

		if check_in_date and check_out_date:
			reserved_rooms = Reservation.objects.filter(
				Q(check_in_date__lt=check_out_date, check_out_date__gt=check_in_date)
			).values_list('room__number', flat=True)

			# Исключаем забронированные комнаты
			queryset = queryset.exclude(number__in=reserved_rooms)

		sort_by = self.request.query_params.get('sort_by')
		if sort_by == 'asc':
			queryset = queryset.order_by('price_per_night')
		elif sort_by == 'desc':
			queryset = queryset.order_by('-price_per_night')

		return queryset

class ReservationCreateAPIView(generics.CreateAPIView):
	"""Представление для бронирования комнат"""
	serializer_class = ReservationSerializer
	permission_classes = [IsAuthenticated]

	def create(self, request, *args, **kwargs):
		room_number = request.data.get('room')
		check_in_date = request.data.get('check_in_date')
		check_out_date = request.data.get('check_out_date')

		room = get_object_or_404(Room, number=room_number)

		# Проверка доступности комнаты с использованием метода is_room_available
		reservation = Reservation(room=room, check_in_date=check_in_date, check_out_date=check_out_date, user=request.user)
		if reservation.is_room_available(check_in_date, check_out_date):
			reservation.save()
			return Response(self.get_serializer(reservation).data, status=status.HTTP_201_CREATED)
		else:
			return Response({"error": "Комната не доступна для бронирования в эти даты."}, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationAPIView(generics.CreateAPIView):
    """Представление для регистрации пользователей"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserLoginAPIView(APIView):
	"""Представление для аутентификации пользователей и генерации токена"""

	def get(self, request):
		"""Отображение страницы при загрузке"""
		return render(request, 'hotel_1/login.html')  # Отображаем страницу логина

	def post(self, request, *args, **kwargs):
		"""Отправка данных для логина"""
		username = request.data.get('username')
		password = request.data.get('password')

		# Попытка аутентифицировать пользователя
		user = authenticate(request, username=username, password=password)

		if user is not None:
			# Если пользователь аутентифицирован, создайте токен и верните его в ответе
			token, created = Token.objects.get_or_create(user=user)
			return Response({'token': token.key}, status=status.HTTP_200_OK)
		else:
			# Если аутентификация не удалась, верните ошибку 401 и покажите страницу логина с сообщением об ошибке
			return render(request, 'hotel_1/login.html', context={'error': 'Invalid credentials'}, 
						status=status.HTTP_401_UNAUTHORIZED)

class ReservationCancelAPIView(generics.DestroyAPIView):
    """Представление для отмены бронирования номера"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """Функция для отмены бронирования"""
        reservation = self.get_object()
        print(reservation.user, self.request.user)
        if reservation.user == self.request.user:
            reservation.delete()
            return Response({"message": "Бронирование успешно отменено"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"error": "Вы не можете отменить это бронирование"},
                            status=status.HTTP_403_FORBIDDEN)

@login_required
def user_reservations(request):
	"""Функия для отображения броней пользователя"""
	reservations = Reservation.objects.filter(user=request.user)
	return render(request, 'hotel_1/user_reservations.html', {'reservations': reservations})

@login_required
def user_profile(request):
	"""Профиль пользователя с указанием броней"""
	if request.method == 'POST':
		reservation_id = request.POST.get('reservation_id')
		print(reservation_id)
		try:
			reservation = Reservation.objects.get(id=reservation_id, user=request.user)
			reservation.delete()
			# Перенаправляем пользователя на страницу профиля после отмены бронирования
			return redirect('user-profile')
		except Reservation.DoesNotExist:
			# Обработка случая, когда бронирование с указанным ID не найдено или не принадлежит текущему пользователю
			print("Бронирование не найдено.")
		except Exception as e:
			print(f"Произошла ошибка: {e}")

	user = request.user
	reservations = Reservation.objects.filter(user=user)
	return render(request, 'hotel_1/user_profile.html', {'reservations': reservations})
