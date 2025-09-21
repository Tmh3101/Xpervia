import logging
from typing import Dict, List
from django.db.models import Count
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from api.pagination import CoursePagination
from api.models import Course
from api.serializers import CourseSerializer, CourseListItemSerializer
from api.middlewares.authentication import SupabaseJWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from api.services.reco_service.cb.similarity import top_k_similar_from_course
from api.services.reco_service.hybrid.service import hybrid_recommend_home
from api.services.reco_service.data_access.courses import fetch_popular_course_ids
from api.utils.course_util import get_progress_map_bulk
from api.services.reco_service.config import ALPHA_HOME, CACHE_TTL

logger = logging.getLogger(__name__)

# Lớp API để lấy danh sách khóa học được đề xuất
class SimilarCourseListAPIView(generics.ListAPIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer

    # Lấy boolean từ query params (exclude_enrolled, exclude_favorited)
    def _parse_bool(self, value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        return value.lower() in {"1", "true", "yes", "y", "t"}

    # Xây tập hợp các course_id cần loại bỏ dựa trên user và base_exclude
    def _get_exclude_ids_for_user(self, user, base_exclude: set[int]) -> set[int]:
        exclude_ids = set(base_exclude)
        exclude_enrolled = self._parse_bool(self.request.query_params.get("exclude_enrolled"))
        exclude_favorited = self._parse_bool(self.request.query_params.get("exclude_favorited"))

        if not getattr(user, "is_authenticated", False):
            return exclude_ids
        
        if user.role == "student":
            exclude_enrolled = True

        if exclude_enrolled:
            enrolled_ids = (
                Course.objects.filter(enrollments__student_id=user.id)
                .values_list("id", flat=True)
                .distinct()
            )
            exclude_ids.update(enrolled_ids)
        if exclude_favorited:
            favorited_ids = (
                Course.objects.filter(favorites__student_id=user.id)
                .values_list("id", flat=True)
                .distinct()
            )
            exclude_ids.update(favorited_ids)

        return exclude_ids


    def list(self, request, *args, **kwargs):
        course_id = kwargs.get("course_id")
        if not Course.objects.filter(id=course_id).exists():
            raise NotFound(f"Course with id={course_id} not found.")
        
        k = request.query_params.get("k", 12)
        base_exclude = {int(course_id)}  # luôn loại chính nó
        exclude_ids = self._get_exclude_ids_for_user(request.user, base_exclude)

        logger.info(f"Fetching content-based similar courses for {course_id}, k={k}")
        similar = top_k_similar_from_course(course_id=int(course_id), k=k, exclude_ids=exclude_ids)
        if not similar:
            return Response({
                "success": True,
                "message": "No similar courses found.",
                "results": []
            })

        # Lấy Course queryset tương ứng & annotate metrics (num_students, num_favorites) để đồng nhất format
        similar_ids = [cid for (cid, _score) in similar]
        qs = (
            Course.objects.filter(id__in=similar_ids)
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True),
            )
        )
        # Đưa về dict để match theo id -> Giữ thứ tự theo score do mô hình trả về
        course_by_id: Dict[int, Course] = {c.id: c for c in qs}
        ordered_courses: List[Course] = [course_by_id[cid] for (cid, _s) in similar if cid in course_by_id]

        results = []
        for course in ordered_courses:
            c_data = CourseSerializer(course).data
            c_data["num_students"] = course.num_students
            c_data["num_favorites"] = course.num_favorites
            results.append(c_data)

        logger.info(f"Returned {len(results)} recommended courses for course_id={course_id}")
        return Response({
            "success": True,
            "message": "Recommended courses fetched successfully.",
            "results": results
        })

# Home Recommendations
# @method_decorator(cache_page(CACHE_TTL), name="dispatch")
class HomeRecoListAPIView(generics.ListAPIView):
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = CourseListItemSerializer
    pagination_class = CoursePagination

    # ------------ helpers ------------
    def _parse_float(self, value: str | None, default: float) -> float:
        if not value:
            return default
        try:
            return float(value)
        except Exception:
            return default

    def list(self, request, *args, **kwargs):
        alpha = self._parse_float(request.query_params.get("alpha"), ALPHA_HOME)
        title = self.request.query_params.get("title")
        categories = self.request.query_params.getlist("categories") or self.request.query_params.get("categories")
        is_visible = self.request.query_params.get("is_visible")

        # Guest → Popular fallback
        if not getattr(request.user, "is_authenticated", False):
            logger.info(f"[reco_home] guest request")
            # Lấy danh sách course phổ biến nhất
            popular = fetch_popular_course_ids(limit=-1)
            payload = [{"course_id": cid, "score": score} for (cid, score) in popular]
        else:
            user_id = str(request.user.id)
            logger.info(f"[reco_home] user={user_id}, alpha={alpha}")
            payload = hybrid_recommend_home(
                user_id=user_id,
                alpha=alpha,
            )

        if not payload:
            return Response({
                "success": True,
                "message": "No recommendations available.",
                "results": []
            })

        # Lấy IDs theo thứ tự đã xếp hạng
        ordered_ids = [p["course_id"] for p in payload]

        # Query Course + annotate để đồng nhất format
        qs = (
            Course.objects.filter(id__in=ordered_ids)
            .select_related("course_content")
            .annotate(
                num_students=Count("enrollments", distinct=True),
                num_favorites=Count("favorites", distinct=True),
                num_lessons=Count("course_content__lessons", distinct=True)
            )
        )

        # Áp filter bổ sung nếu có
        if title:
            qs = qs.filter(course_content__title__icontains=title)
        if categories:
            if isinstance(categories, str):
                categories = [categories]
            qs = qs.filter(course_content__categories__id__in=categories).distinct()
        if is_visible is not None and self.request.user.role == 'admin':
            qs = qs.filter(is_visible=is_visible)

        # Map id -> Course & giữ thứ tự theo payload
        course_by_id: Dict[int, Course] = {c.id: c for c in qs}
        ordered_courses: List[Course] = [course_by_id[cid] for cid in ordered_ids if cid in course_by_id]

        # Pagination thủ công theo list đã sắp xếp
        page = self.paginate_queryset(ordered_courses)

        # Tính progress theo lô (nếu user đăng nhập)
        progress_map = {}
        user = getattr(request, "user", None)
        if page and getattr(user, "is_authenticated", False):
            content_ids = [c.course_content_id for c in page]
            progress_map = get_progress_map_bulk(content_ids, user.id)
        serializer = self.get_serializer(page, many=True, context={"progress_map": progress_map})
        return self.get_paginated_response(serializer.data)
