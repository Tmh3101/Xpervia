"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Edit, UserX, UserCheck } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDate } from "@/lib/utils";
import type { User } from "@/lib/types/user";

interface UserTableProps {
  users: User[];
  onToggleDisable: (userId: string) => void;
  onEdit: (userId: string) => void;
}

export const UserTable = ({
  users,
  onToggleDisable,
  onEdit,
}: UserTableProps) => {
  const [confirmDisable, setConfirmDisable] = useState(false);
  const [userToDisable, setUserToDisable] = useState<User | null>(null);

  const handleToggleDisable = (user: User) => {
    setUserToDisable(user);
    setConfirmDisable(true);
  };

  const handleConfirmDisable = () => {
    if (userToDisable) {
      onToggleDisable(userToDisable.id);
    }
    setConfirmDisable(false);
  };

  const handleCancelDisable = () => {
    setConfirmDisable(false);
  };

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Họ tên</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Ngày tạo</TableHead>
            <TableHead>Trạng thái</TableHead>
            <TableHead className="text-right">Thao tác</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center">
                Không có dữ liệu
              </TableCell>
            </TableRow>
          ) : (
            users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.id}</TableCell>
                <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{formatDate(user.created_at)}</TableCell>
                <TableCell>
                  {user.is_active ? (
                    <span className="px-2 py-1 rounded-full text-xs bg-success/20 text-success">
                      Hoạt động
                    </span>
                  ) : (
                    <span className="px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                      Đã vô hiệu
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(user.id)}
                    className="text-primary hover:text-primary hover:bg-primary/10"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleToggleDisable(user)}
                    className={
                      user.is_active
                        ? "text-red-500 hover:text-red-700 hover:bg-red-100"
                        : "text-success hover:text-success hover:bg-success/10"
                    }
                  >
                    {user.is_active ? (
                      <UserX className="h-4 w-4" />
                    ) : (
                      <UserCheck className="h-4 w-4" />
                    )}
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      <AlertDialog open={confirmDisable} onOpenChange={setConfirmDisable}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Bạn có chắc chắn muốn{" "}
              {userToDisable?.is_active ? "vô hiệu hóa" : "kích hoạt"} tài khoản
              này?
            </AlertDialogTitle>
            <AlertDialogDescription>
              Tài khoản {userToDisable?.email} sẽ{" "}
              {userToDisable?.is_active
                ? "không thể đăng nhập"
                : "được kích hoạt"}
              .
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleCancelDisable}>
              Hủy
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDisable}
              className={
                userToDisable?.is_active
                  ? "bg-red-600 hover:bg-red-700"
                  : "bg-success hover:bg-success/80"
              }
            >
              {userToDisable?.is_active ? "Vô hiệu hóa" : "Kích hoạt"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};
