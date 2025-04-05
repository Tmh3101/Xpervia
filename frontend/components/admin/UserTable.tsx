import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Edit, UserX } from "lucide-react"
import type { User } from "@/lib/types/user"
import { formatDate } from "@/lib/utils"

interface UserTableProps {
  users: User[]
  onDisable: (userId: string) => void
  onEdit: (userId: string) => void
}
  
export const UserTable = ({ users, onDisable, onEdit }: UserTableProps) => {
    return (
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
                <TableCell>{formatDate(user.date_joined)}</TableCell>
                <TableCell>
                  <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">Hoạt động</span>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" onClick={() => onEdit(user.id)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDisable(user.id)}
                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                  >
                    <UserX className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    )
  }