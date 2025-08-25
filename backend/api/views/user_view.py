# import logging
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from api.middlewares.authentication import SupabaseJWTAuthentication
# from api.models import User
# from api.services.supabase.client import supabase
# from api.permissions import IsAdmin  
    
# logger = logging.getLogger(__name__)

# class UserAdminView(APIView):
#     authentication_classes = [SupabaseJWTAuthentication]
#     permission_classes = [IsAuthenticated, IsAdmin]

#     def get(self, request):
#         logger.info(f"Retrieving user list")
#         users = User.objects.all()

#         logger.info("User list retrieved successfully")
#         return Response({
#             "success": True,
#             "message": "User list retrieved successfully",
#             "users": [user.to_dict() for user in users]
#         }, status=status.HTTP_200_OK)

#     def post(self, request):
#         logger.info(f"Creating user with email: {request.data.get('email')}")
#         email = request.data.get("email")
#         password = request.data.get("password")
#         first_name = request.data.get("first_name")
#         last_name = request.data.get("last_name")
#         date_of_birth = request.data.get("date_of_birth")
#         role = request.data.get("role")

#         # Create user on supabase
#         data = {
#             "email": email,
#             "password": password,
#             "user_metadata": {
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "role": role
#             }
#         }

#         user = create_user(email, password, user_metadata)  
#         if user:
#             logger.info(f"User created successfully: {user}")
#             return Response({
#                 "success": True,
#                 "message": "User created successfully",
#                 "user": user.to_dict()
#             }, status=status.HTTP_201_CREATED)
        
#         logger.error(f"Failed to create user: {email}")
#         return Response({
#             "success": False,
#             "message": "Failed to create user"
#         }, status=status.HTTP_400_BAD_REQUEST)
    

#     def put(self, request, user_id):
#         logger.info(f"Updating user with ID: {user_id}")

#         email = request.data.get("email")
#         password = request.data.get("password") 
#         user_metadata = request.data.get("user_metadata")

#         user = update_user_info_by_id(user_id, email, password, user_metadata)  
#         if user:
#             logger.info(f"User updated successfully: {user}")
#             return Response({
#                 "success": True,
#                 "message": "User updated successfully",
#                 "user": user.to_dict()
#             }, status=status.HTTP_200_OK)
        
#         logger.error(f"Failed to update user: {user_id}")
#         return Response({
#             "success": False,
#             "message": "Failed to update user"
#         }, status=status.HTTP_400_BAD_REQUEST)
        

#     def delete(self, request, user_id):
#         logger.info(f"Deleting user with ID: {user_id}")
#         try:
#             delete_user(user_id)
#         except Exception as e:
#             logger.error(f"Error deleting user: {e}")
#             return Response({
#                 "success": False,
#                 "message": "Failed to delete user"
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         logger.info(f"User deleted successfully: {user_id}")
#         return Response({
#             "success": True,
#             "message": "User deleted"
#         }, status=status.HTTP_200_OK)
    

# class UserDetailView(APIView):
#     def get(self, request, user_id):
#         user = get_user_info_by_id(user_id)
#         if user:
#             logger.info(f"Retrieved user info: {user}")
#             return Response({
#                 "success": True,
#                 "message": "User info retrieved successfully",
#                 "user": user.to_dict()
#             }, status=status.HTTP_200_OK)
        
#         logger.error(f"Failed to retrieve user info for user_id: {user_id}")
#         return Response({
#             "success": False,
#             "message": "Failed to retrieve user info",
#         }, status=404)
