import authAxios from "./axios-auth";
import type {
  Course,
  CourseWithDetailLessons,
  CreateCourseRequest,
} from "@/lib/types/course";

export const getCoursesApi = async (
  page = 1,
  title?: string,
  categories?: number | number[]
): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: Course[];
}> => {
  const params: any = { page };
  if (title) params.title = title;
  if (categories) params.categories = categories;
  const response = await authAxios.get(`courses/`, {
    params,
  });
  const { count, next, previous, results } = response.data;
  return {
    count,
    next,
    previous,
    results: results.filter((course: Course) => course.is_visible),
  };
};

export const getCoursesByAdminApi = async (
  page: number,
  title?: string,
  is_visible?: boolean
): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: Course[];
}> => {
  const response = await authAxios.get(`courses/`, {
    params: { page, title, is_visible },
  });
  const { count, next, previous, results } = response.data;
  return {
    count,
    next,
    previous,
    results: results.filter((course: Course) => course.is_visible),
  };
};

export const getEnrolledCoursesApi = async (): Promise<Course[]> => {
  const response = await authAxios.get(`courses/student/enrolled/`);
  return response.data.courses;
};

export const getFavoritedCoursesApi = async (): Promise<Course[]> => {
  const response = await authAxios.get(`courses/student/favorited/`);
  return response.data.courses;
};

export const getCourseDetailApi = async (id: number): Promise<Course> => {
  const response = await authAxios.get(`courses/${id}/`);
  return response.data.course;
};

export const getCourseByTeacherApi = async (
  page = 1
): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: Course[];
}> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
  };
  const response = await authAxios.get(`courses/teacher/`, {
    headers,
    params: { page },
  });
  const { count, next, previous, results } = response.data;
  return {
    count,
    next,
    previous,
    results,
  };
};

export const getCourseWithDetailLessonsApi = async (
  courseId: number
): Promise<CourseWithDetailLessons> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
  };
  const response = await authAxios.get(`courses/${courseId}/detail-lessons/`, {
    headers,
  });
  return response.data.course;
};

export const createCourseApi = async (
  data: CreateCourseRequest
): Promise<Course> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
    "Content-Type": "multipart/form-data",
  };

  let formData = new FormData();
  formData.append("thumbnail", data.thumbnail);
  formData.append("title", data.title);
  formData.append("description", data.description);
  formData.append("price", data.price.toString());
  formData.append("start_date", data.start_date || "");
  formData.append("regis_start_date", data.regis_start_date || "");
  formData.append("regis_end_date", data.regis_end_date || "");
  formData.append("max_students", data.max_students.toString());
  formData.append("is_visible", data.is_visible.toString());
  formData.append("categories", JSON.stringify(data.categories));
  formData.append("discount", data.discount?.toString() || "");

  const response = await authAxios.post(`courses/create/`, formData, {
    headers,
  });

  return response.data.course;
};

export const updateCourseApi = async (
  id: number,
  data: CreateCourseRequest
): Promise<Course> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
    "Content-Type": "multipart/form-data",
  };

  let formData = new FormData();

  if (data.thumbnail) {
    formData.append("thumbnail", data.thumbnail);
  }

  formData.append("title", data.title);
  formData.append("description", data.description);
  formData.append("price", data.price.toString());

  if (data.start_date) {
    formData.append("start_date", data.start_date);
  }

  if (data.regis_start_date) {
    formData.append("regis_start_date", data.regis_start_date);
  }

  if (data.regis_end_date) {
    formData.append("regis_end_date", data.regis_end_date);
  }

  formData.append("max_students", data.max_students.toString());
  formData.append("is_visible", data.is_visible.toString());
  formData.append("categories", JSON.stringify(data.categories));

  if (data.discount) {
    formData.append("discount", data.discount.toString());
  }

  const response = await authAxios.put(`courses/${id}/update/`, formData, {
    headers,
  });
  return response.data.course;
};

export const deleteCourseApi = async (id: number): Promise<boolean> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
  };
  const response = await authAxios.delete(`courses/${id}/delete/`, { headers });
  return response.data.success;
};

export const hideCourseApi = async (id: number): Promise<Course> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
  };
  const response = await authAxios.put(`courses/${id}/hide/`, {}, { headers });
  return response.data.course;
};

export const showCourseApi = async (id: number): Promise<Course> => {
  const headers = {
    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
  };
  const response = await authAxios.put(`courses/${id}/show/`, {}, { headers });
  return response.data.course;
};
