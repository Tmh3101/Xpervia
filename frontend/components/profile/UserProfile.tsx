"use client"

import Image from "next/image"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { User } from "@/lib/types/user"
import { format } from "date-fns/format"
import userAvatar from "@/public/user-avatar.svg"

interface UserProfileProps {
    user: User
    handleShowEditDialog: () => void
    handleShowChangePasswordDialog: () => void
}

export const UserProfile = ({ user, handleShowEditDialog, handleShowChangePasswordDialog }: UserProfileProps) => {
    return (
        <Card>
            <CardHeader className="flex flex-col items-center">
                <div className="w-32 h-32 rounded-full overflow-hidden mb-4">
                <Image
                    src={userAvatar}
                    alt={`${user.first_name} ${user.last_name}`}
                    width={128}
                    height={128}
                    className="object-cover w-full h-full"
                />
                </div>
                <CardTitle className="text-2xl font-bold text-center">{`${user.first_name} ${user.last_name}`}</CardTitle>
                <p className="text-muted-foreground text-center">
                    <b>Email:</b> {user.email}
                </p>
                <p className="text-muted-foreground text-center">
                    <b>Ngày sinh:</b> {format(new Date(user.date_of_birth), "dd/MM/yyyy")}
                </p>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-center">
                <p className="text-muted-foreground text-sm font-medium mb-1 mr-2">Vai trò:</p>
                <div className="bg-blue-100 border border-blue-500 text-blue-500 text-xs font-bold rounded-full px-2 py-1 inline-block">
                    <p>{user.role === "student" ? "Học viên" : "Giảng viên"}</p>
                </div>
                </div>

                <div> 
                    <Button className="w-full" onClick={handleShowEditDialog}>
                        Chỉnh sửa hồ sơ
                    </Button>
                    <div className="w-full text-center mt-2">
                        <span 
                            className="w-full text-sm text-primary hover:underline cursor-pointer"
                            onClick={handleShowChangePasswordDialog}
                        >
                            Đổi mật khẩu
                        </span>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}