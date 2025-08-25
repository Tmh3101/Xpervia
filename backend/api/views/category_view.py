import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.models import Category
from api.serializers import CategorySerializer
from api.permissions import IsAdmin
from api.middlewares.authentication import SupabaseJWTAuthentication
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

# Category API
class CategoryAdminAPIView(APIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        logger.info("Creating a new category")
        serializer = CategorySerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Category not created: {serializer.errors}')

        serializer.save()
        logger.info("Category created successfully")
        return Response({
            'success': True,
            'message': 'Category created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def put(self, request, id):
        logger.info(f"Updating category with ID: {id}")
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise NotFound('Category does not exist')

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'Category not updated => {serializer.errors}')
        
        serializer.save()
        logger.info("Category updated successfully")
        return Response({
            'success': True,
            'message': 'Category updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

    def delete(self, request, id):
        logger.info(f"Deleting category with ID: {id}")
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise NotFound('Category does not exist')

        category.delete()
        logger.info("Category deleted successfully")
        return Response({
            'success': True,
            'message': f'Category "{category}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    

# Category API to retrieve all categories
class CategoryListAPIView(APIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("Retrieving all categories")
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        logger.info("Categories retrieved successfully")
        return Response({
            'success': True,
            'message': 'All categories have been retrieved successfully',
            'categories': serializer.data
        }, status=status.HTTP_200_OK)
    

# Category API to retrieve a category by ID
class CategoryDetailAPIView(APIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, id):
        logger.info(f"Retrieving category with ID: {id}")
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise NotFound('Category does not exist')

        serializer = CategorySerializer(category)
        logger.info("Category retrieved successfully")
        return Response({
            'success': True,
            'message': 'Category retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)