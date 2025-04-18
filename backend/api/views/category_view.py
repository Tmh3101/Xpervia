import logging
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.models import Category
from api.serializers import CategorySerializer
from api.permissions import IsAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

# Category API to list categories
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # No authentication required for listing

    def list(self, request, *args, **kwargs):
        logger.info("Listing all categories")
        queryset = self.get_queryset()
        serializer = CategorySerializer(queryset, many=True)
        logger.info("Successfully listed all categories")
        return Response({
            'success': True,
            'message': 'All categories have been listed successfully',
            'categories': serializer.data
        }, status=status.HTTP_200_OK)
    

# Category API to create a category
class CategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        logger.info("Creating a new category")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Category not created: {serializer.errors}')

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info("Category created successfully")
        return Response({
            'success': True,
            'message': 'Category created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


# Category API to retrieve a category
class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving category with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Category not found: {str(e)}')

        serializer = self.get_serializer(instance)
        logger.info("Category retrieved successfully")
        return Response({
            'success': True,
            'message': 'Category retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# Category API to update a category
class CategoryUpdateAPIView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating category with ID: {kwargs.get('id')}")
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Category does not exist: {str(e)}')
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            raise ValidationError(f'Category not updated => {serializer.errors}')
        
        self.perform_update(serializer)
        logger.info("Category updated successfully")
        return Response({
            'success': True,
            'message': 'Category updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
# Category API to delete a category
class CategoryDeleteAPIView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting category with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'Category does not exist: {str(e)}')
        
        self.perform_destroy(instance)
        logger.info("Category deleted successfully")
        return Response({
            'success': True,
            'message': f'Category "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

