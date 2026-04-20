from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import CalculationPermission
from .serializers import CalculationRunSerializer, CalculationSerializer
from .services import execute_manual_calculation


class CalculationRunContractAPIView(APIView):
    """Contrato inicial para ejecución manual de cálculos."""

    permission_classes = [IsAuthenticated, CalculationPermission]

    def post(self, request):
        serializer = CalculationRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calculation = execute_manual_calculation(
            entity=serializer.validated_data['entity'],
            period=serializer.validated_data['period'],
            user=request.user,
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description', ''),
        )

        return Response(
            CalculationSerializer(calculation, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
