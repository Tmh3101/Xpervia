export interface SimpleUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface User extends SimpleUser {
  date_of_birth: string | null;
  role: "student" | "teacher" | "admin";
  is_active: boolean;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserWithPassword extends User {
  password: string;
}
